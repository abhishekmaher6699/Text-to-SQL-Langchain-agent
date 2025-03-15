from pydantic import BaseModel, Field
from typing_extensions import List

class QueryOutput(BaseModel):
    query: str = Field(description="Valid SQL query to run")

class QueryValidation(BaseModel):
    isValid: str = Field(
        description="Query is useful to the question, 'yes' or 'no'"
    )
    suggestions: str = Field(description='Suggestion to fix or improve the query if any else none')

class DataValidation(BaseModel):
    ValidData: str = Field(description="yes if data is valid and no error exists else no")
    suggestions: str = Field(description='Suggestion to fix or improve the query if any else none')

class QueryBreakdown(BaseModel):
    subq: List[str] = Field(description="List of Subquestions in order")

class QueryAnalysis(BaseModel):
    breakdown: str = Field(description="yes if question should be broken down into subquestions else no")
