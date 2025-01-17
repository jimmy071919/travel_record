from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from typing import List
import aiofiles
import os
from datetime import datetime
from PIL import Image
from ..models.travel_record import TravelRecordCreate, TravelRecordInDB

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/records/", response_model=TravelRecordInDB)
async def create_record(request: Request, record: TravelRecordCreate):
    record_dict = record.dict()
    record_in_db = TravelRecordInDB(**record_dict)
    
    new_record = await request.app.mongodb.records.insert_one(
        record_in_db.dict()
    )
    
    created_record = await request.app.mongodb.records.find_one(
        {"_id": new_record.inserted_id}
    )
    
    return created_record

@router.post("/records/upload-photo/")
async def upload_photo(file: UploadFile = File(...)):
    try:
        # 驗證文件是否為圖片
        content_type = file.content_type
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{timestamp}{file_extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        async with aiofiles.open(filepath, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # 驗證並處理圖片
        with Image.open(filepath) as img:
            # 可以在這裡添加圖片處理邏輯，例如壓縮、調整大小等
            img.verify()
        
        # 返回文件URL
        return {"photo_url": f"/uploads/{filename}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records/", response_model=List[TravelRecordInDB])
async def get_records(request: Request):
    records = []
    async for record in request.app.mongodb.records.find():
        records.append(record)
    return records

@router.put("/records/{record_id}", response_model=TravelRecordInDB)
async def update_record(request: Request, record_id: str, record_update: TravelRecordCreate):
    update_result = await request.app.mongodb.records.update_one(
        {"id": record_id},
        {"$set": record_update.dict(exclude_unset=True)}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    updated_record = await request.app.mongodb.records.find_one({"id": record_id})
    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return updated_record

@router.delete("/records/{record_id}")
async def delete_record(request: Request, record_id: str):
    delete_result = await request.app.mongodb.records.delete_one({"id": record_id})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record deleted successfully"}
