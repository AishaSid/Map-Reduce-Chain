"""Validation and edge case handling."""

from typing import List, Tuple
from src.models import ActionItem
from src.config import get_logger, CONFIDENCE_THRESHOLD


logger = get_logger(__name__)


class ValidationLayer:
    """Validate and filter action items."""
    
    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        """Initialize validation layer."""
        self.confidence_threshold = confidence_threshold
        logger.info(f"Initialized validation with threshold: {confidence_threshold}")
    
    def validate_item(self, item: ActionItem) -> Tuple[bool, str]:
        """
        Validate a single action item.
        
        Args:
            item: ActionItem to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check confidence threshold
        if item.confidence < self.confidence_threshold:
            return False, f"Confidence too low ({item.confidence} < {self.confidence_threshold})"
        
        # Check for empty task
        if not item.task or not item.task.strip():
            return False, "Task is empty"
        
        # Check for vague task descriptions
        vague_terms = ["something", "stuff", "thing", "whatever", "etc"]
        task_lower = item.task.lower()
        if any(term in task_lower for term in vague_terms):
            return False, "Task description is too vague"
        
        # Check for unassigned high-priority items
        if item.owner == "Unassigned" and item.deadline:
            logger.warning(f"Item without owner has deadline: {item.task}")
        
        return True, "Valid"
    
    def validate_batch(self, items: List[ActionItem]) -> Tuple[List[ActionItem], List[ActionItem]]:
        """
        Validate multiple items.
        
        Args:
            items: List of ActionItem objects
            
        Returns:
            Tuple of (valid_items, invalid_items)
        """
        valid_items = []
        invalid_items = []
        
        for item in items:
            is_valid, reason = self.validate_item(item)
            
            if is_valid:
                valid_items.append(item)
            else:
                logger.debug(f"Item rejected: {item.task} - {reason}")
                invalid_items.append(item)
        
        logger.info(f"Validation: {len(valid_items)} valid, {len(invalid_items)} invalid")
        return valid_items, invalid_items
    
    def handle_missing_fields(self, item: ActionItem) -> ActionItem:
        """Fill in missing fields with defaults."""
        if not item.owner or item.owner.strip() == "":
            item.owner = "Unassigned"
        
        if not item.deadline or item.deadline.strip() == "":
            item.deadline = "Not specified"
        
        if not item.notes:
            item.notes = None
        
        return item
    
    def handle_edge_cases(self, items: List[ActionItem]) -> List[ActionItem]:
        """Handle special edge cases."""
        processed_items = []
        
        for item in items:
            # Fill missing fields
            item = self.handle_missing_fields(item)
            
            # Handle conflicting owners
            if "and" in item.owner.lower() and item.owner.count(",") == 0:
                # Multiple owners listed without clear assignment
                logger.warning(f"Item has multiple owners: {item.owner}")
                # Keep as-is and let human review
            
            # Handle vague deadlines
            if item.deadline:
                vague_deadlines = ["soon", "ASAP", "when possible", "this week"]
                if any(term in item.deadline for term in vague_deadlines):
                    if not item.notes:
                        item.notes = ""
                    item.notes += " [DEADLINE NEEDS CLARIFICATION]"
            
            processed_items.append(item)
        
        return processed_items
