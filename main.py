import uvicorn


def main():
    print("Starting Email Classifier FastAPI service...")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
