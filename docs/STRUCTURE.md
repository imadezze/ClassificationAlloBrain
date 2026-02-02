# Project Structure

## Overview

This document describes the organization of the Semantic Classifier project following a clean, modular architecture based on the technical plan.

## Directory Structure

```
testAlloBrainNew/
│
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
├── STRUCTURE.md                   # This file - project structure guide
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   │
│   ├── data_ingestion/           # DATA INGESTION LAYER
│   │   ├── __init__.py
│   │   ├── file_parser.py        # Excel/CSV parsing, multi-sheet support
│   │   ├── data_sampler.py       # Smart sampling for LLM analysis
│   │   └── column_detector.py    # Auto-detect text columns
│   │
│   ├── category_discovery/       # CATEGORY DISCOVERY LAYER
│   │   └── __init__.py           # Category generation and refinement
│   │
│   ├── classification/           # CLASSIFICATION LAYER
│   │   └── __init__.py           # Classification orchestration
│   │
│   ├── services/                 # SERVICES LAYER
│   │   ├── __init__.py
│   │   └── llm_service.py        # LiteLLM integration (OpenAI)
│   │
│   └── ui/                       # UI LAYER
│       ├── __init__.py
│       │
│       ├── components/           # Reusable UI components
│       │   ├── __init__.py
│       │   ├── file_upload.py            # File upload with drag & drop
│       │   ├── sheet_selector.py         # Sheet selection for Excel
│       │   ├── data_preview.py           # Data preview with row limits
│       │   ├── column_selector.py        # Column selection with auto-detect
│       │   ├── category_discovery.py     # Category discovery interface
│       │   └── classification_interface.py # Classification execution UI
│       │
│       ├── pages/                # Full page layouts (future)
│       │   └── __init__.py
│       │
│       └── utils/                # UI utility functions
│           └── __init__.py
│
├── tests/                        # Test suite
│   └── __init__.py
│
├── plan/                         # Technical documentation
│   └── Technical-Implementation-Guide.md
│
├── data/                         # Sample data files (not in git)
├── subject/                      # Project requirements
└── other/                        # Miscellaneous files
```

## Layer Responsibilities

### 1. Data Ingestion Layer (`src/data_ingestion/`)

**Purpose**: Handle all file parsing and data preprocessing

**Components**:
- `file_parser.py`: Parse Excel (.xlsx, .xls) and CSV files
- `data_sampler.py`: Smart sampling with stratified random sampling and token management
- `column_detector.py`: Auto-detect text columns and suggest classification targets

**Key Features**:
- Multi-sheet Excel support
- Automatic encoding detection for CSV
- Token-aware sampling
- Column validation

### 2. Category Discovery Layer (`src/category_discovery/`)

**Purpose**: Generate and refine categories dynamically

**Planned Components**:
- Content analyzer for theme extraction
- Category suggester using LLM
- Category refiner for user modifications
- Merge/split category operations

### 3. Classification Layer (`src/classification/`)

**Purpose**: Orchestrate classification pipeline

**Planned Components**:
- Classification orchestrator
- Batch processing
- Concurrency management
- Result aggregation

### 4. Services Layer (`src/services/`)

**Purpose**: Cross-cutting services and integrations

**Components**:
- `llm_service.py`: LiteLLM wrapper for OpenAI integration
  - Category discovery
  - Value classification
  - Batch classification
  - Category refinement

### 5. UI Layer (`src/ui/`)

**Purpose**: Streamlit user interface components

**Structure**:
- `components/`: Reusable UI components
  - File upload with drag & drop
  - Sheet selector
  - Data preview
  - Column selector with auto-detection
  - Category discovery and editor
  - Classification interface
- `pages/`: Full page layouts (for future multi-page app)
- `utils/`: UI helper functions

## Data Flow

```
1. File Upload (UI)
   ↓
2. File Parser (Data Ingestion)
   ↓
3. Sheet Selection (UI)
   ↓
4. Data Preview (UI)
   ↓
5. Column Detection (Data Ingestion)
   ↓
6. Column Selection (UI)
   ↓
7. Data Sampling (Data Ingestion)
   ↓
8. Category Discovery (LLM Service)
   ↓
9. Category Editing (UI)
   ↓
10. Classification (LLM Service)
    ↓
11. Results Display (UI)
    ↓
12. Export Results (UI)
```

## Module Dependencies

```
app.py
  └─> src.ui.components.*
      └─> src.data_ingestion.*
      └─> src.services.llm_service
          └─> src.config

src.data_ingestion.*
  └─> src.config

src.services.*
  └─> src.config
```

## Configuration

All configuration is centralized in `src/config.py` which loads from `.env`:

- OpenAI API credentials
- Model settings (model name, temperature, max tokens)
- Data processing settings (preview limits, sample sizes)
- Supported file types

## Extension Points

### Adding New File Types
- Extend `FileParser` in `src/data_ingestion/file_parser.py`
- Update `Config.SUPPORTED_*_EXTENSIONS`

### Adding New Classification Methods
- Create new classifier in `src/classification/`
- Extend LLM service or create new service

### Adding New UI Components
- Create component in `src/ui/components/`
- Export in `src/ui/components/__init__.py`
- Import in `app.py`

### Adding New Pages
- Create page in `src/ui/pages/`
- Configure Streamlit multipage in `app.py`

## Best Practices

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Modularity**: Components are self-contained and reusable
3. **Configuration**: All settings in one place (`config.py`)
4. **Error Handling**: Each layer handles its own errors
5. **Type Hints**: Use type hints for better code documentation
6. **Documentation**: Docstrings for all public functions

## Future Structure

As the project grows, consider:

- `src/storage/` - Data persistence layer
- `src/evaluation/` - Evaluation metrics and validation
- `src/feedback/` - Feedback loop implementation
- `src/api/` - REST API endpoints
- `src/models/` - Data models and schemas
- `src/utils/` - Shared utility functions
