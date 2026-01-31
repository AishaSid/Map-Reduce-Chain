"""Configuration management for the project."""

import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Project Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.4"))

# Chunking Settings
CHUNK_STRATEGY = "speaker_turns"  # or "time_based"
CHUNK_SIZE_MINUTES = 2
MAX_CHUNK_TOKENS = 2000

# LLM Parameters
TEMPERATURE = 0.3  # Lower = more deterministic
MAX_TOKENS = 1000

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    level=LOG_LEVEL,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Validate configuration
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set in environment variables")


def get_logger(name: str):
    """Get a configured logger."""
    return logger.bind(name=name)
