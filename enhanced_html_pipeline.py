import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

class EnhancedHTMLPipeline:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.dataset_name = self.file_path.stem
        self.output_dir = Path(f"{self.dataset_name}_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.raw_data = None
        self.cleaned_data = None
        self.cleaning_log = []
        
    def log_action(self, action):
        """Log cleaning actions"""
        self.cleaning_log.append(f"• {action}")
        print(f"Action: {action}")
        
    def load_data(self):
        """Auto-detect and load data from various formats"""
        try:
            file_ext = self.file_path.suffix.lower()
            
            if file_ext == '.csv':
                self.raw_data = pd.read_csv(self.file_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.raw_data = pd.read_excel(self.file_path)
            elif file_ext == '.json':
                self.raw_data = pd.read_json(self.file_path)
            elif file_ext == '.parquet':
                self.raw_data = pd.read_parquet(self.file_path)
            elif file_ext == '.tsv':
                self.raw_data = pd.read_csv(self.file_path, sep='\t')
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            print(f"Loaded {len(self.raw_data)} rows and {len(self.raw_data.columns)} columns")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def clean_data(self):
        """Comprehensive data cleaning with detailed logging"""
        self.cleaned_data = self.raw_data.copy()
        original_shape = self.raw_data.shape
        
        # 1. Standardize column names
        old_cols = list(self.cleaned_data.columns)
        import re
        self.cleaned_data.columns = [re.sub(r'[^a-zA-Z0-9_]', '', col.strip().lower().replace(' ', '_').replace('-', '_')) 
                                   for col in self.cleaned_data.columns]
        self.log_action(f"Standardized {len(old_cols)} column names")
        
        # 2. Handle missing values - only drop columns with >95% missing
        missing_threshold = 0.95
        cols_to_drop = []
        for col in self.cleaned_data.columns:
            missing_pct = self.cleaned_data[col].isnull().sum() / len(self.cleaned_data)
            if missing_pct > missing_threshold:
                cols_to_drop.append(col)
                self.log_action(f"Dropped column '{col}' ({missing_pct:.1%} missing)")
        
        if cols_to_drop:
            self.cleaned_data = self.cleaned_data.drop(columns=cols_to_drop)
        else:
            self.log_action("No columns dropped (all below 95% missing threshold)")
        
        # 3. Remove duplicates
        initial_rows = len(self.cleaned_data)
        self.cleaned_data = self.cleaned_data.drop_duplicates()
        duplicates_removed = initial_rows - len(self.cleaned_data)
        if duplicates_removed > 0:
            self.log_action(f"Removed {duplicates_removed} duplicate rows")
        else:
            self.log_action("No duplicate rows found")
        
        # 4. Handle remaining missing values
        missing_filled = 0
        for col in self.cleaned_data.columns:
            missing_count = self.cleaned_data[col].isnull().sum()
            if missing_count > 0:
                if self.cleaned_data[col].dtype in ['int64', 'float64']:
                    # Fill numeric with median
                    self.cleaned_data[col].fillna(self.cleaned_data[col].median(), inplace=True)
                    self.log_action(f"Filled {missing_count} missing values in '{col}' with median")
                else:
                    # Fill categorical with mode or 'Unknown'
                    mode_val = self.cleaned_data[col].mode()
                    fill_val = mode_val[0] if len(mode_val) > 0 else 'Unknown'
                    self.cleaned_data[col].fillna(fill_val, inplace=True)
                    self.log_action(f"Filled {missing_count} missing values in '{col}' with mode/Unknown")
                missing_filled += missing_count
        
        if missing_filled == 0:
            self.log_action("No missing values to fill")
        
        # 5. Handle outliers for numeric columns
        numeric_cols = self.cleaned_data.select_dtypes(include=[np.number]).columns
        total_outliers = 0
        for col in numeric_cols:
            Q1 = self.cleaned_data[col].quantile(0.25)
            Q3 = self.cleaned_data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers instead of removing
            outliers = ((self.cleaned_data[col] < lower_bound) | 
                       (self.cleaned_data[col] > upper_bound)).sum()
            if outliers > 0:
                self.cleaned_data[col] = np.clip(self.cleaned_data[col], lower_bound, upper_bound)
                self.log_action(f"Capped {outliers} outliers in '{col}'")
                total_outliers += outliers
        
        if total_outliers == 0:
            self.log_action("No outliers detected in numeric columns")
        
        final_shape = self.cleaned_data.shape
        self.log_action(f"Cleaning complete: {original_shape} -> {final_shape}")
    
    def analyze_data(self, data, prefix=""):
        """Generate comprehensive analysis for given dataset"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        analysis = {
            'basic_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                'numeric_columns': len(numeric_cols),
                'categorical_columns': len(categorical_cols),
                'total_missing': data.isnull().sum().sum()
            },
            'missing_data': {},
            'data_types': {},
            'numeric_summary': {},
            'categorical_summary': {},
            'outlier_analysis': {}
        }
        
        # Missing data analysis
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            analysis['missing_data'][col] = {
                'count': missing_count,
                'percentage': missing_pct
            }
        
        # Data types
        for col in data.columns:
            analysis['data_types'][col] = str(data[col].dtype)
        
        # Numeric analysis
        for col in numeric_cols:
            analysis['numeric_summary'][col] = {
                'mean': round(data[col].mean(), 3) if not pd.isna(data[col].mean()) else 0,
                'median': round(data[col].median(), 3) if not pd.isna(data[col].median()) else 0,
                'std': round(data[col].std(), 3) if not pd.isna(data[col].std()) else 0,
                'min': data[col].min(),
                'max': data[col].max(),
                'unique_count': data[col].nunique(),
                'zeros': (data[col] == 0).sum()
            }
        
        # Categorical analysis
        for col in categorical_cols:
            top_values = data[col].value_counts().head(3)
            analysis['categorical_summary'][col] = {
                'unique_count': data[col].nunique(),
                'top_values': top_values.to_dict(),
                'most_frequent': data[col].mode().iloc[0] if len(data[col].mode()) > 0 else 'N/A'
            }
        
        # Outlier analysis for numeric columns
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
            
            analysis['outlier_analysis'][col] = {
                'count': outliers,
                'percentage': round((outliers / len(data)) * 100, 2)
            }
        
        return analysis
    
    def create_html_dashboard(self):
        """Create comprehensive HTML dashboard with before/after analysis"""
        # Generate analyses
        raw_analysis = self.analyze_data(self.raw_data, "Raw")
        cleaned_analysis = self.analyze_data(self.cleaned_data, "Cleaned")
        
        # Calculate improvements
        rows_change = cleaned_analysis['basic_info']['rows'] - raw_analysis['basic_info']['rows']
        cols_change = cleaned_analysis['basic_info']['columns'] - raw_analysis['basic_info']['columns']
        missing_improvement = raw_analysis['basic_info']['total_missing'] - cleaned_analysis['basic_info']['total_missing']
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Data Analysis Dashboard - {self.dataset_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .section {{ background: white; padding: 25px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #4a5568; margin-bottom: 20px; font-size: 1.8em; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .comparison {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 20px; align-items: center; }}
        .vs {{ text-align: center; font-size: 2em; color: #667eea; font-weight: bold; }}
        .card {{ background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .card.before {{ border-left-color: #e53e3e; }}
        .card.after {{ border-left-color: #38a169; }}
        .card h3 {{ color: #2d3748; margin-bottom: 15px; }}
        .stat {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
        .stat-label {{ font-weight: 600; color: #4a5568; }}
        .stat-value {{ color: #667eea; font-weight: bold; }}
        .improvement {{ color: #38a169; font-weight: bold; }}
        .degradation {{ color: #e53e3e; font-weight: bold; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        .table th {{ background: #edf2f7; font-weight: 600; color: #4a5568; }}
        .table tr:hover {{ background: #f7fafc; }}
        .cleaning-log {{ background: #f0fff4; border: 1px solid #9ae6b4; border-radius: 8px; padding: 15px; margin-top: 15px; }}
        .cleaning-log h4 {{ color: #2f855a; margin-bottom: 10px; }}
        .cleaning-log ul {{ list-style: none; }}
        .cleaning-log li {{ margin-bottom: 5px; color: #2d3748; }}
        .tabs {{ display: flex; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: #edf2f7; border: none; cursor: pointer; border-radius: 5px 5px 0 0; margin-right: 5px; }}
        .tab.active {{ background: #667eea; color: white; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Enhanced Data Analysis Dashboard</h1>
            <p>Dataset: {self.dataset_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>🔄 Before vs After Cleaning</h2>
            <div class="comparison">
                <div class="card before">
                    <h3>📥 Before Cleaning</h3>
                    <div class="stat"><span class="stat-label">Rows:</span><span class="stat-value">{raw_analysis['basic_info']['rows']:,}</span></div>
                    <div class="stat"><span class="stat-label">Columns:</span><span class="stat-value">{raw_analysis['basic_info']['columns']}</span></div>
                    <div class="stat"><span class="stat-label">Missing Values:</span><span class="stat-value">{raw_analysis['basic_info']['total_missing']:,}</span></div>
                    <div class="stat"><span class="stat-label">Memory Usage:</span><span class="stat-value">{raw_analysis['basic_info']['memory_usage']}</span></div>
                </div>
                <div class="vs">→</div>
                <div class="card after">
                    <h3>✅ After Cleaning</h3>
                    <div class="stat"><span class="stat-label">Rows:</span><span class="stat-value">{cleaned_analysis['basic_info']['rows']:,}</span></div>
                    <div class="stat"><span class="stat-label">Columns:</span><span class="stat-value">{cleaned_analysis['basic_info']['columns']}</span></div>
                    <div class="stat"><span class="stat-label">Missing Values:</span><span class="stat-value">{cleaned_analysis['basic_info']['total_missing']:,}</span></div>
                    <div class="stat"><span class="stat-label">Memory Usage:</span><span class="stat-value">{cleaned_analysis['basic_info']['memory_usage']}</span></div>
                </div>
            </div>
            
            <div class="cleaning-log">
                <h4>🔧 Cleaning Actions Performed:</h4>
                <ul>
                    {''.join(f'<li>{action}</li>' for action in self.cleaning_log)}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Improvement Summary</h2>
            <div class="grid">
                <div class="card">
                    <h3>📊 Data Changes</h3>
                    <div class="stat"><span class="stat-label">Rows Change:</span><span class="stat-value {'improvement' if rows_change >= 0 else 'degradation'}">{rows_change:+,}</span></div>
                    <div class="stat"><span class="stat-label">Columns Change:</span><span class="stat-value {'improvement' if cols_change >= 0 else 'degradation'}">{cols_change:+}</span></div>
                    <div class="stat"><span class="stat-label">Missing Values Removed:</span><span class="stat-value improvement">{missing_improvement:,}</span></div>
                </div>
                <div class="card">
                    <h3>🎯 Quality Metrics</h3>
                    <div class="stat"><span class="stat-label">Data Completeness:</span><span class="stat-value">{((1 - cleaned_analysis['basic_info']['total_missing'] / (cleaned_analysis['basic_info']['rows'] * cleaned_analysis['basic_info']['columns'])) * 100):.1f}%</span></div>
                    <div class="stat"><span class="stat-label">Numeric Columns:</span><span class="stat-value">{cleaned_analysis['basic_info']['numeric_columns']}</span></div>
                    <div class="stat"><span class="stat-label">Categorical Columns:</span><span class="stat-value">{cleaned_analysis['basic_info']['categorical_columns']}</span></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Detailed Analysis</h2>
            <div class="tabs">
                <button class="tab active" onclick="showTab('before')">Before Cleaning</button>
                <button class="tab" onclick="showTab('after')">After Cleaning</button>
                <button class="tab" onclick="showTab('comparison')">Comparison</button>
            </div>
            
            <div id="before" class="tab-content active">
                <h3>📥 Raw Data Analysis</h3>
                {self.generate_analysis_table(raw_analysis)}
            </div>
            
            <div id="after" class="tab-content">
                <h3>✅ Cleaned Data Analysis</h3>
                {self.generate_analysis_table(cleaned_analysis)}
            </div>
            
            <div id="comparison" class="tab-content">
                <h3>🔍 Before vs After Comparison</h3>
                {self.generate_comparison_table(raw_analysis, cleaned_analysis)}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
        """
        
        return html_content
    
    def generate_analysis_table(self, analysis):
        """Generate HTML table for analysis data"""
        html = f"""
        <table class="table">
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Missing</th>
                    <th>Unique</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for col in analysis['data_types'].keys():
            missing_info = analysis['missing_data'][col]
            col_type = analysis['data_types'][col]
            
            if col in analysis['numeric_summary']:
                details = f"Mean: {analysis['numeric_summary'][col]['mean']}, Std: {analysis['numeric_summary'][col]['std']}"
                unique_count = analysis['numeric_summary'][col]['unique_count']
            elif col in analysis['categorical_summary']:
                details = f"Most frequent: {analysis['categorical_summary'][col]['most_frequent']}"
                unique_count = analysis['categorical_summary'][col]['unique_count']
            else:
                details = "N/A"
                unique_count = "N/A"
            
            html += f"""
                <tr>
                    <td>{col}</td>
                    <td>{col_type}</td>
                    <td>{missing_info['count']} ({missing_info['percentage']:.1f}%)</td>
                    <td>{unique_count}</td>
                    <td>{details}</td>
                </tr>
            """
        
        html += "</tbody></table>"
        return html
    
    def generate_comparison_table(self, raw_analysis, cleaned_analysis):
        """Generate comparison table between raw and cleaned data"""
        html = f"""
        <table class="table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Before</th>
                    <th>After</th>
                    <th>Change</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Total Rows</td>
                    <td>{raw_analysis['basic_info']['rows']:,}</td>
                    <td>{cleaned_analysis['basic_info']['rows']:,}</td>
                    <td class="{'improvement' if cleaned_analysis['basic_info']['rows'] >= raw_analysis['basic_info']['rows'] else 'degradation'}">{cleaned_analysis['basic_info']['rows'] - raw_analysis['basic_info']['rows']:+,}</td>
                </tr>
                <tr>
                    <td>Total Columns</td>
                    <td>{raw_analysis['basic_info']['columns']}</td>
                    <td>{cleaned_analysis['basic_info']['columns']}</td>
                    <td class="{'improvement' if cleaned_analysis['basic_info']['columns'] >= raw_analysis['basic_info']['columns'] else 'degradation'}">{cleaned_analysis['basic_info']['columns'] - raw_analysis['basic_info']['columns']:+}</td>
                </tr>
                <tr>
                    <td>Missing Values</td>
                    <td>{raw_analysis['basic_info']['total_missing']:,}</td>
                    <td>{cleaned_analysis['basic_info']['total_missing']:,}</td>
                    <td class="improvement">{raw_analysis['basic_info']['total_missing'] - cleaned_analysis['basic_info']['total_missing']:+,}</td>
                </tr>
                <tr>
                    <td>Numeric Columns</td>
                    <td>{raw_analysis['basic_info']['numeric_columns']}</td>
                    <td>{cleaned_analysis['basic_info']['numeric_columns']}</td>
                    <td class="{'improvement' if cleaned_analysis['basic_info']['numeric_columns'] >= raw_analysis['basic_info']['numeric_columns'] else 'degradation'}">{cleaned_analysis['basic_info']['numeric_columns'] - raw_analysis['basic_info']['numeric_columns']:+}</td>
                </tr>
                <tr>
                    <td>Categorical Columns</td>
                    <td>{raw_analysis['basic_info']['categorical_columns']}</td>
                    <td>{cleaned_analysis['basic_info']['categorical_columns']}</td>
                    <td class="{'improvement' if cleaned_analysis['basic_info']['categorical_columns'] >= raw_analysis['basic_info']['categorical_columns'] else 'degradation'}">{cleaned_analysis['basic_info']['categorical_columns'] - raw_analysis['basic_info']['categorical_columns']:+}</td>
                </tr>
            </tbody>
        </table>
        """
        return html
    
    def run(self):
        """Run the complete pipeline"""
        print("\n" + "=" * 50)
        print("DATA CLEANING STARTED")
        print("=" * 50)
        
        # Load data
        if not self.load_data():
            return False
        
        # Clean data
        print("\nCleaning data...")
        self.clean_data()
        
        # Create HTML dashboard
        print("\nCreating enhanced HTML dashboard...")
        html_content = self.create_html_dashboard()
        
        # Save outputs
        dashboard_path = self.output_dir / "enhanced_dashboard.html"
        cleaned_data_csv = self.output_dir / "cleaned_data.csv"
        cleaned_data_excel = self.output_dir / "cleaned_data.xlsx"
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as both CSV and Excel
        self.cleaned_data.to_csv(cleaned_data_csv, index=False)
        self.cleaned_data.to_excel(cleaned_data_excel, index=False)
        
        print("\n" + "=" * 50)
        print("DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Enhanced Dashboard: {dashboard_path.absolute()}")
        print(f"Cleaned Data (CSV): {cleaned_data_csv.absolute()}")
        print(f"Cleaned Data (Excel): {cleaned_data_excel.absolute()}")
        print("Open the HTML file in your browser to view the interactive dashboard!")
        
        return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python enhanced_html_pipeline.py <dataset_file>")
        print("Example: python enhanced_html_pipeline.py flight.csv")
    else:
        pipeline = EnhancedHTMLPipeline(sys.argv[1])
        pipeline.run()