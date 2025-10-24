"""
Data loader module for loading apartment, door, window, appliance, and RSMeans cost data.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple


class DataLoader:
    """Loads all project data files."""
    
    def __init__(self, base_path: str = "/Users/weizhang/git/VEAgent"):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.rsmeans_path = self.base_path / "rsmeans"
        
    def load_apartment_specs(self) -> pd.DataFrame:
        """Load apartment specifications."""
        df = pd.read_csv(self.data_path / "apartment_specs.csv")
        # Filter units with Total Units > 0
        df = df[df['Total Units'] > 0].copy()
        return df
    
    def load_door_schedule(self) -> pd.DataFrame:
        """Load door schedule (specifications)."""
        df = pd.read_csv(
            self.data_path / "schedule" / "schedule_unit_doors.tsv",
            sep="\t"
        )
        return df
    
    def load_door_counts(self) -> pd.DataFrame:
        """Load door counts by unit."""
        df = pd.read_csv(
            self.data_path / "counts" / "count_unit_doors.tsv",
            sep="\t"
        )
        return df
    
    def load_window_schedule(self) -> pd.DataFrame:
        """Load window schedule (specifications)."""
        df = pd.read_csv(
            self.data_path / "schedule" / "schedule_window.tsv",
            sep="\t"
        )
        return df
    
    def load_window_counts(self) -> pd.DataFrame:
        """Load window counts by facade."""
        df = pd.read_csv(
            self.data_path / "counts" / "count_windows.tsv",
            sep="\t"
        )
        return df
    
    def load_appliance_counts(self) -> pd.DataFrame:
        """Load appliance counts."""
        df = pd.read_csv(
            self.data_path / "counts" / "count_appliance.tsv",
            sep="\t"
        )
        return df
    
    def load_rsmeans_windows(self) -> pd.DataFrame:
        """Load RSMeans windows cost data."""
        df = pd.read_csv(
            self.rsmeans_path / "rsmeams_B2020_ext_windows_unit_cost.tsv",
            sep="\t"
        )
        # Clean numeric columns
        for col in ['MAT', 'INST', 'TOTAL']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').replace('', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def load_rsmeans_ext_doors(self) -> pd.DataFrame:
        """Load RSMeans exterior doors cost data."""
        df = pd.read_csv(
            self.rsmeans_path / "rsmeans_B2030_110_ext_doors_unit_cost.tsv",
            sep="\t"
        )
        # Clean numeric columns
        for col in ['MAT.', 'INST.', 'TOTAL']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').replace('', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def load_rsmeans_int_doors(self) -> pd.DataFrame:
        """Load RSMeans interior doors cost data."""
        df = pd.read_csv(
            self.rsmeans_path / "rsmenas_C1020_102_int_doors_unit_cost.tsv",
            sep="\t"
        )
        # Clean numeric columns
        for col in ['MAT.', 'INST.', 'TOTAL']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').replace('', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def load_rsmeans_appliances(self) -> pd.DataFrame:
        """Load RSMeans appliances cost data."""
        # The appliances file has an unusual format - read as raw lines
        with open(self.rsmeans_path / "rsmeams_appliances_unit_cost.tsv", 'r') as f:
            lines = f.readlines()
        
        # Parse manually to handle inconsistent columns
        data = []
        for line in lines[3:]:  # Skip headers
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[0].strip():
                # Left column set
                data.append({
                    'Description': parts[0].strip(),
                    'Unit': parts[1].strip() if len(parts) > 1 else '',
                    'Cost': parts[2].strip() if len(parts) > 2 else ''
                })
            if len(parts) >= 6 and parts[3].strip():
                # Right column set
                data.append({
                    'Description': parts[3].strip(),
                    'Unit': parts[4].strip() if len(parts) > 4 else '',
                    'Cost': parts[5].strip() if len(parts) > 5 else ''
                })
        
        df = pd.DataFrame(data)
        # Filter out empty rows
        df = df[df['Description'].str.len() > 0].copy()
        return df
    
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all data at once."""
        return {
            'apartment_specs': self.load_apartment_specs(),
            'door_schedule': self.load_door_schedule(),
            'door_counts': self.load_door_counts(),
            'window_schedule': self.load_window_schedule(),
            'window_counts': self.load_window_counts(),
            'appliance_counts': self.load_appliance_counts(),
            'rsmeans_windows': self.load_rsmeans_windows(),
            'rsmeans_ext_doors': self.load_rsmeans_ext_doors(),
            'rsmeans_int_doors': self.load_rsmeans_int_doors(),
            'rsmeans_appliances': self.load_rsmeans_appliances(),
        }


def main():
    """Test the data loader."""
    loader = DataLoader()
    data = loader.load_all()
    
    print("Data loaded successfully!")
    print("\n" + "="*60)
    for name, df in data.items():
        print(f"\n{name}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)[:5]}...")
        if len(df) > 0:
            print(f"  Sample:\n{df.head(2)}")
    

if __name__ == "__main__":
    main()

