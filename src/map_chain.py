"""MAP phase - Extract action items from each transcript chunk."""

import yaml
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from src.models import ActionItem, MapPhaseOutput
from src.config import get_logger, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS
import json


logger = get_logger(__name__)


class MapChain:
    """LangChain-based MAP chain for action item extraction."""
    
    def __init__(self, model_name: str = OPENAI_MODEL):
        """Initialize the MAP chain with LLM and prompts."""
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        # Load prompt from YAML
        with open("src/prompts/map_prompt.yaml", "r") as f:
            prompt_config = yaml.safe_load(f)
        
        self.system_prompt = prompt_config["system_prompt"]
        self.user_prompt_template = prompt_config["user_prompt_template"]
        self.parser = PydanticOutputParser(pydantic_object=ActionItem)
        
        logger.info(f"Initialized MAP chain with model: {model_name}")
    
    def extract(self, chunk_text: str, chunk_index: int, total_chunks: int) -> MapPhaseOutput:
        """
        Extract action items from a single transcript chunk.
        
        Args:
            chunk_text: The transcript chunk text
            chunk_index: Index of this chunk
            total_chunks: Total number of chunks
            
        Returns:
            MapPhaseOutput with extracted items
        """
        import time
        start_time = time.time()
        
        try:
            # Format the user prompt
            user_prompt = self.user_prompt_template.format(transcript_chunk=chunk_text)
            
            # Create full prompt
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Extracting from chunk {chunk_index + 1}/{total_chunks}")
            
            # Call LLM
            response = self.llm.invoke(full_prompt)
            response_text = response.content
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    items_data = json.loads(json_str)
                else:
                    logger.warning(f"No valid JSON in response for chunk {chunk_index}")
                    items_data = []
                
                # Convert to ActionItem objects
                items = []
                for item_data in items_data:
                    try:
                        item = ActionItem(**item_data)
                        item.source_chunk = chunk_index
                        items.append(item)
                    except Exception as e:
                        logger.warning(f"Failed to parse item: {e}")
                
                processing_time = time.time() - start_time
                
                return MapPhaseOutput(
                    items=items,
                    chunk_index=chunk_index,
                    total_chunks=total_chunks,
                    processing_time=processing_time
                )
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                processing_time = time.time() - start_time
                return MapPhaseOutput(
                    items=[],
                    chunk_index=chunk_index,
                    total_chunks=total_chunks,
                    processing_time=processing_time,
                    error=f"JSON parsing failed: {str(e)}"
                )
        
        except Exception as e:
            logger.error(f"Error in MAP chain: {e}")
            processing_time = time.time() - start_time
            return MapPhaseOutput(
                items=[],
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                processing_time=processing_time,
                error=str(e)
            )
    
    def extract_batch(self, chunks: List[str]) -> List[MapPhaseOutput]:
        """Extract action items from multiple chunks."""
        results = []
        for i, chunk in enumerate(chunks):
            result = self.extract(chunk, i, len(chunks))
            results.append(result)
        return results
