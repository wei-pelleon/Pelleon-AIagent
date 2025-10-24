"""
Alternatives finder module - finds top 3 cost-effective alternatives for each material.

Rules:
1. Windows: Similar area and style, cheaper alternatives
2. Exterior doors: Similar materials, width fixed, height > 7', cheaper
3. Interior doors: Similar materials and dimensions, cheaper
4. Appliances: Uniform 10% reduction (no alternatives needed)
"""
import pandas as pd
from typing import List, Dict, Optional
import re


class AlternativesFinder:
    """Finds cost-effective alternatives for matched materials."""
    
    def __init__(self, data: Dict[str, pd.DataFrame], matched_materials: Dict[str, pd.DataFrame]):
        self.data = data
        self.matched_materials = matched_materials
        
    def find_window_alternatives(self) -> pd.DataFrame:
        """Find top 3 alternatives for each window type."""
        windows = self.matched_materials['windows']
        rsmeans_windows = self.data['rsmeans_windows']
        
        results = []
        
        for _, window in windows.iterrows():
            material_id = window['MATERIAL_ID']
            original_cost = window['UNIT_COST_TOTAL']
            original_code = window['RSMEANS_CODE']
            area = window['AREA_SQFT']
            style = str(window['DESCRIPTION']).lower()
            
            # Find alternatives
            alternatives = self._find_window_alts(
                original_code, original_cost, area, style, rsmeans_windows
            )
            
            # Add original as rank 0
            results.append({
                'MATERIAL_ID': material_id,
                'MATERIAL_TYPE': 'Window',
                'ORIGINAL_CODE': original_code,
                'ORIGINAL_COST': original_cost,
                'ALT_RANK': 0,
                'ALT_CODE': original_code,
                'ALT_DESC': window['RSMEANS_DESC'],
                'ALT_COST_MAT': window['UNIT_COST_MAT'],
                'ALT_COST_INST': window['UNIT_COST_INST'],
                'ALT_COST_TOTAL': original_cost,
                'COST_REDUCTION_PCT': 0.0,
            })
            
            # Add alternatives
            for rank, alt in enumerate(alternatives, start=1):
                cost_reduction = ((original_cost - alt['TOTAL']) / original_cost) * 100
                results.append({
                    'MATERIAL_ID': material_id,
                    'MATERIAL_TYPE': 'Window',
                    'ORIGINAL_CODE': original_code,
                    'ORIGINAL_COST': original_cost,
                    'ALT_RANK': rank,
                    'ALT_CODE': alt['CODE'],
                    'ALT_DESC': f"{alt['MATERIAL']} {alt['TYPE']} {alt['SIZE']}",
                    'ALT_COST_MAT': alt['MAT'],
                    'ALT_COST_INST': alt['INST'],
                    'ALT_COST_TOTAL': alt['TOTAL'],
                    'COST_REDUCTION_PCT': cost_reduction,
                })
        
        return pd.DataFrame(results)
    
    def _find_window_alts(self, original_code: str, original_cost: float,
                          target_area: float, style: str, 
                          rsmeans: pd.DataFrame) -> List[Dict]:
        """Find up to 3 window alternatives."""
        # Filter out original
        candidates = rsmeans[rsmeans['CODE'] != original_code].copy()
        
        # Filter by style keywords
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
        
        # Calculate area similarity
        candidates['area'] = candidates['SIZE'].apply(self._parse_window_size)
        candidates['area_diff_pct'] = abs(candidates['area'] - target_area) / target_area * 100
        
        # Filter: area within 30% of target
        candidates = candidates[candidates['area_diff_pct'] <= 30].copy()
        
        # Filter: cheaper than original
        candidates = candidates[candidates['TOTAL'] < original_cost].copy()
        
        # Sort by cost (cheapest first)
        candidates = candidates.sort_values('TOTAL')
        
        # Return top 3
        return candidates.head(3).to_dict('records')
    
    def _parse_window_size(self, size_str: str) -> float:
        """Parse window size string to square feet."""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', str(size_str))
        if len(matches) >= 2:
            w_ft, w_in = map(int, matches[0])
            h_ft, h_in = map(int, matches[1])
            width_inches = w_ft * 12 + w_in
            height_inches = h_ft * 12 + h_in
            return (width_inches * height_inches) / 144.0
        return 20.0
    
    def find_door_alternatives(self) -> pd.DataFrame:
        """Find top 3 alternatives for each door type."""
        doors = self.matched_materials['doors']
        rsmeans_ext = self.data['rsmeans_ext_doors']
        rsmeans_int = self.data['rsmeans_int_doors']
        
        results = []
        
        for _, door in doors.iterrows():
            material_id = door['MATERIAL_ID']
            material_type = door['MATERIAL_TYPE']
            original_cost = door['UNIT_COST_TOTAL']
            original_code = door['RSMEANS_CODE']
            width = door['WIDTH']
            height = door['HEIGHT']
            material = door.get('MATERIAL', '')
            
            is_exterior = material_type == 'Exterior Door'
            rsmeans = rsmeans_ext if is_exterior else rsmeans_int
            
            # Find alternatives
            alternatives = self._find_door_alts(
                original_code, original_cost, width, height, 
                material, is_exterior, rsmeans
            )
            
            # Add original as rank 0 (use the same description from matched_doors)
            original_desc = door['RSMEANS_DESC']
            
            results.append({
                'MATERIAL_ID': material_id,
                'MATERIAL_TYPE': material_type,
                'ORIGINAL_CODE': original_code,
                'ORIGINAL_COST': original_cost,
                'ALT_RANK': 0,
                'ALT_CODE': original_code,
                'ALT_DESC': original_desc,
                'ALT_COST_MAT': door['UNIT_COST_MAT'],
                'ALT_COST_INST': door['UNIT_COST_INST'],
                'ALT_COST_TOTAL': original_cost,
                'COST_REDUCTION_PCT': 0.0,
            })
            
            # Add alternatives
            for rank, alt in enumerate(alternatives, start=1):
                cost_reduction = ((original_cost - alt['TOTAL']) / original_cost) * 100
                mat_cost = alt.get('MAT.', alt.get('MAT', 0))
                inst_cost = alt.get('INST.', alt.get('INST', 0))
                
                # Build better description based on door type
                if material_type == 'Exterior Door':
                    alt_desc = f"{alt.get('MATERIAL', '')} {alt.get('TYPE', '')} {alt.get('OPENING', '')}".strip()
                else:
                    mat = alt.get('Material', '')
                    core = alt.get('Core type', '')
                    desc = alt.get('DESCRIPTION', '')
                    dims = alt.get('DIMENSIONS', '')
                    alt_desc = f"{mat} {core} {desc} {dims}".strip()
                    # Fallback if still empty
                    if not alt_desc:
                        alt_desc = f"{alt.get('MATERIAL', '')} {alt.get('TYPE', '')}".strip()
                
                results.append({
                    'MATERIAL_ID': material_id,
                    'MATERIAL_TYPE': material_type,
                    'ORIGINAL_CODE': original_code,
                    'ORIGINAL_COST': original_cost,
                    'ALT_RANK': rank,
                    'ALT_CODE': alt['CODE'],
                    'ALT_DESC': alt_desc,
                    'ALT_COST_MAT': mat_cost,
                    'ALT_COST_INST': inst_cost,
                    'ALT_COST_TOTAL': alt['TOTAL'],
                    'COST_REDUCTION_PCT': cost_reduction,
                })
        
        return pd.DataFrame(results)
    
    def _find_door_alts(self, original_code: str, original_cost: float,
                        width_str: str, height_str: str, material: str,
                        is_exterior: bool, rsmeans: pd.DataFrame) -> List[Dict]:
        """Find up to 3 door alternatives."""
        # Parse dimensions
        target_width = self._parse_door_width(width_str)
        target_height = self._parse_door_height(height_str)
        
        # Filter out original
        candidates = rsmeans[rsmeans['CODE'] != original_code].copy()
        
        if is_exterior:
            # For exterior doors: height > 7' (84 inches)
            candidates['height'] = candidates['OPENING'].apply(self._parse_door_height)
            candidates = candidates[candidates['height'] >= 84].copy()
            
            # Keep similar materials
            if 'glass' in str(material).lower() or 'WD/CMF' in str(material):
                candidates = candidates[
                    candidates['MATERIAL'].str.contains('glass|alum', case=False, na=False)
                ].copy()
        else:
            # For interior doors: similar materials and dimensions
            material_lower = str(material).lower()
            
            if 'wood' in material_lower or 'wd' in material_lower:
                candidates = candidates[
                    candidates['Material'].str.contains('wood', case=False, na=False)
                ].copy()
            elif 'metal' in material_lower:
                candidates = candidates[
                    candidates['Material'].str.contains('metal', case=False, na=False)
                ].copy()
            
            # Width should be close (within 6 inches)
            candidates['width'] = candidates['DIMENSIONS'].apply(self._parse_door_width)
            candidates['width_diff'] = abs(candidates['width'] - target_width)
            candidates = candidates[candidates['width_diff'] <= 6].copy()
        
        # Filter: at most same price as original (never more expensive)
        valid_alternatives = candidates[candidates['TOTAL'] <= original_cost].copy()
        
        # If we have less than 3 alternatives, also include same-price options with different specs
        if len(valid_alternatives) < 3:
            # Find alternatives at exactly the same price
            same_price = candidates[candidates['TOTAL'] == original_cost].copy()
            
            # Combine and remove duplicates
            valid_alternatives = pd.concat([valid_alternatives, same_price]).drop_duplicates(subset=['CODE'])
        
        # Sort by cost (cheapest first)
        valid_alternatives = valid_alternatives.sort_values('TOTAL')
        
        # Return top 3 (or however many we found)
        return valid_alternatives.head(3).to_dict('records')
    
    def _parse_door_width(self, width_str: str) -> float:
        """Parse door width to inches."""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', str(width_str))
        if matches:
            feet, inches = map(int, matches[0])
            return feet * 12 + inches
        return 36.0
    
    def _parse_door_height(self, height_str: str) -> float:
        """Parse door height to inches."""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', str(height_str))
        if matches:
            feet, inches = map(int, matches[0])
            return feet * 12 + inches
        return 84.0
    
    def create_appliance_alternatives(self) -> pd.DataFrame:
        """Create alternatives table for appliances (uniform 10% reduction)."""
        appliances = self.matched_materials['appliances']
        
        results = []
        
        for _, app in appliances.iterrows():
            material_id = app['MATERIAL_ID']
            original_cost = app['UNIT_COST_ORIGINAL']
            reduced_cost = app['UNIT_COST_REDUCED']
            
            # Original (rank 0)
            results.append({
                'MATERIAL_ID': material_id,
                'MATERIAL_TYPE': 'Appliance',
                'ORIGINAL_CODE': 'N/A',
                'ORIGINAL_COST': original_cost,
                'ALT_RANK': 0,
                'ALT_CODE': 'ORIGINAL',
                'ALT_DESC': f"{material_id} (Original)",
                'ALT_COST_TOTAL': original_cost,
                'COST_REDUCTION_PCT': 0.0,
            })
            
            # Alternative: 10% reduction (rank 1)
            results.append({
                'MATERIAL_ID': material_id,
                'MATERIAL_TYPE': 'Appliance',
                'ORIGINAL_CODE': 'N/A',
                'ORIGINAL_COST': original_cost,
                'ALT_RANK': 1,
                'ALT_CODE': 'REDUCED',
                'ALT_DESC': f"{material_id} (10% discount)",
                'ALT_COST_TOTAL': reduced_cost,
                'COST_REDUCTION_PCT': 10.0,
            })
        
        return pd.DataFrame(results)
    
    def find_all_alternatives(self) -> Dict[str, pd.DataFrame]:
        """Find all alternatives and return as dictionary."""
        return {
            'window_alternatives': self.find_window_alternatives(),
            'door_alternatives': self.find_door_alternatives(),
            'appliance_alternatives': self.create_appliance_alternatives(),
        }


def main():
    """Test the alternatives finder."""
    from data_loader import DataLoader
    from material_matcher import MaterialMatcher
    
    # Load data and match materials
    loader = DataLoader()
    data = loader.load_all()
    
    matcher = MaterialMatcher(data)
    matched_materials = {
        'windows': matcher.match_windows(),
        'doors': matcher.match_doors(),
        'appliances': matcher.match_appliances(),
    }
    
    # Find alternatives
    finder = AlternativesFinder(data, matched_materials)
    alternatives = finder.find_all_alternatives()
    
    print("="*60)
    print("WINDOW ALTERNATIVES")
    print("="*60)
    window_alts = alternatives['window_alternatives']
    print(f"Total entries: {len(window_alts)}")
    print(window_alts.head(10).to_string())
    
    print("\n" + "="*60)
    print("DOOR ALTERNATIVES")
    print("="*60)
    door_alts = alternatives['door_alternatives']
    print(f"Total entries: {len(door_alts)}")
    print(door_alts.head(10).to_string())
    
    print("\n" + "="*60)
    print("APPLIANCE ALTERNATIVES")
    print("="*60)
    app_alts = alternatives['appliance_alternatives']
    print(f"Total entries: {len(app_alts)}")
    print(app_alts.head(10).to_string())
    
    # Save to processed folder
    window_alts.to_csv('/Users/weizhang/git/VEAgent/data/processed/window_alternatives.csv', index=False)
    door_alts.to_csv('/Users/weizhang/git/VEAgent/data/processed/door_alternatives.csv', index=False)
    app_alts.to_csv('/Users/weizhang/git/VEAgent/data/processed/appliance_alternatives.csv', index=False)
    
    print("\n✅ Alternatives saved to data/processed/")


if __name__ == "__main__":
    main()

