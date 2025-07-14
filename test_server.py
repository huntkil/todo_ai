from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test Server")

class TestInput(BaseModel):
    text: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "server": "Test Server"}

@app.post("/test")
async def test_endpoint(input_data: TestInput):
    return {
        "message": "Test successful",
        "input": input_data.text,
        "processed": True
    } 