from typing import Optional
from pydantic import BaseModel
from enum import StrEnum, auto

class JobSize(StrEnum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    

class Job(BaseModel):
  user_id: int
  description: str
  job_size: JobSize
  
class JobQueryParams(BaseModel):
  id: Optional[int]
