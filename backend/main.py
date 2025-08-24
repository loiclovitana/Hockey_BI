import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start the Hockey BI FastAPI backend")
    parser.add_argument("--prod", action="store_true", help="Run in production mode")
    args = parser.parse_args()

    if args.prod:
        # Production mode
        uvicorn.run("src.hmtracker.api.server:app", host="0.0.0.0", workers=4)
    else:
        # Development mode with auto-reload
        uvicorn.run(
            "src.hmtracker.api.server:app",
            host="127.0.0.1",
            reload=True,
            reload_dirs=["src"],
        )


if __name__ == "__main__":
    main()
