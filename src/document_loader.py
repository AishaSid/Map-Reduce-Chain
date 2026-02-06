"""Document loading and chunking utilities for transcripts."""

from typing import List, Dict, Optional
from langchain.schema import Document
from src.models import TranscriptMetadata
from src.config import get_logger, CHUNK_SIZE_MINUTES, MAX_CHUNK_TOKENS


logger = get_logger(__name__)


class DocumentLoader:
    """Load and chunk transcripts while preserving metadata."""
    
    def __init__(self, chunk_strategy: str = "speaker_turns"):
        """
        Initialize the document loader.
        
        Args:
            chunk_strategy: "speaker_turns" or "time_based"
        """
        self.chunk_strategy = chunk_strategy
    
    def ingest(self, text: str, source: str, metadata: Optional[Dict] = None) -> List[Document]:
        """
        Convert raw transcript text into Document objects with metadata.
        
        Args:
            text: Raw transcript text
            source: Source identifier (filename, meeting ID, etc.)
            metadata: Optional additional metadata
            
        Returns:
            List of Document objects with metadata
        """
        logger.info(f"Ingesting transcript from {source}")
        
        lines = text.strip().split("\n")
        documents = []
        
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                doc_metadata = {
                    "source": source,
                    "line_index": i,
                    "original_text": line,
                }
                
                # Extract speaker if present (format: "Speaker: text")
                if ":" in line:
                    parts = line.split(":", 1)
                    speaker = parts[0].strip()
                    content = parts[1].strip()
                    doc_metadata["speaker"] = speaker
                else:
                    content = line
                    doc_metadata["speaker"] = "Unknown"
                
                # Add any provided metadata
                if metadata:
                    doc_metadata.update(metadata)
                
                doc = Document(page_content=content, metadata=doc_metadata)
                documents.append(doc)
        
        logger.info(f"Ingested {len(documents)} lines from transcript")
        return documents
    
    def chunk_by_speaker_turns(self, documents: List[Document]) -> List[Document]:
        """
        Chunk transcript by speaker turns, preserving context.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Chunked documents with turn-based grouping
        """
        logger.info("Chunking transcript by speaker turns")
        
        if not documents:
            return []
        
        chunks = []
        current_chunk_content = []
        current_speaker = None
        chunk_index = 0
        
        for doc in documents:
            speaker = doc.metadata.get("speaker", "Unknown")
            
            # Start new chunk when speaker changes
            if current_speaker is not None and speaker != current_speaker:
                # Save current chunk
                if current_chunk_content:
                    chunk_text = "\n".join(current_chunk_content)
                    chunk_metadata = {
                        "chunk_index": chunk_index,
                        "chunk_strategy": "speaker_turns",
                        "speaker": current_speaker,
                        "num_lines": len(current_chunk_content),
                        "source": doc.metadata.get("source", "unknown"),
                    }
                    chunks.append(Document(page_content=chunk_text, metadata=chunk_metadata))
                    chunk_index += 1
                    current_chunk_content = []
            
            current_chunk_content.append(doc.page_content)
            current_speaker = speaker
        
        # Don't forget the last chunk
        if current_chunk_content:
            chunk_text = "\n".join(current_chunk_content)
            chunk_metadata = {
                "chunk_index": chunk_index,
                "chunk_strategy": "speaker_turns",
                "speaker": current_speaker,
                "num_lines": len(current_chunk_content),
                "source": documents[-1].metadata.get("source", "unknown"),
            }
            chunks.append(Document(page_content=chunk_text, metadata=chunk_metadata))
        
        logger.info(f"Created {len(chunks)} chunks from speaker turns")
        return chunks
    
    def chunk_by_time(self, documents: List[Document], chunk_size_minutes: int = CHUNK_SIZE_MINUTES) -> List[Document]:
        """
        Chunk transcript by time intervals.
        
        Args:
            documents: List of Document objects
            chunk_size_minutes: Size of each chunk in minutes
            
        Returns:
            Chunked documents by time
        """
        logger.info(f"Chunking transcript by {chunk_size_minutes} minute intervals")
        
        # Simple implementation: group documents by rough time estimation
        # In production, you'd parse timestamp metadata
        chunks = []
        chunk_size = max(1, len(documents) // max(1, len(documents) // (chunk_size_minutes * 30)))
        
        for i, chunk_docs in enumerate([documents[j:j + chunk_size] for j in range(0, len(documents), chunk_size)]):
            if chunk_docs:
                chunk_text = "\n".join([doc.page_content for doc in chunk_docs])
                chunk_metadata = {
                    "chunk_index": i,
                    "chunk_strategy": "time_based",
                    "num_lines": len(chunk_docs),
                    "source": chunk_docs[0].metadata.get("source", "unknown"),
                }
                chunks.append(Document(page_content=chunk_text, metadata=chunk_metadata))
        
        logger.info(f"Created {len(chunks)} time-based chunks")
        return chunks
    
    def process(self, text: str, source: str, metadata: Optional[Dict] = None) -> List[Document]:
        """
        Full pipeline: ingest → chunk.
        
        Args:
            text: Raw transcript text
            source: Source identifier
            metadata: Optional metadata
            
        Returns:
            List of chunked documents
        """
        documents = self.ingest(text, source, metadata)
        
        if self.chunk_strategy == "speaker_turns":
            chunks = self.chunk_by_speaker_turns(documents)
        elif self.chunk_strategy == "time_based":
            chunks = self.chunk_by_time(documents)
        else:
            logger.warning(f"Unknown chunk strategy: {self.chunk_strategy}, using speaker_turns")
            chunks = self.chunk_by_speaker_turns(documents)
        
        return chunks
