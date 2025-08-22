#!/usr/bin/env python3
"""
Quick runner script for the automated data pipeline
Usage: python run_pipeline.py <dataset_file>
"""

from enhanced_html_pipeline import EnhancedHTMLPipeline
import sys
import os

def run_on_file(file_path):
    """Run pipeline on a specific file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    print(f"Processing: {file_path}")
    pipeline = EnhancedHTMLPipeline(file_path)
    return pipeline.run()

def main():
    if len(sys.argv) < 2:
        print("Enhanced Data Science Pipeline")
        print("=" * 50)
        print("Usage: python run_pipeline.py <dataset_file>")
        print("\nSupported formats:")
        print("  - CSV (.csv)")
        print("  - Excel (.xlsx, .xls)")
        print("  - JSON (.json)")
        print("  - Parquet (.parquet)")
        print("  - TSV (.tsv)")
        print("\nExamples:")
        print("  python run_pipeline.py flight.csv")
        print("  python run_pipeline.py \"Car data final.xlsx\"")
        print("  python run_pipeline.py user_data.json")
        print("\nFeatures:")
        print("  - Before/After cleaning analysis")
        print("  - Interactive HTML dashboard")
        print("  - Comprehensive data quality report")
        print("  - Smart missing value handling")
        print("  - Outlier detection and capping")
        return
    
    file_path = sys.argv[1]
    success = run_on_file(file_path)
    
    if success:
        print("\nSuccess! Check the output folder for results.")
    else:
        print("\nPipeline execution failed.")

if __name__ == "__main__":
    main()