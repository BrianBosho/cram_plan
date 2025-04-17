from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"message": "API is working!"}

if __name__ == "__main__":
    print("Starting simple test API...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 