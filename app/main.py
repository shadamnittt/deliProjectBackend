import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api.router:app", host="localhost", port=8000, reload=True, log_level="info")
