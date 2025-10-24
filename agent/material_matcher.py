"""
Material matcher module - matches project materials to RSMeans cost data.
Finds the best match for each window, door, and appliance based on specifications.
"""
import pandas as pd
import re
from typing import Dict, Optional, Tuple


def parse_dimension(dim_str: str) -> Tuple[float, float]:
    """Parse dimension string like '5\'-0"' or '8'-0"' to inches."""
    if not dim_str or pd.isna(dim_str):
        return 0, 0
    
    # Remove quotes and clean
    dim_str = str(dim_str).strip().replace('"', '').replace("'", "-")
    
    # Match patterns like 5-0, 5'-0", 8'-0" etc
    parts = re.findall(r'(\d+)-(\d+)', dim_str)
    if parts:
        feet, inches = map(int, parts[0])
        return feet, inches
    
    # Try just feet
    match = re.search(r'(\d+)', dim_str)
    if match:
        feet = int(match.group(1))
        return feet, 0
    
    return 0, 0


def dim_to_inches(feet: float, inches: float) -> float:
    """Convert feet and inches to total inches."""
    return feet * 12 + inches


def dim_to_sqft(width_str: str, height_str: str) -> float:
    """Calculate area in square feet from dimension strings."""
    w_ft, w_in = parse_dimension(width_str)
    h_ft, h_in = parse_dimension(height_str)
    
    width_inches = dim_to_inches(w_ft, w_in)
    height_inches = dim_to_inches(h_ft, h_in)
    
    return (width_inches * height_inches) / 144.0  # Convert to sq ft


class MaterialMatcher:
    """Matches project materials to RSMeans cost data."""
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data
        
    def match_windows(self) -> pd.DataFrame:
        """Match each window type to RSMeans cost data."""
        window_schedule = self.data['window_schedule']
        window_counts = self.data['window_counts']
        rsmeans_windows = self.data['rsmeans_windows']
        
        results = []
        
        for _, window in window_schedule.iterrows():
            mark = window['MARK']
            
            # Get total count for this window
            if mark in window_counts['MARK'].values:
                count_row = window_counts[window_counts['MARK'] == mark].iloc[0]
                # Sum all facade counts
                total_count = sum([
                    count_row.get(col, 0) 
                    for col in ['North-outside', 'South-outside', 'West-outside', 
                               'East-outside', 'North-inside', 'South-inside', 
                               'West-inside', 'East-inside']
                    if col in count_row and not pd.isna(count_row[col])
                ])
            else:
                total_count = 0
            
            # Skip if no windows of this type
            if total_count == 0:
                continue
            
            # Calculate window area
            width_str = window.get('UNIT SIZE WIDTH', '')
            height_str = window.get('UNIT SIZE HEIGHT', '')
            window_area = dim_to_sqft(width_str, height_str)
            
            # Get window style and material
            style = str(window.get('STYLE', '')).lower()
            material = str(window.get('MATERIAL', 'V')).upper()  # Default to V (vinyl)
            
            # Find best match in RSMeans
            best_match = self._find_best_window_match(
                window_area, style, material, rsmeans_windows
            )
            
            if best_match is not None:
                results.append({
                    'MATERIAL_ID': mark,
                    'MATERIAL_TYPE': 'Window',
                    'DESCRIPTION': window.get('STYLE', ''),
                    'WIDTH': width_str,
                    'HEIGHT': height_str,
                    'AREA_SQFT': window_area,
                    'QUANTITY': total_count,
                    'RSMEANS_CODE': best_match['CODE'],
                    'RSMEANS_DESC': f"{best_match['MATERIAL']} {best_match['TYPE']} {best_match['SIZE']}",
                    'UNIT_COST_MAT': best_match['MAT'],
                    'UNIT_COST_INST': best_match['INST'],
                    'UNIT_COST_TOTAL': best_match['TOTAL'],
                    'TOTAL_COST_MAT': best_match['MAT'] * total_count,
                    'TOTAL_COST_INST': best_match['INST'] * total_count,
                    'TOTAL_COST': best_match['TOTAL'] * total_count,
                })
        
        return pd.DataFrame(results)
    
    def _find_best_window_match(self, target_area: float, style: str, 
                                  material: str, rsmeans: pd.DataFrame) -> Optional[Dict]:
        """Find the best matching window in RSMeans data."""
        # Filter by material type (wood, vinyl, etc.)
        material_map = {'V': 'Vinyl', 'W': 'Wood', 'A': 'Alum'}
        target_material = material_map.get(material, 'Vinyl')
        
        candidates = rsmeans[
            rsmeans['MATERIAL'].str.contains(target_material, case=False, na=False)
        ].copy()
        
        # If no material match, use all
        if len(candidates) == 0:
            candidates = rsmeans.copy()
        
        # Filter by style if possible (casement, sliding, etc.)
        style_keywords = ['casement', 'sliding', 'fixed', 'picture', 'awning', 'double hung']
        matched_style = None
        for keyword in style_keywords:
            if keyword in style:
                matched_style = keyword
                break
        
        if matched_style:
            style_candidates = candidates[
                candidates['TYPE'].str.contains(matched_style, case=False, na=False)
            ]
            if len(style_candidates) > 0:
                candidates = style_candidates
        
        # Calculate area for each candidate and find closest match
        candidates['area'] = candidates['SIZE'].apply(
            lambda x: self._parse_window_size(str(x))
        )
        
        # Find closest area match
        candidates['area_diff'] = abs(candidates['area'] - target_area)
        best_idx = candidates['area_diff'].idxmin()
        
        if pd.notna(best_idx):
            return candidates.loc[best_idx].to_dict()
        
        # Fallback: return first available
        if len(rsmeans) > 0:
            return rsmeans.iloc[0].to_dict()
        
        return None
    
    def _parse_window_size(self, size_str: str) -> float:
        """Parse window size string to square feet."""
        # Try to extract dimensions like "4'-6" x 4'-6""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', size_str)
        if len(matches) >= 2:
            w_ft, w_in = map(int, matches[0])
            h_ft, h_in = map(int, matches[1])
            width_inches = w_ft * 12 + w_in
            height_inches = h_ft * 12 + h_in
            return (width_inches * height_inches) / 144.0
        return 20.0  # Default area
    
    def match_doors(self) -> pd.DataFrame:
        """Match each door type to RSMeans cost data."""
        door_schedule = self.data['door_schedule']
        door_counts = self.data['door_counts']
        apartment_specs = self.data['apartment_specs']
        rsmeans_ext = self.data['rsmeans_ext_doors']
        rsmeans_int = self.data['rsmeans_int_doors']
        
        results = []
        
        for _, door in door_schedule.iterrows():
            mark = str(door['MARK'])
            
            # Calculate total count for this door across all units
            total_count = self._calculate_door_count(
                mark, door_counts, apartment_specs
            )
            
            if total_count == 0:
                continue
            
            # Determine if exterior or interior
            location = str(door.get('LOCATION', '')).lower()
            is_exterior = 'balcony' in location
            
            # Get door specs
            width_str = door.get('WIDTH', '')
            height_str = door.get('HEIGHT', '')
            material = door.get('MATERIAL', '')
            door_type = door.get('TYPE', '')
            
            # Find best match
            rsmeans = rsmeans_ext if is_exterior else rsmeans_int
            best_match = self._find_best_door_match(
                width_str, height_str, material, door_type, is_exterior, rsmeans
            )
            
            if best_match is not None:
                # Build better description
                if is_exterior:
                    rsmeans_desc = f"{best_match.get('MATERIAL', '')} {best_match.get('TYPE', '')} {best_match.get('OPENING', '')}"
                else:
                    mat = best_match.get('Material', '')
                    core = best_match.get('Core type', '')
                    desc = best_match.get('DESCRIPTION', '')
                    dims = best_match.get('DIMENSIONS', '')
                    rsmeans_desc = f"{mat} {core} {desc} {dims}".strip()
                
                results.append({
                    'MATERIAL_ID': mark,
                    'MATERIAL_TYPE': 'Exterior Door' if is_exterior else 'Interior Door',
                    'DESCRIPTION': f"{location} - {door_type}",
                    'WIDTH': width_str,
                    'HEIGHT': height_str,
                    'MATERIAL': material,
                    'QUANTITY': total_count,
                    'RSMEANS_CODE': best_match['CODE'],
                    'RSMEANS_DESC': rsmeans_desc,
                    'UNIT_COST_MAT': best_match.get('MAT.', best_match.get('MAT', 0)),
                    'UNIT_COST_INST': best_match.get('INST.', best_match.get('INST', 0)),
                    'UNIT_COST_TOTAL': best_match.get('TOTAL', 0),
                    'TOTAL_COST_MAT': best_match.get('MAT.', best_match.get('MAT', 0)) * total_count,
                    'TOTAL_COST_INST': best_match.get('INST.', best_match.get('INST', 0)) * total_count,
                    'TOTAL_COST': best_match.get('TOTAL', 0) * total_count,
                })
        
        return pd.DataFrame(results)
    
    def _calculate_door_count(self, mark: str, door_counts: pd.DataFrame, 
                             apartment_specs: pd.DataFrame) -> int:
        """Calculate total door count across all units."""
        total = 0
        
        # Get valid unit descriptions from apartment_specs
        valid_units = set(apartment_specs['Unit Description'].values)
        
        for _, unit_row in door_counts.iterrows():
            unit_desc = unit_row.get('Unit Description', '')
            
            # Skip if unit is not in valid units (Total Units = 0)
            if unit_desc not in valid_units:
                continue
            
            # Get unit count from apartment_specs
            unit_spec = apartment_specs[
                apartment_specs['Unit Description'] == unit_desc
            ]
            if len(unit_spec) == 0:
                continue
            
            unit_count = unit_spec.iloc[0]['Total Units']
            
            # Get door count for this mark in this unit
            door_count_in_unit = 0
            # Check column by mark number
            if mark in unit_row:
                val = unit_row[mark]
                if not pd.isna(val):
                    door_count_in_unit = int(val)
            
            total += door_count_in_unit * unit_count
        
        return total
    
    def _find_best_door_match(self, width_str: str, height_str: str, 
                              material: str, door_type: str, is_exterior: bool,
                              rsmeans: pd.DataFrame) -> Optional[Dict]:
        """Find the best matching door in RSMeans data."""
        # Parse dimensions
        w_ft, w_in = parse_dimension(width_str)
        h_ft, h_in = parse_dimension(height_str)
        target_width = dim_to_inches(w_ft, w_in)
        target_height = dim_to_inches(h_ft, h_in)
        
        if is_exterior:
            # For exterior doors, look for sliding glass or similar
            candidates = rsmeans[
                rsmeans['TYPE'].str.contains('glass|door', case=False, na=False)
            ].copy()
            
            if len(candidates) == 0:
                candidates = rsmeans.copy()
            
            # Parse opening size and find closest match
            candidates['opening_width'] = candidates['OPENING'].apply(
                lambda x: self._parse_opening_width(str(x))
            )
            candidates['width_diff'] = abs(candidates['opening_width'] - target_width)
            
            best_idx = candidates['width_diff'].idxmin()
            if pd.notna(best_idx):
                return candidates.loc[best_idx].to_dict()
        else:
            # For interior doors, match by material, core type, and dimensions
            material_lower = str(material).lower()
            
            # Determine core type
            is_solid_core = 'sc' in material_lower
            is_hollow_core = 'hc' in material_lower or 'hollow' in material_lower
            is_wood = 'wood' in material_lower or 'wd' in material_lower
            is_metal = 'metal' in material_lower
            
            # Start with all candidates
            candidates = rsmeans.copy()
            
            # Filter by material type
            if is_wood:
                candidates = candidates[
                    candidates['Material'].str.contains('wood', case=False, na=False)
                ]
            elif is_metal:
                candidates = candidates[
                    candidates['Material'].str.contains('metal', case=False, na=False)
                ]
            
            # Filter by core type for more specificity
            if is_solid_core and len(candidates) > 0:
                solid_candidates = candidates[
                    candidates['Core type'].str.contains('solid', case=False, na=False)
                ]
                if len(solid_candidates) > 0:
                    candidates = solid_candidates
            elif is_hollow_core and len(candidates) > 0:
                hollow_candidates = candidates[
                    candidates['Core type'].str.contains('hollow', case=False, na=False)
                ]
                if len(hollow_candidates) > 0:
                    candidates = hollow_candidates
            
            if len(candidates) > 0:
                # Find closest dimension match
                candidates = candidates.copy()
                candidates['dim_width'] = candidates['DIMENSIONS'].apply(
                    lambda x: self._parse_opening_width(str(x))
                )
                candidates['width_diff'] = abs(candidates['dim_width'] - target_width)
                
                # Sort by width difference, then by cost
                candidates = candidates.sort_values(['width_diff', 'TOTAL'])
                
                best_idx = candidates.index[0]
                if pd.notna(best_idx):
                    return candidates.loc[best_idx].to_dict()
        
        # Fallback
        if len(rsmeans) > 0:
            return rsmeans.iloc[0].to_dict()
        
        return None
    
    def _parse_opening_width(self, opening_str: str) -> float:
        """Parse opening width from string like '3\'-0" x 7\'-0"'."""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', opening_str)
        if matches:
            feet, inches = map(int, matches[0])
            return feet * 12 + inches
        return 36.0  # Default 3 feet
    
    def match_appliances(self) -> pd.DataFrame:
        """Match each appliance to RSMeans cost data (with 10% reduction)."""
        appliance_counts = self.data['appliance_counts']
        rsmeans_appliances = self.data['rsmeans_appliances']
        
        results = []
        
        for _, app in appliance_counts.iterrows():
            appliance_type = app.get('Appliance', '')
            count = app.get('Count', 0)
            
            if pd.isna(count) or count == 0 or pd.isna(appliance_type):
                continue
            
            # Try to match in RSMeans
            best_match = self._find_best_appliance_match(appliance_type, rsmeans_appliances)
            
            if best_match:
                # Parse cost (handle ranges like "885 - 1300")
                cost_str = best_match.get('Cost', '0')
                unit_cost = self._parse_cost(cost_str)
                
                results.append({
                    'MATERIAL_ID': appliance_type,
                    'MATERIAL_TYPE': 'Appliance',
                    'DESCRIPTION': appliance_type,
                    'MANUFACTURER': app.get('Manufacturer', ''),
                    'MODEL': app.get('Model', ''),
                    'QUANTITY': count,
                    'RSMEANS_DESC': best_match.get('Description', ''),
                    'UNIT_COST_ORIGINAL': unit_cost,
                    'UNIT_COST_REDUCED': unit_cost * 0.9,  # 10% reduction
                    'TOTAL_COST_ORIGINAL': unit_cost * count,
                    'TOTAL_COST_REDUCED': unit_cost * 0.9 * count,
                })
        
        return pd.DataFrame(results)
    
    def _find_best_appliance_match(self, appliance_type: str, 
                                    rsmeans: pd.DataFrame) -> Optional[Dict]:
        """Find the best matching appliance in RSMeans data."""
        appliance_lower = appliance_type.lower()
        
        # Map common appliance types to keywords (in order of specificity)
        keywords_map = {
            'refrigerator': ['Refrigerator, no frost', 'Refrigerator'],
            'microwave': ['Microwave oven'],
            'range': ['Cooking range', 'range'],
            'dishwasher': ['Dishwasher, built-in'],
            'washer': ['Washer'],
            'dryer': ['Dryer'],
            'hood': ['Hood for range'],
        }
        
        # Find matching keywords
        for app_key, keywords in keywords_map.items():
            if app_key in appliance_lower:
                for keyword in keywords:
                    matches = rsmeans[
                        rsmeans['Description'].str.contains(keyword, case=False, na=False)
                    ].copy()
                    
                    # Filter out entries with no cost
                    if len(matches) > 0:
                        # Parse costs and filter out zero/empty
                        matches['parsed_cost'] = matches['Cost'].apply(self._parse_cost)
                        matches = matches[matches['parsed_cost'] > 0]
                        
                        if len(matches) > 0:
                            return matches.iloc[0].to_dict()
        
        # Fallback: return first appliance with a cost
        if len(rsmeans) > 0:
            rsmeans_copy = rsmeans.copy()
            rsmeans_copy['parsed_cost'] = rsmeans_copy['Cost'].apply(self._parse_cost)
            with_cost = rsmeans_copy[rsmeans_copy['parsed_cost'] > 0]
            if len(with_cost) > 0:
                return with_cost.iloc[0].to_dict()
        
        return None
    
    def _parse_cost(self, cost_str: str) -> float:
        """Parse cost string, handling ranges like '885 - 1300'."""
        if pd.isna(cost_str):
            return 0.0
        
        cost_str = str(cost_str).replace(',', '').replace('$', '').strip()
        
        # Handle ranges - take the average
        if '-' in cost_str:
            parts = cost_str.split('-')
            try:
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return (low + high) / 2.0
            except:
                pass
        
        # Single value
        try:
            return float(cost_str)
        except:
            return 0.0


def main():
    """Test the material matcher."""
    from data_loader import DataLoader
    
    loader = DataLoader()
    data = loader.load_all()
    
    matcher = MaterialMatcher(data)
    
    print("="*60)
    print("WINDOWS")
    print("="*60)
    windows = matcher.match_windows()
    print(windows.to_string())
    
    print("\n" + "="*60)
    print("DOORS")
    print("="*60)
    doors = matcher.match_doors()
    print(doors.to_string())
    
    print("\n" + "="*60)
    print("APPLIANCES")
    print("="*60)
    appliances = matcher.match_appliances()
    print(appliances.to_string())
    
    # Save to processed folder
    windows.to_csv('/app/data/processed/matched_windows.csv', index=False)
    doors.to_csv('/app/data/processed/matched_doors.csv', index=False)
    appliances.to_csv('/app/data/processed/matched_appliances.csv', index=False)
    
    print("\n✅ Matched materials saved to data/processed/")


if __name__ == "__main__":
    main()

