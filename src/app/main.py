from fastapi import FastAPI
from app.api import api_router
from common.db.connection import init_db_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_connection()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



