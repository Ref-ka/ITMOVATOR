from typing import List

from pydantic import BaseModel, HttpUrl


class PredictionRequest(BaseModel):
    id: int
    query: str


# class PredictionResponse(BaseModel):
#     id: int
#     answer: int
#     reasoning: str
#     sources: List[HttpUrl]

from pydantic import BaseModel, HttpUrl
from typing import List

class PredictionResponse(BaseModel):
    id: int
    answer: int
    reasoning: str
    sources: List[HttpUrl]  # This is where the HttpUrl type is used

    def model_dump(self, *args, **kwargs):
        # Override the default model_dump to convert HttpUrl to string
        data = super().model_dump(*args, **kwargs)
        data["sources"] = [str(url) for url in self.sources]  # Convert HttpUrl to string
        return data