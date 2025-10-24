"""
Add better descriptions to alternatives files by merging with schedule data.
"""
import pandas as pd
from pathlib import Path


def enhance_descriptions():
    """Add full descriptions from schedule files."""
    data_dir = Path('/Users/weizhang/git/VEAgent/data')
    processed_dir = data_dir / 'processed'
    
    # Load schedules
    window_schedule = pd.read_csv(data_dir / 'schedule' / 'schedule_window.tsv', sep='\t')
    door_schedule = pd.read_csv(data_dir / 'schedule' / 'schedule_unit_doors.tsv', sep='\t')
    
    # Create description mappings
    window_descriptions = {}
    for _, row in window_schedule.iterrows():
        mark = row['MARK']
        material = row.get('MATERIAL', 'V')
        material_map = {'V': 'Vinyl', 'W': 'Wood', 'A': 'Aluminum'}
        material_name = material_map.get(material, material)
        
        width = row.get('UNIT SIZE WIDTH', '')
        height = row.get('UNIT SIZE HEIGHT', '')
        style = row.get('STYLE', '')
        
        desc = f"{mark} - {material_name} {style} ({width} x {height})"
        window_descriptions[mark] = desc
    
    door_descriptions = {}
    for _, row in door_schedule.iterrows():
        mark = str(row['MARK'])
        location = row.get('LOCATION', '')
        material = row.get('MATERIAL', '')
        width = row.get('WIDTH', '')
        height = row.get('HEIGHT', '')
        door_type = row.get('TYPE', '')
        
        desc = f"Door {mark} - {location} ({material}, {width} x {height}, Type {door_type})"
        door_descriptions[mark] = desc
    
    # Update windows
    windows = pd.read_csv(processed_dir / 'window_alternatives_scored.csv')
    windows['MATERIAL_DESC'] = windows['MATERIAL_ID'].map(window_descriptions)
    windows.to_csv(processed_dir / 'window_alternatives_scored.csv', index=False)
    print(f'✅ Updated window descriptions')
    
    # Update doors
    doors = pd.read_csv(processed_dir / 'door_alternatives_scored.csv')
    doors['MATERIAL_DESC'] = doors['MATERIAL_ID'].apply(lambda x: door_descriptions.get(str(x), f'Door {x}'))
    doors.to_csv(processed_dir / 'door_alternatives_scored.csv', index=False)
    print(f'✅ Updated door descriptions')
    
    print('\n✅ All descriptions enhanced!')


if __name__ == '__main__':
    enhance_descriptions()


