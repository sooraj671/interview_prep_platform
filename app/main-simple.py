from fastapi import FastAPI
import os

app = FastAPI(title="Interview Prep Platform", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Interview Prep Platform API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
