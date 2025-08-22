# Data Cleaning Pipeline

Automated data cleaning and analysis pipeline that works on any tabular dataset with interactive HTML dashboard output.

## 🚀 Quick Start

### 1. **Clone the Repository**
```bash
git clone https://github.com/logesh4v/dataclean_final.git
cd dataclean_final
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Run the Pipeline**
```bash
# Basic usage
python run_pipeline.py your_data.csv

# With sample data
python run_pipeline.py "sample_data/Car check.xlsx"
python run_pipeline.py "sample_data/flight.csv"
```

## 📁 **Supported File Formats**
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`) 
- JSON (`.json`)
- Parquet (`.parquet`)
- TSV (`.tsv`)

## 📊 **What You Get**
After running, check the `{dataset_name}_output/` folder:
- `enhanced_dashboard.html` - Interactive HTML report
- `cleaned_data.csv` - Cleaned dataset

## 💡 **Examples**
```bash
# Process car data
python run_pipeline.py "sample_data/Car data final.xlsx"

# Process flight data  
python run_pipeline.py "sample_data/flight.csv"

# Process your own data
python run_pipeline.py "path/to/your/data.csv"
```

## 🌐 **View Results**
Open the generated HTML file in your browser to see:
- Before vs After comparison
- Data quality metrics
- Cleaning actions performed
- Interactive analysis tabs

## ✨ **Features**
- **Universal File Support** - Works with any tabular data format
- **Smart Data Cleaning** - Preserves important columns (95% missing threshold)
- **Interactive Dashboard** - Beautiful HTML reports with before/after analysis
- **Outlier Management** - IQR-based outlier detection and capping
- **Missing Value Handling** - Intelligent imputation strategies
- **Duplicate Removal** - Automatic duplicate detection and removal

## 🔧 **Pipeline Logic**
1. **Data Loading** - Auto-detects file format and loads data
2. **Column Standardization** - Cleans and standardizes column names
3. **Missing Value Handling** - Smart imputation based on data type
4. **Duplicate Removal** - Removes exact duplicate rows
5. **Outlier Detection** - IQR-based outlier capping
6. **Report Generation** - Creates interactive HTML dashboard

## 📈 **Sample Datasets Included**
- `Car check.xlsx` - Car maintenance data (7×3)
- `Car data final.xlsx` - Car service records (421×6)
- `flight.csv` - Flight customer data (62,988×23)

## 🛠 **Requirements**
- Python 3.7+
- pandas >= 1.3.0
- numpy >= 1.21.0
- openpyxl >= 3.0.0

## 📝 **Output Structure**
```
{dataset_name}_output/
├── enhanced_dashboard.html    # Interactive HTML report
└── cleaned_data.csv          # Cleaned dataset
```

## 🎯 **Use Cases**
- Data preprocessing for machine learning
- Exploratory data analysis (EDA)
- Data quality assessment
- Automated data cleaning workflows
- Dataset preparation for analysis

**That's it!** The pipeline automatically handles everything else.