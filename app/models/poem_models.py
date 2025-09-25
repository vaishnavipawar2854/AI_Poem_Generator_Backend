from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class PoemRequest(BaseModel):
    """Request model for poem generation"""
    theme: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="The theme or topic for the poem",
        example="love and nature"
    )
    style: Literal["creative", "haiku", "sonnet", "free_verse", "rhyming"] = Field(
        default="creative",
        description="The style of poem to generate"
    )
    length: Literal["short", "medium", "long"] = Field(
        default="medium",
        description="The desired length of the poem"
    )

class PoemResponse(BaseModel):
    """Enhanced response model for poem generation"""
    success: bool = True
    poem: str = Field(..., description="The generated poem text")
    theme: str = Field(..., description="The theme used for generation")
    style: str = Field(..., description="The style used for generation")
    length: str = Field(..., description="The length used for generation")
    generated_at: datetime = Field(default_factory=datetime.now)
    generation_method: Optional[str] = Field(default=None, description="Method used: 'openai' or 'fallback'")
    response_time_seconds: Optional[float] = Field(default=None, description="Time taken to generate the poem")
    using_openai: bool = Field(default=False, description="Whether OpenAI was used (deprecated, use generation_method)")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Health message")
    openai_configured: bool = Field(..., description="Whether OpenAI API key is configured")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")