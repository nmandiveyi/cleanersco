from typing import Annotated
from fastapi import APIRouter, Query

from services.job import JobService
from models.job import Job as JobPayload, JobQueryParams
from prisma.models import Job


router = APIRouter()

@router.post("/")
async def create_job(payload: JobPayload) -> Job:
    return await JobService.create_job(payload)

router.get("/")
async def get_jobs(params: Annotated[JobQueryParams, Query()] = None):
    return JobService.get_jobs(params)
    