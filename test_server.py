from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test server working"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
