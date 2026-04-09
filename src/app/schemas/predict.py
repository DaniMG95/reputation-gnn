from pydantic import BaseModel

class ChangeModelRequest(BaseModel):
    model_path: str