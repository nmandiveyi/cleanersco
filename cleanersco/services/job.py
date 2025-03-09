from core.decorators.exceptions import catch_server_err
from models.job import Job as JobPayload, JobQueryParams
from prisma.models import Job
from core.services.db import prisma


class JobService:
    
    @catch_server_err
    @staticmethod
    async def create_job(payload: JobPayload) -> Job:
        payload.job_size = payload.job_size.upper()
        return await prisma.job.create(
            data=payload.model_dump(),
            include={
                "user": True
            }
        )
    @catch_server_err
    async def get_jobs(params: JobQueryParams):
        return await prisma.job.find_many(
            where={ 
                key: value for key, value
                in params.model_dump() if value
            }
        )
    
    
        
        