from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)

from fastapi import FastAPI


swagger_js_url = "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"
swagger_css_url = "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
redoc_js_url = "https://unpkg.com/redoc@next/bundles/redoc.standalone.js"

api_prefix = "/api/v1"


def attach_api_doc_routes(app: FastAPI):
    @app.get(f"{api_prefix}/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - API Docs",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get(f"{api_prefix}/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url=redoc_js_url,
        )
