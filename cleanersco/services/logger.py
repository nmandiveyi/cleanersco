import logging
import structlog
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send


class Logger:
    @staticmethod
    def setup_logger():
        timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
        pre_chain = [
            # Add the log level and a timestamp to the event_dict if the log entry
            # is not from structlog.
            structlog.stdlib.add_log_level,
            # Add extra attributes of LogRecord objects to the event dictionary
            # so that values passed in the extra parameter of log methods pass
            # through to log output.
            structlog.stdlib.ExtraAdder(),
            timestamper,
        ]

        def extract_from_record(_, __, event_dict):
            """
            Extract thread and process names and add them to the event dict.
            """
            record = event_dict["_record"]
            event_dict["thread_name"] = record.threadName
            event_dict["process_name"] = record.processName
            return event_dict

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "plain": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.processors.JSONRenderer(),
                        ],
                        "foreign_pre_chain": pre_chain,
                    },
                    "colored": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            extract_from_record,
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.dev.ConsoleRenderer(colors=True),
                        ],
                        "foreign_pre_chain": pre_chain,
                    },
                },
                "handlers": {
                    "default": {
                        "level": "DEBUG",
                        "class": "logging.StreamHandler",
                        "formatter": "colored",
                    },
                    "file": {
                        "level": "DEBUG",
                        "class": "logging.handlers.WatchedFileHandler",
                        "filename": "app.log",  # Change the log file name as needed
                        "formatter": "plain",
                    },
                },
                "loggers": {
                    # Override Uvicorn loggers to suppress unnecessary info logs
                    "uvicorn.error": {
                        "level": "ERROR",
                        "handlers": ["default", "file"],
                        "propagate": False,
                    },
                    "uvicorn.access": {
                        "level": "ERROR",
                        "handlers": ["default", "file"],
                        "propagate": False,
                    },
                    "uvicorn": {
                        "handlers": ["default", "file"],
                        "level": "INFO",  # Logs above warning, suppresses startup info
                        "propagate": False,
                    },
                    "": {
                        "handlers": ["default", "file"],
                        "level": "DEBUG",
                        "propagate": True,
                    },
                },
            }
        )
        structlog.configure(
            processors=[
                # If log level is too low, abort pipeline and throw away log entry.
                structlog.stdlib.filter_by_level,
                # Add the name of the logger to event dict.
                structlog.stdlib.add_logger_name,
                # Add log level to event dict.
                structlog.stdlib.add_log_level,
                # Perform %-style formatting.
                structlog.stdlib.PositionalArgumentsFormatter(),
                # Add a timestamp in ISO 8601 format.
                structlog.processors.TimeStamper(fmt="iso"),
                # If the "stack_info" key in the event dict is true, remove it and
                # render the current stack trace in the "stack" key.
                structlog.processors.StackInfoRenderer(),
                # If the "exc_info" key in the event dict is either true or a
                # sys.exc_info() tuple, remove "exc_info" and render the exception
                # with traceback into the "exception" key.
                structlog.processors.format_exc_info,
                # If some value is in bytes, decode it to a Unicode str.
                structlog.processors.UnicodeDecoder(),
                # Add callsite parameters.
                structlog.processors.CallsiteParameterAdder(
                    {
                        structlog.processors.CallsiteParameter.PATHNAME,
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.MODULE,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                        structlog.processors.CallsiteParameter.THREAD,
                        structlog.processors.CallsiteParameter.THREAD_NAME,
                    }
                ),
                # Render the final event dict as JSON.
                structlog.processors.JSONRenderer(),
            ],
            # `wrapper_class` is the bound logger that you get back from
            # get_logger(). This one imitates the API of `logging.Logger`.
            wrapper_class=structlog.stdlib.BoundLogger,
            # `logger_factory` is used to create wrapped loggers that are used for
            # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
            # string) from the final processor (`JSONRenderer`) will be passed to
            # the method of the same name as that you've called on the bound logger.
            logger_factory=structlog.stdlib.LoggerFactory(),
            # Effectively freeze configuration after creating the first bound
            # logger.
            cache_logger_on_first_use=True,
            context_class=dict,
        )
        return structlog.get_logger("structlog")


logger = Logger.setup_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _recieve():
            handled_request = await receive()
            log_params = {
                "event": "Incoming HTTP Request",
                "path": scope.get("path", None),
                "payload": handled_request.get("body", None).decode(),
                "method": scope.get("method", None),
                "asgi": scope.get("asgi", None),
                "request_id": str(uuid4()),
            }
            logger.info(**log_params)
            return handled_request

        await self.app(scope, _recieve, send)
