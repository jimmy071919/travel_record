from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.staticfiles import StaticFiles
from .routes import travel_records
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = FastAPI(title="Travel Record API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設置具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件服務
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 包含路由
app.include_router(travel_records.router, tags=["travel_records"])

@app.on_event("startup")
async def startup_db_client():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    app.mongodb_client = AsyncIOMotorClient(mongodb_url)
    app.mongodb = app.mongodb_client.travel_records

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "Welcome to Travel Record API"}
