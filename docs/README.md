# Semantic Classifier - Setup Guide

Quick setup guide to get the Semantic Classifier running in less than 5 minutes.

## Prerequisites

### Required Software
- **Python 3.9+** - Check version with `python --version`
- **PostgreSQL** (via Supabase or local)
- **pip** - Python package manager

### Required API Keys
1. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **AWS Bedrock Access** (optional) - For Claude Opus 4.5 via Bedrock
3. **Anthropic API Key** (optional) - For direct Claude API access
4. **Supabase Account** - For database and file storage

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd testAlloBrainNew
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration (Optional - for direct API)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AWS Bedrock Configuration (Optional - for Bedrock models)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION_NAME=eu-west-3

# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
Supabase_api_key=your_supabase_anon_key
Supabase_secret_key=your_supabase_service_role_key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 5. Initialize Database

Run database migrations:
```bash
alembic upgrade head
```

### 6. Configure Supabase Storage

1. Go to your Supabase project dashboard
2. Navigate to Storage
3. Create a new bucket named `uploads`
4. Set bucket to **Public** (or configure appropriate policies)

## Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Alternative: Using Scripts
```bash
# Run with custom port
streamlit run app.py --server.port 8080

# Run in development mode
streamlit run app.py --server.runOnSave true
```

## Quick Start Workflow

Once the app is running:

1. **Upload Data** - Upload CSV or Excel file
2. **Select Sheet** - Choose the sheet to work with
3. **Preview Data** - Review your data
4. **Select Column** - Choose the text column to classify
5. **Discover Categories** - Let AI discover categories automatically
6. **Classify Data** - Run classification on your data
7. **Evaluate Quality** - Use evaluation tools to assess results

## Configuration Options

### Model Selection
The app supports multiple LLM providers:
- **OpenAI**: GPT-5.2, GPT-5.1, GPT-5, GPT-4.1, GPT-4o
- **Anthropic (Direct)**: Claude Opus 4.5, Sonnet 4.5, Claude 3.7
- **AWS Bedrock**: Claude Opus 4.5, Sonnet 4.5 via Bedrock

Select your preferred model in the sidebar under "Model Selection".

### Advanced Settings
Adjust in the sidebar:
- **Temperature**: 0.0 (deterministic) to 2.0 (creative)
- **Max Tokens**: 100 to 4000
- **Sample Size**: Number of rows to sample for category discovery

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'streamlit'`
- **Solution**: Ensure virtual environment is activated and dependencies installed

**Issue**: `Database connection failed`
- **Solution**: Check DATABASE_URL in `.env` is correct

**Issue**: `OpenAI API key not found`
- **Solution**: Verify OPENAI_API_KEY is set in `.env`

**Issue**: `Supabase storage error`
- **Solution**: Check bucket exists and is publicly accessible

**Issue**: `AWS Bedrock models not working`
- **Solution**: Verify AWS credentials are correct and region matches your setup

### Getting Help

- Check logs in the Streamlit app (bottom right corner)
- Review [Technical Documentation](./TECHNICAL_ARCHITECTURE.md)
- Check [Database Schema](./DATABASE_SCHEMA_REFERENCE.md)

## Next Steps

- Read [Technical Architecture](./TECHNICAL_ARCHITECTURE.md) to understand the system
- Review [Column Detection](./COLUMN_DETECTION.md) for how text columns are identified
- Explore evaluation features for quality assessment

## Development

### Running Tests
```bash
# Run all tests
./scripts/run_tests.sh all

# Run specific test file
./scripts/run_tests.sh few-shot

# Run with coverage
./scripts/run_tests.sh coverage
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Production Deployment

For production deployment:
1. Set appropriate environment variables
2. Use PostgreSQL connection pooling
3. Configure Supabase security policies
4. Set up monitoring and logging
5. Use production-grade web server (not Streamlit's dev server)

## License

[Add your license information here]
