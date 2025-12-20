from fastapi import FastAPI

app = FastAPI(title="测试API")

@app.get("/")
async def root():
    return {"message": "测试成功"}

@app.get("/health")
async def health():
    return {"status": "ok"}