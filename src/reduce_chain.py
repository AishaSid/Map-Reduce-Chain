"""REDUCE phase - Consolidate and deduplicate action items."""

import yaml
from typing import List
from langchain_openai import ChatOpenAI
from src.models import ActionItem, ReducePhaseOutput
from src.config import get_logger, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS
import json


logger = get_logger(__name__)


class ReduceChain:
    """LangChain-based REDUCE chain for consolidating action items."""
    
    def __init__(self, model_name: str = OPENAI_MODEL):
        """Initialize the REDUCE chain."""
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=TEMPERATURE - 0.1,  # Lower temperature for consistency
            max_tokens=MAX_TOKENS
        )
        
        # Load prompt from YAML
        with open("src/prompts/reduce_prompt.yaml", "r") as f:
            prompt_config = yaml.safe_load(f)
        
        self.system_prompt = prompt_config["system_prompt"]
        self.user_prompt_template = prompt_config["user_prompt_template"]
        
        logger.info(f"Initialized REDUCE chain with model: {model_name}")
    
    def consolidate(self, items: List[ActionItem]) -> ReducePhaseOutput:
        """
        Consolidate and deduplicate action items.
        
        Args:
            items: List of ActionItem objects to consolidate
            
        Returns:
            ReducePhaseOutput with consolidated items
        """
        import time
        start_time = time.time()
        
        if not items:
            logger.info("No items to consolidate")
            return ReducePhaseOutput(
                items=[],
                duplicates_removed=0,
                fields_filled=0,
                total_processing_time=0
            )
        
        try:
            # Convert items to JSON for LLM
            items_json = json.dumps([item.dict() for item in items], indent=2)
            
            # Format the prompt
            user_prompt = self.user_prompt_template.format(items_json=items_json)
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Consolidating {len(items)} items")
            
            # Call LLM
            response = self.llm.invoke(full_prompt)
            response_text = response.content
            
            # Parse response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result_data = json.loads(json_str)
                else:
                    logger.warning("No valid JSON in REDUCE response")
                    result_data = {"items": []}
                
                # Convert to ActionItem objects
                consolidated_items = []
                for item_data in result_data.get("items", []):
                    try:
                        item = ActionItem(**item_data)
                        consolidated_items.append(item)
                    except Exception as e:
                        logger.warning(f"Failed to parse consolidated item: {e}")
                
                summary = result_data.get("summary", {})
                processing_time = time.time() - start_time
                
                return ReducePhaseOutput(
                    items=consolidated_items,
                    duplicates_removed=summary.get("duplicates_removed", 0),
                    fields_filled=summary.get("items_needing_review", 0),
                    total_processing_time=processing_time,
                    notes=f"Consolidated from {len(items)} items"
                )
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in REDUCE: {e}")
                processing_time = time.time() - start_time
                return ReducePhaseOutput(
                    items=items,  # Return originals if consolidation fails
                    duplicates_removed=0,
                    fields_filled=0,
                    total_processing_time=processing_time,
                    notes=f"Consolidation failed: {str(e)}"
                )
        
        except Exception as e:
            logger.error(f"Error in REDUCE chain: {e}")
            processing_time = time.time() - start_time
            return ReducePhaseOutput(
                items=items,
                duplicates_removed=0,
                fields_filled=0,
                total_processing_time=processing_time,
                notes=f"Error: {str(e)}"
            )
