from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from typing import List
import os
import shutil
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from ..models.travel_record import TravelRecordBase, TravelRecordCreate, TravelRecordInDB, TravelRecordResponse

router = APIRouter()

# 確保上傳目錄存在
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload-photo/")
async def upload_photo(request: Request, file: UploadFile = File(...)):
    try:
        # 驗證文件類型
        content_type = file.content_type
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只允許上傳圖片文件")
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
            raise HTTPException(status_code=400, detail="只支持 JPG、PNG 和 GIF 格式")
            
        unique_filename = f"{uuid4()}{file_extension}"
        relative_path = f"photos/{unique_filename}"  # 相對路徑
        absolute_path = UPLOAD_DIR / relative_path  # 絕對路徑
        
        # 確保目標目錄存在
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with absolute_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 構建訪問 URL
        base_url = str(request.base_url).rstrip('/')
        
        return {
            "photo_path": relative_path,  # 返回相對路徑用於存儲
            "photo_url": f"{base_url}/uploads/{relative_path}"  # 返回完整 URL 用於訪問
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/uploads/photos/{filename}")
async def get_photo(filename: str):
    file_path = UPLOAD_DIR / "photos" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="圖片不存在")
    return FileResponse(str(file_path))

# 記錄相關的路由
@router.post("/records/", response_model=TravelRecordResponse)
async def create_record(request: Request, record: TravelRecordCreate):
    try:
        new_record = TravelRecordInDB(**record.dict())
        
        # 如果有照片路徑，添加完整的訪問 URL
        if new_record.photo_path:
            base_url = str(request.base_url).rstrip('/')
            new_record_dict = new_record.dict()
            new_record_dict["photo_url"] = f"{base_url}/uploads/{new_record.photo_path}"
            return new_record_dict
            
        return new_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records/", response_model=List[TravelRecordResponse])
async def get_records(request: Request):
    try:
        # 模擬從資料庫獲取記錄
        records = []  # 這裡應該是從資料庫獲取的記錄
        
        # 為每個記錄添加完整的照片訪問 URL
        base_url = str(request.base_url).rstrip('/')
        for record in records:
            if record.photo_path:
                record_dict = record.dict()
                record_dict["photo_url"] = f"{base_url}/uploads/{record.photo_path}"
                records.append(record_dict)
            else:
                records.append(record)
                
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records/{record_id}", response_model=TravelRecordResponse)
async def get_record(request: Request, record_id: str):
    # 模擬從資料庫獲取記錄
    record = None  # 這裡應該是從資料庫獲取的記錄
    
    if not record:
        raise HTTPException(status_code=404, detail="記錄不存在")
        
    # 添加完整的照片訪問 URL
    if record.photo_path:
        base_url = str(request.base_url).rstrip('/')
        record_dict = record.dict()
        record_dict["photo_url"] = f"{base_url}/uploads/{record.photo_path}"
        return record_dict
        
    return record

@router.put("/records/{record_id}", response_model=TravelRecordResponse)
async def update_record(request: Request, record_id: str, record_update: TravelRecordBase):
    # 模擬從資料庫獲取和更新記錄
    record = None  # 這裡應該是從資料庫獲取的記錄
    
    if not record:
        raise HTTPException(status_code=404, detail="記錄不存在")
    
    # 更新記錄
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
        
    # 添加完整的照片訪問 URL
    if record.photo_path:
        base_url = str(request.base_url).rstrip('/')
        record_dict = record.dict()
        record_dict["photo_url"] = f"{base_url}/uploads/{record.photo_path}"
        return record_dict
        
    return record

@router.delete("/records/{record_id}")
async def delete_record(record_id: str):
    # 模擬從資料庫刪除記錄
    record = None  # 這裡應該是從資料庫獲取的記錄
    
    if not record:
        raise HTTPException(status_code=404, detail="記錄不存在")
    
    # 如果有關聯的照片，也刪除照片文件
    if record.photo_path:
        photo_path = UPLOAD_DIR / record.photo_path
        if photo_path.exists():
            photo_path.unlink()
    
    # 從資料庫中刪除記錄
    
    return {"message": "記錄已刪除"}
