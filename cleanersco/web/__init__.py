import uvicorn


def main():
    uvicorn.run(
        "web.app:get_application",
        host="0.0.0.0",
        port=8765,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    main()
