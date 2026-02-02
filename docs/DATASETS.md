# Dataset Documentation

This document provides comprehensive information about the datasets used in the Semantic Classifier application, including the main dataset, subdatasets, their structure, and how to use them.

## Table of Contents

- [Overview](#overview)
- [Main Dataset](#main-dataset)
- [Subdatasets](#subdatasets)
- [Dataset Structure](#dataset-structure)
- [Generation Process](#generation-process)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## Overview

The Semantic Classifier uses customer support ticket data to demonstrate its AI-powered classification capabilities. The dataset collection includes:

- **1 Main Dataset**: Complete customer support tickets dataset
- **43 CSV Subdatasets**: Various filtered and sampled subsets
- **10 Excel Subdatasets**: Key datasets in Excel format for easy viewing

**Total Records**: 8,469 customer support tickets

---

## Main Dataset

### Location
```
data/customer_support_tickets.csv
```

### Description
Complete dataset of customer support tickets containing various ticket types, priorities, and customer interactions across multiple channels.

### Schema

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `Ticket ID` | Integer | Unique ticket identifier | 1, 2, 3... |
| `Customer Name` | String | Full name of customer | "John Smith" |
| `Customer Email` | String | Customer email address | "john@example.com" |
| `Customer Age` | Integer | Customer age | 32 |
| `Customer Gender` | String | Customer gender | "Male", "Female", "Other" |
| `Product Purchased` | String | Product name | "Canon EOS", "GoPro Hero" |
| `Date of Purchase` | Date | Purchase date | "2021-03-22" |
| `Ticket Type` | String | Category of ticket | See [Ticket Types](#ticket-types) |
| `Ticket Subject` | String | Brief ticket summary | "Product setup" |
| `Ticket Description` | Text | Detailed ticket content | Full description text |
| `Ticket Status` | String | Current status | "Open", "Closed", "Pending Customer Response" |
| `Resolution` | Text | Resolution notes | Resolution text or null |
| `Ticket Priority` | String | Priority level | "Low", "Medium", "High", "Critical" |
| `Ticket Channel` | String | Support channel | "Email", "Phone", "Chat", "Social media" |
| `First Response Time` | Datetime | Initial response timestamp | "2023-06-01 12:15:36" |
| `Time to Resolution` | Datetime | Resolution timestamp | "2023-06-01 18:05:38" or null |
| `Customer Satisfaction Rating` | Float | Rating 1-5 | 3.0, 4.5, null |

### Ticket Types

The dataset contains 5 distinct ticket types:

1. **Technical issue** (1,747 tickets) - Hardware/software problems, compatibility issues
2. **Refund request** (1,752 tickets) - Customer refund inquiries
3. **Billing inquiry** (1,634 tickets) - Payment and billing questions
4. **Product inquiry** (1,641 tickets) - Product information requests
5. **Cancellation request** (1,695 tickets) - Service/order cancellations

### Statistics

- **Total Tickets**: 8,469
- **Unique Products**: 42
- **Priority Levels**: 4 (Low, Medium, High, Critical)
- **Support Channels**: 4 (Email, Phone, Chat, Social media)
- **Status Types**: 3 (Open, Closed, Pending Customer Response)
- **Date Range**: 2020 - 2021
- **Satisfaction Ratings**: Some tickets include ratings (1-5 scale)

---

## Subdatasets

Subdatasets are pre-generated subsets of the main dataset, organized by various criteria for testing and demonstration purposes.

### Location
```
data/subdatasets/          # CSV files
data/subdatasets/excel/    # Excel files
```

### Categories

#### 1. Random Samples
**Purpose**: General testing with various dataset sizes

| File | Records | Description |
|------|---------|-------------|
| `random_sample_50.csv` | 50 | Small sample for quick tests |
| `random_sample_100.csv` | 100 | Standard small test set |
| `random_sample_200.csv` | 200 | Medium test set |
| `random_sample_500.csv` | 500 | Larger test set |
| `random_sample_1000.csv` | 1,000 | Large test set |
| `random_sample_2000.csv` | 2,000 | Extra large test set |

**Use Case**: Quick prototyping, performance testing, feature demos

---

#### 2. Stratified Samples
**Purpose**: Balanced representation across ticket types

| File | Records | Description |
|------|---------|-------------|
| `stratified_sample_50.csv` | 50 | Balanced small sample |
| `stratified_sample_100.csv` | 100 | Balanced standard sample |
| `stratified_sample_200.csv` | 200 | Balanced medium sample |
| `stratified_sample_500.csv` | 500 | Balanced large sample |
| `stratified_sample_1000.csv` | 1,000 | Balanced extra large sample |
| `stratified_sample_2000.csv` | 2,000 | Balanced XXL sample |

**Use Case**: Training/testing ML models, ensuring category representation

---

#### 3. By Ticket Type
**Purpose**: Focus on specific ticket categories

| File | Records | Type |
|------|---------|------|
| `ticket_type_technical_issue.csv` | 1,747 | Technical issues only |
| `ticket_type_refund_request.csv` | 1,752 | Refund requests only |
| `ticket_type_billing_inquiry.csv` | 1,634 | Billing questions only |
| `ticket_type_product_inquiry.csv` | 1,641 | Product inquiries only |
| `ticket_type_cancellation_request.csv` | 1,695 | Cancellation requests only |

**Use Case**: Category-specific analysis, specialized classification tasks

---

#### 4. By Priority
**Purpose**: Filter by urgency level

| File | Records | Priority |
|------|---------|----------|
| `priority_critical.csv` | 2,129 | Critical priority only |
| `priority_high.csv` | 2,085 | High priority only |
| `priority_medium.csv` | 2,192 | Medium priority only |
| `priority_low.csv` | 2,063 | Low priority only |

**Use Case**: SLA testing, priority-based routing, urgency classification

---

#### 5. By Status
**Purpose**: Filter by ticket state

| File | Records | Status |
|------|---------|--------|
| `status_open.csv` | 2,819 | Open tickets |
| `status_closed.csv` | 2,769 | Closed tickets |
| `status_pending_customer_response.csv` | 2,881 | Pending response |

**Use Case**: Workflow testing, status-based analysis

---

#### 6. By Product (Top 10)
**Purpose**: Product-specific analysis

| File | Records | Product |
|------|---------|---------|
| `product_canon_eos.csv` | 240 | Canon EOS camera |
| `product_gopro_hero.csv` | 228 | GoPro Hero |
| `product_nest_thermostat.csv` | 225 | Nest Thermostat |
| `product_philips_hue_lights.csv` | 221 | Philips Hue Lights |
| `product_amazon_echo.csv` | 221 | Amazon Echo |
| `product_lg_smart_tv.csv` | 219 | LG Smart TV |
| `product_sony_xperia.csv` | 217 | Sony Xperia |
| `product_roomba_robot_vacuum.csv` | 216 | Roomba Robot Vacuum |
| `product_apple_airpods.csv` | 213 | Apple AirPods |
| `product_lg_oled.csv` | 213 | LG OLED TV |

**Use Case**: Product-specific issue analysis, targeted testing

---

#### 7. By Channel
**Purpose**: Filter by support channel

| File | Records | Channel |
|------|---------|---------|
| `channel_email.csv` | 2,143 | Email support |
| `channel_phone.csv` | 2,132 | Phone support |
| `channel_social_media.csv` | 2,121 | Social media |
| `channel_chat.csv` | 2,073 | Live chat |

**Use Case**: Channel-specific analysis, omnichannel testing

---

#### 8. Quality-Based
**Purpose**: Filter by customer satisfaction

| File | Records | Description |
|------|---------|-------------|
| `quality_high_satisfaction.csv` | 500 | 4-5 star ratings |
| `quality_low_satisfaction.csv` | 500 | 1-2 star ratings |

**Use Case**: Quality analysis, sentiment correlation

---

#### 9. Time-Based
**Purpose**: Filter by time period

| File | Records | Period |
|------|---------|--------|
| `time_recent_2021_onwards.csv` | 1,000 | 2021 onwards |
| `time_older_before_2021.csv` | 1,000 | Before 2021 |

**Use Case**: Temporal analysis, trend detection

---

#### 10. Edge Cases
**Purpose**: Test handling of special cases

| File | Records | Description |
|------|---------|-------------|
| `edge_case_missing_ratings.csv` | 100 | No satisfaction rating |

**Use Case**: Null handling, incomplete data testing

---

### Excel Datasets

Located in `data/subdatasets/excel/`, these are Excel-formatted versions of key datasets for easy viewing and sharing:

- `random_sample_100.xlsx` - Quick demo dataset
- `random_sample_500.xlsx` - Medium demo dataset
- `stratified_sample_100.xlsx` - Balanced demo dataset
- `ticket_type_technical_issue.xlsx` - Technical issues
- `ticket_type_billing_inquiry.xlsx` - Billing questions
- `priority_critical.xlsx` - Critical tickets
- `status_open.xlsx` - Open tickets
- `quality_high_satisfaction.xlsx` - Satisfied customers
- `quality_low_satisfaction.xlsx` - Unsatisfied customers
- `channel_email.xlsx` - Email channel

**Features**:
- Auto-adjusted column widths for readability
- Formatted headers
- Easy to open in Excel, Google Sheets, or LibreOffice

---

## Dataset Structure

### CSV Format
All CSV files follow this structure:
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Header**: First row contains column names
- **Line Endings**: Unix-style (`\n`)

### Excel Format
Excel files include:
- **Sheet Name**: "Customer Support Tickets"
- **Auto-formatted columns**: Width adjusted to content
- **Headers**: Bold and frozen (first row)
- **Format**: `.xlsx` (Office Open XML)

---

## Generation Process

### Automated Generation

Subdatasets are generated using the automated script:

```bash
python scripts/create_subdatasets.py
```

### Script Options

```bash
# Custom input file
python scripts/create_subdatasets.py --input path/to/tickets.csv

# Custom output directory
python scripts/create_subdatasets.py --output-dir data/my_subdatasets

# Custom sample sizes
python scripts/create_subdatasets.py --sizes 100,250,500,1000
```

### Generation Methods

1. **Random Sampling**: Uses `pandas.DataFrame.sample()` with fixed seed (42) for reproducibility
2. **Stratified Sampling**: Groups by ticket type, samples proportionally from each group
3. **Filtering**: Uses `pandas` boolean indexing for category/value filtering
4. **Excel Export**: Uses `openpyxl` engine with auto-formatting

### Output Files

After generation, the script creates:
- CSV subdatasets in `data/subdatasets/`
- Excel files in `data/subdatasets/excel/`
- `subdatasets_metadata.json` - Metadata about all subdatasets
- `SUBDATASETS_REPORT.md` - Human-readable summary

---

## Usage Examples

### In the Application

1. **Upload via UI**:
   ```
   streamlit run app.py
   → Upload File → Select subdataset
   ```

2. **Programmatic Loading**:
   ```python
   import pandas as pd

   # Load any subdataset
   df = pd.read_csv('data/subdatasets/random_sample_100.csv')
   ```

### For Testing

```python
import pytest
import pandas as pd

def test_classification_with_sample():
    """Test classification with a small sample"""
    df = pd.read_csv('data/subdatasets/random_sample_50.csv')
    # Your test code here
```

### For Demonstrations

```python
from src.data_ingestion.file_parser import FileParser

# Demo with technical issues
parser = FileParser('data/subdatasets/ticket_type_technical_issue.csv')
df = parser.parse()
```

### For Evaluation

```python
# Use stratified sample for balanced evaluation
eval_data = pd.read_csv('data/subdatasets/stratified_sample_500.csv')

# Evaluate classification accuracy across all ticket types
results = evaluate_model(eval_data)
```

---

## Best Practices

### Choosing the Right Dataset

| Use Case | Recommended Dataset |
|----------|-------------------|
| Quick demo | `random_sample_100.csv` |
| Feature testing | `random_sample_50.csv` or `random_sample_100.csv` |
| Performance testing | `random_sample_1000.csv` or `random_sample_2000.csv` |
| Model training | `stratified_sample_1000.csv` or larger |
| Category-specific testing | `ticket_type_*.csv` |
| Quality analysis | `quality_high_satisfaction.csv` / `quality_low_satisfaction.csv` |
| Non-technical users | Any file in `excel/` folder |

### Data Handling

1. **Always check for null values**:
   ```python
   df.isnull().sum()  # Check missing values
   ```

2. **Verify data types**:
   ```python
   df.dtypes  # Check column types
   ```

3. **Sample before processing large datasets**:
   ```python
   # Use smaller sample first
   df_sample = df.sample(n=100)
   # Test your code
   # Then process full dataset
   ```

4. **Use appropriate dataset size**:
   - Development: 50-100 rows
   - Testing: 100-500 rows
   - Production demo: 500-1000 rows
   - Performance testing: 1000+ rows

### Regenerating Datasets

To regenerate all subdatasets:

```bash
# Standard regeneration
python scripts/create_subdatasets.py

# With custom settings
python scripts/create_subdatasets.py \
  --input data/customer_support_tickets.csv \
  --output-dir data/subdatasets \
  --sizes 50,100,200,500,1000,2000
```

**Note**: Regeneration will overwrite existing files. The script uses a fixed random seed (42) for reproducibility.

---

## Metadata Reference

### Metadata File

`data/subdatasets/subdatasets_metadata.json` contains:

```json
{
  "source_file": "data/customer_support_tickets.csv",
  "total_tickets": 8469,
  "columns": [...],
  "subdatasets": [
    {
      "filename": "random_sample_100.csv",
      "description": "Random sample of 100 tickets",
      "size": 100,
      "method": "random_sample"
    },
    ...
  ]
}
```

### Methods

- `random_sample` - Random sampling
- `stratified_sample` - Stratified by ticket type
- `filter_by_ticket_type` - Filtered by ticket type
- `filter_by_priority` - Filtered by priority
- `filter_by_status` - Filtered by status
- `filter_by_product` - Filtered by product
- `filter_by_channel` - Filtered by channel
- `filter_by_quality` - Filtered by satisfaction rating
- `filter_by_date` - Filtered by time period
- `edge_case` - Special edge cases
- `excel_export` - Excel format version

---

## Troubleshooting

### Common Issues

1. **File Not Found**:
   - Check that subdatasets have been generated: `ls data/subdatasets/`
   - Run generation script: `python scripts/create_subdatasets.py`

2. **Encoding Issues**:
   - All files are UTF-8 encoded
   - Use `encoding='utf-8'` when reading: `pd.read_csv(file, encoding='utf-8')`

3. **Large File Size**:
   - Use smaller samples for development
   - Consider using stratified samples instead of full categories

4. **Missing Excel Files**:
   - Ensure `openpyxl` is installed: `pip install openpyxl`
   - Regenerate: `python scripts/create_subdatasets.py`

---

## Related Documentation

- [README.md](README.md) - Application overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [DATABASE_SCHEMA_REFERENCE.md](DATABASE_SCHEMA_REFERENCE.md) - Database structure
- [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md) - Evaluation methodology

---

## Updates and Maintenance

### Version History

- **v1.0** (2026-02-02): Initial dataset documentation
  - 43 CSV subdatasets
  - 10 Excel subdatasets
  - Automated generation script

### Future Enhancements

Planned improvements:
- Additional edge case datasets
- Multi-language ticket samples
- Synthetic data generation for rare categories
- JSON and Parquet format exports

---

For questions or issues related to datasets, please check the main [README.md](README.md) or open an issue on the project repository.
