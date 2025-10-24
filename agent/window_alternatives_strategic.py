"""
Strategic window alternatives finder - provides 4 specific alternatives per window:
1. Best Functional + Cost: Highest functional score with cost reduction
2. Best Design + Cost: Highest design score with cost reduction  
3. Best Cost Only: Lowest cost regardless of quality
4. Balanced: Best balance of functional, design, and cost
"""
import pandas as pd
import re
from typing import List, Dict


class StrategicWindowAlternativesFinder:
    """Find 4 strategic alternatives for each window."""
    
    def __init__(self, rsmeans_windows: pd.DataFrame):
        self.rsmeans = rsmeans_windows
    
    def find_alternatives_for_window(self, window_spec: Dict) -> List[Dict]:
        """Find 4 strategic alternatives for a specific window."""
        material_id = window_spec['MATERIAL_ID']
        original_cost = window_spec['UNIT_COST_TOTAL']
        original_code = window_spec['RSMEANS_CODE']
        area = window_spec['AREA_SQFT']
        description = window_spec.get('DESCRIPTION', '')
        style = str(description).lower()
        
        # Get candidates (same style, similar area, at most same cost)
        candidates = self._get_candidates(original_code, original_cost, area, style)
        
        if len(candidates) == 0:
            # No alternatives available
            return []
        
        alternatives = []
        used_codes = set()
        
        # 1. Best Functional + Cost (prefer wood for functional)
        best_func = self._find_best_functional_cost(candidates, used_codes)
        if best_func is not None:
            alternatives.append({
                'strategy': 'best_functional_cost',
                'label': 'Best Functional + Cost',
                **best_func
            })
            used_codes.add(best_func['CODE'])
        
        # 2. Best Design + Cost (prefer wood for design)
        best_design = self._find_best_design_cost(candidates, used_codes)
        if best_design is not None:
            alternatives.append({
                'strategy': 'best_design_cost',
                'label': 'Best Design + Cost',
                **best_design
            })
            used_codes.add(best_design['CODE'])
        
        # 3. Best Cost Only (just cheapest, prefer aluminum)
        best_cost = self._find_best_cost_only(candidates, used_codes)
        if best_cost is not None:
            alternatives.append({
                'strategy': 'best_cost_only',
                'label': 'Lowest Cost',
                **best_cost
            })
            used_codes.add(best_cost['CODE'])
        
        # 4. Balanced (prefer vinyl as middle ground)
        balanced = self._find_balanced(candidates, used_codes)
        if balanced is not None:
            alternatives.append({
                'strategy': 'balanced',
                'label': 'Balanced',
                **balanced
            })
            used_codes.add(balanced['CODE'])
        
        return alternatives
    
    def _get_candidates(self, original_code: str, original_cost: float,
                        target_area: float, style: str) -> pd.DataFrame:
        """Get valid candidate alternatives."""
        # Exclude original
        candidates = self.rsmeans[self.rsmeans['CODE'] != original_code].copy()
        
        # Filter by style (more lenient to get more options)
        style_keywords = ['casement', 'sliding', 'fixed', 'picture', 'awning', 'double hung']
        matched_style = None
        for keyword in style_keywords:
            if keyword in style:
                matched_style = keyword
                break
        
        # Try style match first
        if matched_style:
            style_candidates = candidates[
                candidates['TYPE'].str.contains(matched_style, case=False, na=False)
            ]
            if len(style_candidates) >= 4:
                candidates = style_candidates
        
        # Calculate area
        candidates['area'] = candidates['SIZE'].apply(self._parse_window_size)
        candidates['area_diff_pct'] = abs(candidates['area'] - target_area) / target_area * 100
        
        # Strict dimension matching - area within 20% (dimensions roughly close)
        strict = candidates[
            (candidates['area_diff_pct'] <= 20) &
            (candidates['TOTAL'] <= original_cost)
        ].copy()
        
        if len(strict) >= 4:
            return strict
        
        # If not enough with 20%, allow up to 30%
        medium = candidates[
            (candidates['area_diff_pct'] <= 30) &
            (candidates['TOTAL'] <= original_cost)
        ].copy()
        
        if len(medium) >= 2:
            return medium
        
        # Last resort: up to 40% but still reasonable
        lenient = candidates[
            (candidates['area_diff_pct'] <= 40) &
            (candidates['TOTAL'] <= original_cost)
        ].copy()
        
        return lenient
    
    def _find_best_functional_cost(self, candidates: pd.DataFrame, used_codes: set) -> Dict:
        """Find alternative with best functional score + cost reduction.
        
        Functional criteria: Insulation, durability, weather resistance, ventilation
        """
        if len(candidates) == 0:
            return None
        
        # Exclude already used
        available = candidates[~candidates['CODE'].isin(used_codes)].copy()
        if len(available) == 0:
            available = candidates.copy()
        
        # Functional scoring (performance-based):
        available['functional_score'] = 2  # Baseline
        
        # Wood: Best insulation, durability, weather resistance
        wood_mask = available['MATERIAL'].str.contains('Wood', case=False, na=False)
        available.loc[wood_mask, 'functional_score'] = 5
        
        # Vinyl: Good insulation, moderate durability, good weather resistance
        vinyl_mask = available['MATERIAL'].str.contains('Vinyl', case=False, na=False)
        available.loc[vinyl_mask, 'functional_score'] = 4
        
        # Aluminum: Poor insulation, excellent durability, moderate weather resistance
        aluminum_mask = available['MATERIAL'].str.contains('Aluminum', case=False, na=False)
        available.loc[aluminum_mask, 'functional_score'] = 3
        
        # Bonus for insulated glass (better thermal performance)
        insulated_mask = available['GLAZING'].str.contains('insul', case=False, na=False)
        available.loc[insulated_mask, 'functional_score'] += 0.5
        
        # Sort by functional score (desc), then cost (asc)
        available = available.sort_values(['functional_score', 'TOTAL'], ascending=[False, True])
        
        if len(available) > 0:
            return available.iloc[0].to_dict()
        return None
    
    def _find_best_design_cost(self, candidates: pd.DataFrame, used_codes: set) -> Dict:
        """Find alternative with best design score + cost reduction.
        
        Design criteria: Aesthetics, architectural intent, visual appeal, premium appearance
        """
        if len(candidates) == 0:
            return None
        
        # Exclude already used
        available = candidates[~candidates['CODE'].isin(used_codes)].copy()
        if len(available) == 0:
            available = candidates.copy()
        
        # Design scoring (aesthetics-based):
        available['design_score'] = 2  # Baseline
        
        # Wood: Premium, traditional, high-end aesthetic
        wood_mask = available['MATERIAL'].str.contains('Wood', case=False, na=False)
        available.loc[wood_mask, 'design_score'] = 5
        
        # Vinyl: Modern but less premium look
        vinyl_mask = available['MATERIAL'].str.contains('Vinyl', case=False, na=False)
        available.loc[vinyl_mask, 'design_score'] = 3
        
        # Aluminum: Industrial look, modern but less warm
        aluminum_mask = available['MATERIAL'].str.contains('Aluminum', case=False, na=False)
        available.loc[aluminum_mask, 'design_score'] = 3.5
        
        # Penalty for smaller size (less impressive visually)
        available.loc[available['area'] < 20, 'design_score'] -= 0.5
        
        # Bonus for bay/picture windows (architectural features)
        bay_mask = available['TYPE'].str.contains('bay|picture', case=False, na=False)
        available.loc[bay_mask, 'design_score'] += 1
        
        # Sort by design score (desc), then cost (asc)
        available = available.sort_values(['design_score', 'TOTAL'], ascending=[False, True])
        
        if len(available) > 0:
            return available.iloc[0].to_dict()
        return None
    
    def _find_best_cost_only(self, candidates: pd.DataFrame, used_codes: set) -> Dict:
        """Find alternative with lowest cost."""
        if len(candidates) == 0:
            return None
        
        # Exclude already used
        available = candidates[~candidates['CODE'].isin(used_codes)].copy()
        if len(available) == 0:
            available = candidates.copy()
        
        # Prefer aluminum (usually cheapest) for cost-only strategy
        aluminum = available[available['MATERIAL'].str.contains('Aluminum', case=False, na=False)]
        if len(aluminum) > 0:
            cheapest = aluminum.nsmallest(1, 'TOTAL')
        else:
            cheapest = available.nsmallest(1, 'TOTAL')
        
        if len(cheapest) > 0:
            return cheapest.iloc[0].to_dict()
        return None
    
    def _find_balanced(self, candidates: pd.DataFrame, used_codes: set) -> Dict:
        """Find balanced alternative - best overall compromise."""
        if len(candidates) == 0:
            return None
        
        # Exclude already used
        available = candidates[~candidates['CODE'].isin(used_codes)].copy()
        if len(available) == 0:
            available = candidates.copy()
        
        # Prefer vinyl for balanced (good middle ground)
        vinyl = available[available['MATERIAL'].str.contains('Vinyl', case=False, na=False)]
        if len(vinyl) > 0:
            vinyl = vinyl.sort_values('TOTAL')
            mid_idx = len(vinyl) // 2
            return vinyl.iloc[mid_idx].to_dict()
        
        # Calculate balanced score
        available = available.copy()
        
        # Functional scoring (performance)
        available['functional_score'] = 2
        wood_mask = available['MATERIAL'].str.contains('Wood', case=False, na=False)
        vinyl_mask = available['MATERIAL'].str.contains('Vinyl', case=False, na=False)
        aluminum_mask = available['MATERIAL'].str.contains('Aluminum', case=False, na=False)
        
        available.loc[wood_mask, 'functional_score'] = 5  # Best insulation
        available.loc[vinyl_mask, 'functional_score'] = 4   # Good insulation
        available.loc[aluminum_mask, 'functional_score'] = 3 # Poor insulation
        
        # Bonus for insulated glass
        insulated_mask = available['GLAZING'].str.contains('insul', case=False, na=False)
        available.loc[insulated_mask, 'functional_score'] += 0.5
        
        # Design scoring (aesthetics - DIFFERENT from functional)
        available['design_score'] = 2
        available.loc[wood_mask, 'design_score'] = 5      # Premium, traditional
        available.loc[vinyl_mask, 'design_score'] = 3     # Modern but less premium
        available.loc[aluminum_mask, 'design_score'] = 3.5 # Sleek modern but industrial
        
        # Bonus for architectural features
        bay_mask = available['TYPE'].str.contains('bay|picture', case=False, na=False)
        available.loc[bay_mask, 'design_score'] += 1
        
        # Penalty for smaller windows (less impressive)
        available.loc[available['area'] < 20, 'design_score'] -= 0.5
        
        # Cost score
        max_cost = available['TOTAL'].max()
        available['cost_reduction_pct'] = ((max_cost - available['TOTAL']) / max_cost) * 100
        available['cost_score'] = available['cost_reduction_pct'].apply(self._pct_to_score)
        
        # Balanced score
        available['balanced_score'] = (
            available['functional_score'] / 5.5 * 0.333 +
            available['design_score'] / 6.0 * 0.333 +
            available['cost_score'] / 5.0 * 0.334
        )
        
        # Sort by balanced score
        available = available.sort_values('balanced_score', ascending=False)
        
        if len(available) > 0:
            return available.iloc[0].to_dict()
        return None
    
    def _parse_window_size(self, size_str: str) -> float:
        """Parse window size to square feet."""
        matches = re.findall(r'(\d+)(?:\'-|-)(\d+)', str(size_str))
        if len(matches) >= 2:
            w_ft, w_in = map(int, matches[0])
            h_ft, h_in = map(int, matches[1])
            width_inches = w_ft * 12 + w_in
            height_inches = h_ft * 12 + h_in
            return (width_inches * height_inches) / 144.0
        return 20.0
    
    def _pct_to_score(self, pct: float) -> int:
        """Convert percentage to 1-5 score."""
        if pct >= 30: return 5
        if pct >= 20: return 4
        if pct >= 15: return 3
        if pct >= 10: return 2
        if pct >= 5: return 1
        return 1


def main():
    """Test strategic alternatives finder."""
    from data_loader import DataLoader
    from material_matcher import MaterialMatcher
    
    loader = DataLoader()
    data = loader.load_all()
    
    matcher = MaterialMatcher(data)
    windows = matcher.match_windows()
    
    finder = StrategicWindowAlternativesFinder(data['rsmeans_windows'])
    
    # Test on first few windows
    for _, window in windows.head(3).iterrows():
        print(f"\n{'='*60}")
        print(f"Window: {window['MATERIAL_ID']}")
        print(f"Original: {window['RSMEANS_DESC']} - ${window['UNIT_COST_TOTAL']:.2f}")
        print(f"{'='*60}")
        
        alternatives = finder.find_alternatives_for_window(window.to_dict())
        for alt in alternatives:
            print(f"\n  {alt['label']}:")
            print(f"    {alt['MATERIAL']} {alt['TYPE']} {alt['SIZE']}")
            print(f"    Cost: ${alt['TOTAL']:.2f}")


if __name__ == '__main__':
    main()

