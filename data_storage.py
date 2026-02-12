import pandas as pd
import os
from datetime import datetime
import json

class DataStorage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_to_csv(self, df, filename):
        """Save DataFrame to CSV file"""
        filepath = os.path.join(self.data_dir, f"{filename}.csv")
        df.to_csv(filepath)
        return filepath
    
    def save_to_parquet(self, df, filename):
        """Save DataFrame to Parquet file"""
        try:
            import pyarrow
            filepath = os.path.join(self.data_dir, f"{filename}.parquet")
            df.to_parquet(filepath)
            return filepath
        except ImportError:
            print("PyArrow not installed. Using CSV format instead.")
            return self.save_to_csv(df, filename)
    
    def load_from_csv(self, filename):
        """Load DataFrame from CSV file"""
        filepath = os.path.join(self.data_dir, f"{filename}.csv")
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        return None
    
    def load_from_parquet(self, filename):
        """Load DataFrame from Parquet file"""
        try:
            import pyarrow
            filepath = os.path.join(self.data_dir, f"{filename}.parquet")
            if os.path.exists(filepath):
                return pd.read_parquet(filepath)
        except ImportError:
            print("PyArrow not installed. Trying CSV format.")
            return self.load_from_csv(filename)
        return None
    
    def save_metadata(self, metadata, filename):
        """Save metadata to JSON file"""
        filepath = os.path.join(self.data_dir, f"{filename}_metadata.json")
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def load_metadata(self, filename):
        """Load metadata from JSON file"""
        filepath = os.path.join(self.data_dir, f"{filename}_metadata.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def get_latest_data_files(self):
        """Get list of all data files"""
        files = []
        for file in os.listdir(self.data_dir):
            if file.endswith(('.csv', '.parquet')):
                files.append(file)
        return files
    
    def cleanup_old_data(self, days_old=7):
        """Clean up data files older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        for file in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, file)
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                print(f"Removed old file: {file}")
