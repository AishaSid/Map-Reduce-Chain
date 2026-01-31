# Setup Guide - Map-Reduce LLM Pipeline

Follow these steps to get the project up and running.

## Prerequisites

- Python 3.10 or higher
- Git (optional, for version control)
- OpenAI API key (get from https://platform.openai.com/api-keys)

## Step 1: Create Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

## Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- **LangChain** & LangChain OpenAI integration
- **Pydantic** for data validation
- **Streamlit** for the web UI
- **Pytest** for testing
- **Python-dotenv** for environment variables
- Additional utilities for development

## Step 3: Configure Environment Variables

Open `.env` in your editor and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

## Step 4: Verify Installation

Test that everything works:

```bash
python -c "import langchain; import streamlit; print('All imports successful')"
```

Or run a quick test:

```bash
pytest tests/ -v
```

## Step 5: Project Structure

Your project is organized as:

```
src/
├── __init__.py           # Package initialization
├── config.py             # Configuration & logging setup
├── models.py             # Pydantic data models
├── transcript_processor.py  # Ingestion & chunking
├── map_phase.py          # MAP phase (to implement)
├── reduce_phase.py       # REDUCE phase (to implement)
├── confidence_scorer.py  # Confidence layer (to implement)
├── validation.py         # Edge cases (to implement)
└── main.py               # Orchestration (to implement)

data/
├── example_transcript.txt  # Sample transcript
└── outputs/              # Generated results

tests/
├── test_map_phase.py
├── test_reduce_phase.py
└── test_confidence_scorer.py
```

## Next Steps

### Testing During Development

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_map_phase.py -v

# Run specific test
pytest tests/test_map_phase.py::test_extraction -v
```

### Code Quality

Format code:
```bash
black src/ tests/
```

Check for style issues:
```bash
flake8 src/ tests/
```

Type checking:
```bash
mypy src/
```
