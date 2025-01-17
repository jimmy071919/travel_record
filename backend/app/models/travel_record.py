from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TravelRecordBase(BaseModel):
    location_name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = None
    photo_url: Optional[str] = None

class TravelRecordCreate(TravelRecordBase):
    pass

class TravelRecordInDB(TravelRecordBase):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
