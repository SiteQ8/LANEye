"""LANEye - Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LANEye", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LANEye Network Scanner", "version": "1.0.0"}

@app.get("/api/hosts")
async def get_hosts():
    return {"hosts": [], "count": 0}

@app.get("/api/stats")
async def get_stats():
    return {"total_hosts": 0, "online_hosts": 0, "offline_hosts": 0}
