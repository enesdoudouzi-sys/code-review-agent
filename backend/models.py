from pydantic import BaseModel


class ReviewRequest(BaseModel):
    code: str
    dateiname: str = "code.py"


class ReviewResponse(BaseModel):
    dateiname: str
    report: str
    status: str = "success"


class DateiReview(BaseModel):
    dateiname: str
    code: str


class MultiReviewRequest(BaseModel):
    dateien: list[DateiReview]


class MultiReviewResponse(BaseModel):
    reviews: list[ReviewResponse]
    dateien_gesamt: int


class PRRequest(BaseModel):
    pr_url: str
