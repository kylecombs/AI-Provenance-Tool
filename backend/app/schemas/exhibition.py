from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ExhibitionBase(BaseModel):
    name: str
    venue: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ExhibitionCreate(ExhibitionBase):
    pass

class ExhibitionUpdate(BaseModel):
    name: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ExhibitionResponse(ExhibitionBase):
    id: int
    
    class Config:
        from_attributes = True

class ExhibitionListResponse(BaseModel):
    exhibitions: List[ExhibitionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int