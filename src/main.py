"""Main orchestration - MAP-REDUCE pipeline."""

from typing import List
from src.document_loader import DocumentLoader
from src.map_chain import MapChain
from src.reduce_chain import ReduceChain
from src.confidence_chain import ConfidenceChain
from src.validation import ValidationLayer
from src.models import ActionItem
from src.config import get_logger, CONFIDENCE_THRESHOLD
import json


logger = get_logger(__name__)


class ActionItemExtractor:
    """Full MAP-REDUCE pipeline for extracting action items."""
    
    def __init__(self):
        """Initialize all components."""
        self.document_loader = DocumentLoader(chunk_strategy="speaker_turns")
        self.map_chain = MapChain()
        self.reduce_chain = ReduceChain()
        self.confidence_chain = ConfidenceChain()
        self.validator = ValidationLayer(confidence_threshold=CONFIDENCE_THRESHOLD)
        
        logger.info("Initialized ActionItemExtractor pipeline")
    
    def extract(self, transcript_text: str, source: str) -> List[ActionItem]:
        """
        Full pipeline: Load → MAP → REDUCE → Confidence → Validate
        
        Args:
            transcript_text: Raw transcript text
            source: Source identifier
            
        Returns:
            List of validated ActionItem objects
        """
        logger.info(f"Starting extraction pipeline for {source}")
        
        # Step 1: Load and chunk
        logger.info("Step 1: Loading and chunking document")
        chunks = self.document_loader.load(transcript_text, source)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 2: MAP - Extract candidates
        logger.info("Step 2: MAP phase - Extracting action items from chunks")
        map_results = []
        all_items = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)}")
            result = self.map_chain.extract(chunk.page_content, i, len(chunks))
            map_results.append(result)
            all_items.extend(result.items)
        
        logger.info(f"MAP phase extracted {len(all_items)} total items")
        
        if not all_items:
            logger.warning("No action items extracted in MAP phase")
            return []
        
        # Step 3: REDUCE - Consolidate
        logger.info("Step 3: REDUCE phase - Consolidating items")
        reduce_result = self.reduce_chain.consolidate(all_items)
        consolidated_items = reduce_result.items
        logger.info(f"REDUCE phase reduced to {len(consolidated_items)} items")
        
        # Step 4: Confidence scoring
        logger.info("Step 4: Confidence scoring")
        scored_items = self.confidence_chain.score_batch(consolidated_items)
        logger.info(f"Scored {len(scored_items)} items")
        
        # Step 5: Validation
        logger.info("Step 5: Validation and edge case handling")
        validated_items, rejected_items = self.validator.validate_batch(scored_items)
        validated_items = self.validator.handle_edge_cases(validated_items)
        
        logger.info(f"Pipeline complete: {len(validated_items)} valid items, {len(rejected_items)} rejected")
        
        return validated_items
    
    def extract_to_json(self, transcript_text: str, source: str, output_file: str = None) -> str:
        """
        Extract and return as JSON.
        
        Args:
            transcript_text: Raw transcript text
            source: Source identifier
            output_file: Optional file to save results
            
        Returns:
            JSON string of results
        """
        items = self.extract(transcript_text, source)
        
        result = {
            "source": source,
            "total_items": len(items),
            "items": [item.dict() for item in items]
        }
        
        json_output = json.dumps(result, indent=2)
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_output)
            logger.info(f"Results saved to {output_file}")
        
        return json_output


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <transcript_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Read transcript
    with open(input_file, "r") as f:
        transcript = f.read()
    
    # Extract
    extractor = ActionItemExtractor()
    json_result = extractor.extract_to_json(transcript, input_file, output_file)
    
    print(json_result)
