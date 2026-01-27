# 🧠 Semantic Classifier

AI-Powered Data Classification System built with Streamlit and LiteLLM.

## 📋 Overview

This application provides an intelligent data classification system that:
- Uploads and parses CSV and Excel files (including multi-sheet support)
- Auto-detects text columns suitable for classification
- Uses LLM (GPT-4) to discover meaningful categories from your data
- Classifies data into discovered categories
- Provides an intuitive UI for category refinement and editing

## 🏗️ Architecture

```
semantic-classifier/
├── src/
│   ├── data_ingestion/      # File parsing, sampling, column detection
│   │   ├── file_parser.py
│   │   ├── data_sampler.py
│   │   └── column_detector.py
│   ├── category_discovery/  # Category generation and refinement
│   ├── classification/      # Classification orchestration
│   ├── services/           # LLM service (LiteLLM integration)
│   │   └── llm_service.py
│   ├── ui/                 # Streamlit UI components
│   │   ├── file_upload.py
│   │   ├── sheet_selector.py
│   │   ├── data_preview.py
│   │   ├── column_selector.py
│   │   ├── category_discovery.py
│   │   └── classification_interface.py
│   └── config.py          # Configuration management
├── tests/                 # Test suite
├── plan/                  # Technical documentation
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

### Step-by-Step Workflow

1. **Upload File**: Drag and drop or browse for a CSV or Excel file
2. **Select Sheet**: If Excel has multiple sheets, choose which one to work with
3. **Preview Data**: Review your data and column statistics
4. **Select Column**: Choose the text column you want to classify
5. **Discover Categories**: Let the AI analyze your data and suggest categories
6. **Edit Categories**: Review and refine the discovered categories
7. **Classify**: Run classification on sample or full dataset
8. **Export**: Download results as CSV

## ⚙️ Configuration

Edit `.env` file to configure:

```env
# OpenAI API Key
OPENAI_API_KEY=your_key_here

# Model settings
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000

# Data processing
MAX_PREVIEW_ROWS=100
SAMPLE_SIZE=50
MAX_TOKENS_FOR_SAMPLING=8000
```

## 🎯 Features

### Data Ingestion
- ✅ Excel (.xlsx, .xls) parsing with multi-sheet support
- ✅ CSV parsing with automatic encoding detection
- ✅ Smart data preview with row limiting
- ✅ Comprehensive column analysis

### Column Detection
- ✅ Auto-detect text columns
- ✅ Suggest best column for classification
- ✅ Column statistics and validation
- ✅ Sample value preview

### Category Discovery
- ✅ LLM-powered category generation
- ✅ Stratified sampling for analysis
- ✅ Token limit management
- ✅ Category editing interface
- ✅ Refinement with feedback

### Classification
- ✅ Sample or full dataset classification
- ✅ Progress tracking
- ✅ Category distribution visualization
- ✅ Results export to CSV

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM Integration**: LiteLLM (OpenAI provider)
- **Data Processing**: Pandas, NumPy
- **File Parsing**: openpyxl, xlrd, chardet

## 📝 Project Status

Current version: 0.1.0

### Implemented
- ✅ Data ingestion layer
- ✅ File parsing (CSV, Excel)
- ✅ Column detection
- ✅ Category discovery
- ✅ Basic classification
- ✅ Streamlit UI

### Planned
- ⏳ Batch processing optimization
- ⏳ Feedback loop implementation
- ⏳ Evaluation metrics
- ⏳ Session persistence
- ⏳ Advanced sampling strategies

## 📄 License

See plan folder for detailed technical documentation.
