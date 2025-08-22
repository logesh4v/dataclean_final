# Data Cleaning Pipeline

This is an automated data cleaning tool that processes tabular datasets and generates interactive HTML reports showing before and after comparisons.

## Getting Started

### Installation

First, clone this repository to your local machine:

```bash
git clone https://github.com/logesh4v/dataclean_final.git
cd dataclean_final
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Basic Usage

Run the pipeline on your dataset:

```bash
python run_pipeline.py your_data.csv
```

Try it with the included sample data:

```bash
python run_pipeline.py "sample_data/Car check.xlsx"
python run_pipeline.py "sample_data/flight.csv"
```

## Supported File Types

The pipeline works with these file formats:
- CSV files (.csv)
- Excel files (.xlsx, .xls)
- JSON files (.json)
- Parquet files (.parquet)
- Tab-separated files (.tsv)

## Output

After processing your data, you'll find two files in a new folder named `{dataset_name}_output/`:
- `enhanced_dashboard.html` - An interactive web report
- `cleaned_data.csv` - Your cleaned dataset

## Examples

Process different types of data:

```bash
# Car maintenance records
python run_pipeline.py "sample_data/Car data final.xlsx"

# Flight customer data
python run_pipeline.py "sample_data/flight.csv"

# Your own dataset
python run_pipeline.py "path/to/your/data.csv"
```

## What the Dashboard Shows

Open the HTML file in any web browser to see:
- Side-by-side comparison of your data before and after cleaning
- Statistics about data quality improvements
- Details of all cleaning actions performed
- Interactive tabs for exploring the analysis

## Key Features

**File Compatibility**: Handles multiple data formats automatically

**Data Preservation**: Only removes columns with more than 95% missing values to avoid losing important information

**Visual Reports**: Creates professional HTML dashboards with interactive elements

**Outlier Handling**: Uses statistical methods (IQR) to detect and cap extreme values rather than deleting them

**Missing Data**: Fills gaps using appropriate methods - median for numbers, most common value for categories

**Duplicate Detection**: Finds and removes identical rows automatically

## How It Works

The cleaning process follows these steps:

1. **Load Data**: Automatically detects your file format and imports the data
2. **Clean Column Names**: Standardizes column names to work better with analysis tools
3. **Handle Missing Values**: Decides whether to fill gaps or remove columns based on how much data is missing
4. **Remove Duplicates**: Finds and eliminates identical rows
5. **Manage Outliers**: Identifies extreme values and caps them at reasonable limits
6. **Generate Report**: Creates an interactive HTML dashboard showing all changes

## Sample Data

Three example datasets are included:
- `Car check.xlsx` - Small car maintenance dataset (7 rows, 3 columns)
- `Car data final.xlsx` - Car service records (421 rows, 6 columns)
- `flight.csv` - Large airline customer dataset (62,988 rows, 23 columns)

## System Requirements

- Python 3.7 or newer
- pandas 1.3.0 or newer
- numpy 1.21.0 or newer
- openpyxl 3.0.0 or newer (for Excel file support)

## File Structure After Running

```
{your_dataset_name}_output/
├── enhanced_dashboard.html    # Interactive web report
└── cleaned_data.csv          # Your cleaned data
```

## Common Use Cases

- Preparing data for machine learning projects
- Cleaning datasets for analysis and visualization
- Quality checking data before important decisions
- Automating repetitive data preparation tasks
- Getting quick insights into dataset problems

The tool handles the technical details automatically, so you can focus on analyzing your clean data.