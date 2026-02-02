# 🧠 Semantic Classifier

AI-Powered Data Classification System with Multi-Provider LLM Support and Comprehensive Evaluation Framework.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LiteLLM](https://img.shields.io/badge/litellm-1.0+-green.svg)](https://litellm.ai/)

## 📋 Overview

Semantic Classifier is an intelligent data classification system that leverages state-of-the-art Large Language Models (LLMs) to automatically discover categories and classify text data. Built with Streamlit for rapid development and LiteLLM for multi-provider LLM access.

### Key Features

- 🎯 **Automatic Category Discovery** - AI analyzes your data to suggest meaningful categories
- 🤖 **Multi-Provider LLM Support** - OpenAI (GPT-5.2, GPT-4.1), Anthropic (Claude Opus 4.5), AWS Bedrock
- 🔄 **Retry with Feedback** - Iteratively improve classifications with user feedback
- 📚 **Few-Shot Learning** - Add examples to guide classification on edge cases
- 📊 **Comprehensive Evaluation** - Self-consistency, synthetic testing, LLM-as-judge
- 💾 **Session Management** - Save and restore your work across sessions
- 📈 **Version Tracking** - Track classification iterations and compare results

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **OpenAI API Key** (required)
- **AWS Bedrock Access** (optional, for Claude via Bedrock)
- **Anthropic API Key** (optional, for direct Claude access)
- **Supabase Account** (for database and storage)

### Installation (< 5 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd testAlloBrainNew

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
alembic upgrade head

# 6. Run application
streamlit run app.py
```

**That's it!** The app will open at `http://localhost:8501`

📖 **Detailed Setup Guide**: See [docs/README.md](./docs/README.md)

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI]
        Upload[File Upload]
        Selector[Column Selector]
        Discovery[Category Discovery]
        Classification[Classification Interface]
        Evaluation[Evaluation Interface]
    end

    subgraph "Service Layer"
        LLM[LLM Service<br/>Multi-Provider]
        EvalService[Evaluation Service]
        FileService[File Service]
    end

    subgraph "Repository Layer"
        SessionRepo[Session Repository]
        ClassRepo[Classification Repository]
        ExampleRepo[Few-Shot Repository]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>via Supabase)]
        Storage[Supabase Storage]
    end

    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-5.2, GPT-4.1]
        Anthropic[Anthropic API<br/>Claude Opus 4.5]
        Bedrock[AWS Bedrock<br/>Claude via AWS]
    end

    UI --> Upload
    UI --> Selector
    UI --> Discovery
    UI --> Classification
    UI --> Evaluation

    Upload --> FileService
    Discovery --> LLM
    Classification --> LLM
    Evaluation --> EvalService

    LLM --> SessionRepo
    LLM --> ClassRepo
    LLM --> ExampleRepo
    EvalService --> LLM

    SessionRepo --> DB
    ClassRepo --> DB
    ExampleRepo --> DB
    FileService --> Storage

    LLM -.-> OpenAI
    LLM -.-> Anthropic
    LLM -.-> Bedrock

    style UI fill:#e1f5ff
    style LLM fill:#fff4e1
    style DB fill:#e8f5e9
    style OpenAI fill:#f3e5f5
    style Anthropic fill:#f3e5f5
    style Bedrock fill:#f3e5f5
```

📚 **Full Technical Documentation**: See [docs/TECHNICAL_ARCHITECTURE.md](./docs/TECHNICAL_ARCHITECTURE.md)

## 📖 Usage

### Workflow Steps

```mermaid
graph LR
    A[1. Upload<br/>File] --> B[2. Select<br/>Sheet]
    B --> C[3. Preview<br/>Data]
    C --> D[4. Select<br/>Column]
    D --> E[5. Discover<br/>Categories]
    E --> F[6. Classify<br/>Data]
    F --> G[7. Evaluate<br/>Quality]

    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style C fill:#e3f2fd
    style D fill:#fff3e0
    style E fill:#fff3e0
    style F fill:#e8f5e9
    style G fill:#f3e5f5
```

### Step-by-Step Guide

1. **Upload File** - CSV or Excel (multi-sheet supported)
2. **Select Sheet** - Choose which sheet to analyze
3. **Preview Data** - Review data and statistics
4. **Select Column** - Choose text column for classification
5. **Discover Categories** - AI suggests categories based on your data
6. **Classify Data** - Batch classify all rows
7. **Evaluate Quality** - Use evaluation tools to assess results

### Advanced Features

#### Retry with Feedback
- Select misclassified rows
- Provide feedback on what went wrong
- System creates new classification version
- Compare before/after results

#### Few-Shot Learning
- Add examples of text → category mappings
- System includes examples in classification prompts
- Improves accuracy on edge cases
- Examples persist across sessions

#### Model Selection
Choose from multiple providers:
- **OpenAI**: GPT-5.2 (recommended), GPT-5.1, GPT-4.1, GPT-4o
- **Anthropic Direct**: Claude Opus 4.5, Sonnet 4.5, Claude 3.7
- **AWS Bedrock**: Claude Opus 4.5, Sonnet 4.5 via Bedrock

#### Evaluation Framework
Three evaluation methods:
- **Self-Consistency**: Test robustness across temperatures
- **Synthetic Testing**: Generate and classify test examples
- **LLM-as-Judge**: Use stronger models (Opus 4.5, GPT-5.2) to evaluate

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI (Required)
OPENAI_API_KEY=your_openai_key

# Anthropic (Optional - for direct API)
ANTHROPIC_API_KEY=your_anthropic_key

# AWS Bedrock (Optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION_NAME=eu-west-3

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
Supabase_api_key=your_supabase_anon_key
Supabase_secret_key=your_supabase_service_key
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Model Configuration
LLM_MODEL=gpt-5.2-2025-12-11
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
```

### Model Configuration

Models can be changed dynamically in the UI sidebar:
- **Temperature**: 0.0 (deterministic) to 2.0 (creative)
- **Max Tokens**: 100 to 4000
- **Provider**: OpenAI, Anthropic, or Bedrock

## 🎯 Features

### ✅ Implemented

#### Data Ingestion
- Multi-format support (CSV, Excel with multiple sheets)
- Automatic encoding detection
- Smart data preview with configurable limits
- File storage in Supabase

#### Column Detection
- Auto-detect text columns using NLP metrics
- Column statistics and validation
- Sample value preview
- Intelligent column recommendations

#### Category Discovery
- LLM-powered category generation
- Stratified sampling for representative analysis
- Token limit management
- Category editing interface
- Boundary definitions for clarity

#### Classification
- Batch classification with progress tracking
- OpenAI structured outputs (prevents category hallucination)
- Confidence scoring
- Category distribution visualization
- Results export to CSV

#### Retry & Feedback
- Select rows to reclassify
- Add textual feedback to guide model
- Version tracking (preserves history)
- Before/after comparison with highlighting

#### Few-Shot Learning
- Add example text → category mappings
- Database persistence
- CSV import for bulk examples
- Dynamic prompt injection
- Session-specific or global examples

#### Evaluation Framework
- **Self-Consistency**: Multi-temperature testing
- **Synthetic Testing**: Generate and test examples per category
- **LLM-as-Judge**: Cross-model validation with Bedrock Opus + GPT-5.2
- Detailed metrics and reports

#### Session Management
- Save and restore sessions
- Load last session with one click
- Persistent storage of all workflow state
- Session history tracking

### 🔜 Planned

- Multi-label classification (multiple categories per row)
- Hierarchical categories (tree structure)
- Active learning (suggest most valuable rows for review)
- API mode (RESTful API for programmatic access)
- Batch export in multiple formats (JSON, Parquet)
- Model fine-tuning support
- Cost tracking and optimization

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit | Web UI framework |
| Backend | Python 3.9+ | Business logic |
| LLM Gateway | LiteLLM | Multi-provider LLM access |
| Database | PostgreSQL | Data persistence |
| ORM | SQLAlchemy | Database abstraction |
| Storage | Supabase Storage | File uploads |
| Migrations | Alembic | Database versioning |
| Testing | pytest | Unit/integration tests |

### Key Dependencies

```
streamlit>=1.28.0          # Web framework
litellm>=1.0.0             # LLM gateway
sqlalchemy>=2.0.0          # ORM
alembic>=1.12.0            # Migrations
pandas>=2.0.0              # Data processing
openpyxl>=3.1.0            # Excel support
supabase>=2.0.0            # Supabase client
pytest>=7.4.0              # Testing framework
```

## 🧪 Development

### Running Tests

```bash
# All tests
./scripts/run_tests.sh all

# With coverage
./scripts/run_tests.sh coverage

# Specific test file
./scripts/run_tests.sh few-shot

# Watch mode (re-run on changes)
./scripts/run_tests.sh watch
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Project Structure

```
testAlloBrainNew/
├── app.py                      # Main Streamlit application
├── src/
│   ├── config.py              # Configuration management
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── connection.py      # Database connection
│   │   └── repositories/      # Data access layer
│   ├── services/
│   │   ├── llm_service.py     # LLM integration
│   │   └── evaluation_service.py  # Evaluation logic
│   └── ui/
│       └── components/        # Streamlit UI components
├── migrations/                # Alembic migrations
├── tests/                     # Test suite
├── docs/                      # Documentation
│   ├── README.md             # Setup guide
│   └── TECHNICAL_ARCHITECTURE.md  # Technical docs
├── scripts/                   # Utility scripts
└── requirements.txt          # Python dependencies
```

## 📚 Documentation

- **[Setup Guide](./docs/README.md)** - Installation and configuration
- **[Technical Architecture](./docs/TECHNICAL_ARCHITECTURE.md)** - System design and LLM strategy
- **[Database Schema](./docs/DATABASE_SCHEMA_REFERENCE.md)** - Database structure
- **[Column Detection](./docs/COLUMN_DETECTION.md)** - Column detection logic

## 🐛 Troubleshooting

### Common Issues

**Import errors**: Ensure virtual environment is activated
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

**Database connection failed**: Check DATABASE_URL in `.env`

**API key errors**: Verify keys are set in `.env` and file is in project root

**Supabase storage errors**: Ensure `uploads` bucket exists and is public

**Bedrock models not working**: Verify AWS credentials and region match your setup

See [docs/README.md](./docs/README.md#troubleshooting) for more help.

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues or questions:
- Review documentation in `docs/`
- Check existing issues
- Open a new issue with detailed description

## 🔖 Version

Current version: **1.4.0**

### Recent Updates
- ✨ Added AWS Bedrock support for Claude models
- ✨ Comprehensive evaluation framework (self-consistency, synthetic, LLM-as-judge)
- ✨ Multi-provider LLM support (OpenAI, Anthropic, Bedrock)
- ✨ Few-shot learning with database persistence
- ✨ Retry classification with feedback and versioning
- ✨ Dynamic model selection with temperature controls

---

**Built with ❤️ using Streamlit and LiteLLM**
