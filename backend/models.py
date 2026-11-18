from pydantic import BaseModel


class ReviewRequest(BaseModel):
    code: str
    dateiname: str = "code.py"


class ReviewResponse(BaseModel):
    dateiname: str
    report: str
    status: str = "success"
