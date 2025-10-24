"""
Add quantities to alternatives files so UI can calculate real total costs.
"""
import pandas as pd
from pathlib import Path


def add_quantities():
    """Add QUANTITY column to alternatives files."""
    data_dir = Path('/app/data/processed')
    
    # Load matched materials (which have quantities)
    matched_windows = pd.read_csv(data_dir / 'matched_windows.csv')
    matched_doors = pd.read_csv(data_dir / 'matched_doors.csv')
    matched_appliances = pd.read_csv(data_dir / 'matched_appliances.csv')
    
    # Create quantity lookup
    quantities = {}
    for df in [matched_windows, matched_doors, matched_appliances]:
        for _, row in df.iterrows():
            quantities[row['MATERIAL_ID']] = row['QUANTITY']
    
    # Add quantities to alternatives files
    for filename in ['window_alternatives_scored.csv', 'door_alternatives_scored.csv', 
                     'appliance_alternatives_scored.csv']:
        filepath = data_dir / filename
        df = pd.read_csv(filepath)
        
        # Add QUANTITY column
        df['QUANTITY'] = df['MATERIAL_ID'].map(quantities)
        
        # Calculate real total costs
        if 'ALT_COST_MAT' in df.columns:
            df['ALT_TOTAL_COST_MAT'] = df['ALT_COST_MAT'] * df['QUANTITY']
            df['ALT_TOTAL_COST_INST'] = df['ALT_COST_INST'] * df['QUANTITY']
        
        df['ALT_TOTAL_COST_TOTAL'] = df['ALT_COST_TOTAL'] * df['QUANTITY']
        df['ORIGINAL_TOTAL_COST'] = df['ORIGINAL_COST'] * df['QUANTITY']
        
        # Save
        df.to_csv(filepath, index=False)
        print(f'✅ Updated {filename}')
    
    print('\n✅ All alternatives files updated with quantities and total costs!')


if __name__ == '__main__':
    add_quantities()

