"""Confidence scoring for action items."""

from typing import List
from langchain_openai import ChatOpenAI
from src.models import ActionItem
from src.config import get_logger, OPENAI_MODEL
import json


logger = get_logger(__name__)


class ConfidenceChain:
    """Score confidence of action items."""
    
    def __init__(self, model_name: str = OPENAI_MODEL):
        """Initialize the confidence scorer."""
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        
        logger.info(f"Initialized Confidence chain with model: {model_name}")
    
    def score_confidence(self, item: ActionItem) -> float:
        """
        Score confidence of a single action item.
        
        Args:
            item: ActionItem to score
            
        Returns:
            Confidence score 0-1
        """
        prompt = f"""
        Rate your confidence (0.0-1.0) that this is a genuine, actionable task from a meeting:
        
        Task: {item.task}
        Owner: {item.owner}
        Deadline: {item.deadline}
        
        Consider:
        - How explicit is the task?
        - How clear is the owner?
        - How specific is the deadline?
        
        Return ONLY a number between 0.0 and 1.0.
        """
        
        try:
            response = self.llm.invoke(prompt)
            score_text = response.content.strip()
            
            # Try to parse as float
            score = float(score_text)
            return max(0.0, min(1.0, score))  # Clamp to 0-1
        
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse confidence score: {score_text}")
            return item.confidence  # Return original if parsing fails
    
    def score_batch(self, items: List[ActionItem]) -> List[ActionItem]:
        """Score confidence for multiple items."""
        scored_items = []
        
        for i, item in enumerate(items):
            logger.info(f"Scoring item {i + 1}/{len(items)}")
            item.confidence = self.score_confidence(item)
            scored_items.append(item)
        
        return scored_items
