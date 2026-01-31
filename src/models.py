"""Pydantic models for action items and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ActionItem(BaseModel):
    """Schema for extracted action item."""
    
    task: str = Field(..., description="The action task to be completed")
    owner: str = Field(default="Unassigned", description="Person responsible for the task")
    deadline: Optional[str] = Field(default=None, description="When the task should be completed")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score (0-1)")
    source_chunk: Optional[int] = Field(default=None, description="Original chunk index")
    speaker: Optional[str] = Field(default=None, description="Speaker who mentioned the task")
    notes: Optional[str] = Field(default=None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "Implement user authentication",
                "owner": "Sarah",
                "deadline": "2024-02-15",
                "confidence": 0.92,
                "source_chunk": 3,
                "speaker": "John",
                "notes": "Mentioned during security discussion"
            }
        }


class MapPhaseOutput(BaseModel):
    """Output from MAP phase."""
    
    items: List[ActionItem]
    chunk_index: int
    total_chunks: int
    processing_time: float
    error: Optional[str] = None


class ReducePhaseOutput(BaseModel):
    """Output from REDUCE phase."""
    
    items: List[ActionItem]
    duplicates_removed: int
    fields_filled: int
    total_processing_time: float
    notes: Optional[str] = None


class TranscriptMetadata(BaseModel):
    """Metadata for a transcript."""
    
    source: str
    duration_minutes: Optional[float] = None
    speaker_list: List[str] = []
    date: Optional[datetime] = None
    language: str = "English"
    chunk_strategy: str = "speaker_turns"  # or "time_based"
    chunk_size: int = 3  # minutes if time_based
