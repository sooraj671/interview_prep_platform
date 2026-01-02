from fastapi import FastAPI
import os

app = FastAPI(title="Interview Prep Platform", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Interview Prep Platform API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Add all possible health check endpoints Railway might use
@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/ping")
async def ping():
    return {"pong": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, server_header=False)
