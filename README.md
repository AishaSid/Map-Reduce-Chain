# Map-Reduce LLM Pipeline for Meeting Transcripts

Extract and validate action items from long meeting transcripts using LangChain's Map-Reduce chain pattern.

## 🎯 Project Overview

Built a multi-stage Map–Reduce LLM pipeline using LangChain to extract and validate action items from long meeting transcripts.

### Output Schema
```json
{
  "task": "",
  "owner": "",
  "deadline": "",
  "confidence": 0.0
}
```

## 📁 Project Structure

```text
Map-Reduce-Chain/
├── src/
│   ├── config.py
│   ├── models.py                 # Pydantic schemas
│   ├── document_loader.py        # LangChain Documents + metadata
│   ├── map_chain.py              # MAP chain (Prompt + LLM + Parser)
│   ├── reduce_chain.py           # REDUCE chain
│   ├── confidence_chain.py       # Confidence scoring chain
│   ├── validation.py
│   ├── main.py                   # Pipeline orchestration
│   └── prompts/
│       ├── map_prompt.yaml
│       └── reduce_prompt.yaml
├── tests/
├── data/
├── notebooks/
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

```bash
# Copy the example to .env
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Run Tests

```bash
pytest tests/ -v
```

## 📅 Implementation Timeline

### Day 1: Core Extraction (MAP Phase)
- ✅ Define action item schema
- ✅ Transcript ingestion & metadata handling
- ✅ Smart chunking (by speaker turns, 1-2 minutes)
- ✅ MAP prompt + LangChain chain
- ✅ Output validation & retry logic

### Day 2: Consolidation (REDUCE Phase)
- ✅ Merge logic definition
- ✅ REDUCE prompt + chain
- ✅ Confidence scoring layer
- ✅ Edge case handling
- ✅ UI/CLI implementation
- ✅ Documentation

## 🧠 Key LangChain Concepts Used

- **Map-Reduce Chains**: Split, process, and consolidate
- **PromptTemplate**: Reusable prompt patterns
- **LLMChain**: Chain prompts with LLM calls
- **PydanticOutputParser**: Structured extraction
- **Document Objects**: Metadata-aware text processing
- **Custom Text Splitters**: Preserve speaker context
- **Retry & Validation**: Reliability patterns

## 📝 Usage Examples

### Extract from a transcript file

```python
from src.main import ActionItemExtractor

extractor = ActionItemExtractor()
items = extractor.extract("path/to/transcript.txt", "meeting_001")
for item in items:
     print(f"Task: {item.task}")
     print(f"Owner: {item.owner}")
     print(f"Confidence: {item.confidence}")
```

### Using the CLI

```bash
python src/main.py transcript.txt actions.json
```

### Using Streamlit UI

```bash
streamlit run src/app.py
```

## 🔧 Configuration

Edit `src/config.py` to customize:

- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `BATCH_SIZE`: Number of chunks to process at once
- `CONFIDENCE_THRESHOLD`: Minimum confidence score (0-1)
- `OPENAI_MODEL`: LLM to use (gpt-4, gpt-3.5-turbo)

## ✅ Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test:
```bash
pytest tests/ -k map -v
```

With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📚 Architecture Notes

### Why Map-Reduce?

1. **Scalability**: Process transcripts of any length
2. **Reliability**: LLM operates on focused contexts
3. **Debuggability**: Each stage is testable independently
4. **Flexibility**: Easy to add validation layers

### Workflow

```
Raw Transcript
     ↓
[Ingestion] → Add metadata, normalize
     ↓
[Chunking] → Speaker turns, preserve context
     ↓
[MAP Phase] → Extract candidates from each chunk
     ↓
[REDUCE Phase] → Deduplicate, fill gaps, normalize
     ↓
[Confidence Scoring] → Rate certainty
     ↓
[Validation] → Handle edge cases
     ↓
Structured Action Items
```

## 🚨 Known Limitations

- Requires clear speaker labels in transcript
- Performance degrades on very long transcripts (>1hr) without chunking optimization
- Confidence scores are heuristic-based
- LLM hallucinations possible on ambiguous deadlines

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Run `black` and `flake8` before committing
4. Update README if adding new functionality


**Built with**: LangChain, OpenAI, Pydantic, Streamlit
