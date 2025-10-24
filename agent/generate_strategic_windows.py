"""
Generate strategic window alternatives with 4 options per window.
"""
import pandas as pd
from data_loader import DataLoader
from material_matcher import MaterialMatcher
from window_alternatives_strategic import StrategicWindowAlternativesFinder


def generate_strategic_window_alternatives():
    """Generate window alternatives with 4 strategic options each."""
    # Load data
    loader = DataLoader()
    data = loader.load_all()
    
    # Match windows
    matcher = MaterialMatcher(data)
    windows = matcher.match_windows()
    
    # Find strategic alternatives
    finder = StrategicWindowAlternativesFinder(data['rsmeans_windows'])
    
    results = []
    
    for _, window in windows.iterrows():
        material_id = window['MATERIAL_ID']
        original_cost = window['UNIT_COST_TOTAL']
        
        # Add original (rank 0)
        results.append({
            'MATERIAL_ID': material_id,
            'MATERIAL_TYPE': 'Window',
            'ORIGINAL_CODE': window['RSMEANS_CODE'],
            'ORIGINAL_COST': original_cost,
            'ALT_RANK': 0,
            'ALT_CODE': window['RSMEANS_CODE'],
            'ALT_DESC': window['RSMEANS_DESC'],
            'ALT_COST_MAT': window['UNIT_COST_MAT'],
            'ALT_COST_INST': window['UNIT_COST_INST'],
            'ALT_COST_TOTAL': original_cost,
            'COST_REDUCTION_PCT': 0.0,
            'FUNCTIONAL_SCORE': 5,
            'DESIGN_SCORE': 5,
            'COST_SCORE': 1,
            'STRATEGY': 'original',
            'STRATEGY_LABEL': 'Original'
        })
        
        # Find 4 strategic alternatives
        alternatives = finder.find_alternatives_for_window(window.to_dict())
        
        for rank, alt in enumerate(alternatives, start=1):
            cost_reduction = ((original_cost - alt['TOTAL']) / original_cost) * 100
            
            # Get functional and design scores based on material, size, and variants
            material = alt['MATERIAL']
            window_type = alt['TYPE']
            glazing = str(alt.get('GLAZING', '')).lower()
            detail = str(alt.get('DETAIL', '')).lower()
            area = alt.get('area', 20)
            
            # FUNCTIONAL SCORE - Based on performance
            # Primary factor: MATERIAL TYPE (matters a lot)
            if 'Wood' in material:
                func_score = 5.0  # Best insulation & durability
            elif 'Vinyl' in material:
                func_score = 4.0  # Good insulation
            elif 'Aluminum' in material:
                func_score = 2.5  # Poor insulation
            else:
                func_score = 3.0
            
            # Variant/subtype adjustment (matters a bit)
            if 'insul' in glazing:
                func_score += 0.3  # Insulated glass helps
            if 'low-e' in str(alt.get('GLAZING', '')).lower():
                func_score += 0.2  # Low-E coating helps
            
            # Size adjustment (matters a bit for functional)
            if area < 15:
                func_score -= 0.2  # Small window = less ventilation
            
            func_score = max(1.0, min(5.0, func_score))
            
            # DESIGN SCORE - Based on aesthetics
            # Primary factor: MATERIAL TYPE (matters a lot)
            if 'Wood' in material:
                design_score = 5.0  # Premium, traditional
            elif 'Aluminum' in material:
                design_score = 3.0  # Modern, industrial
            elif 'Vinyl' in material:
                design_score = 2.5  # Budget aesthetic
            else:
                design_score = 3.0
            
            # Size adjustment (matters a LOT for design)
            if area >= 40:
                design_score += 1.0  # Large windows are impressive
            elif area >= 30:
                design_score += 0.5  # Medium-large
            elif area < 15:
                design_score -= 1.0  # Small windows less impactful
            elif area < 20:
                design_score -= 0.5
            
            # Architectural features (matters for design)
            if 'bay' in window_type.lower():
                design_score += 0.8  # Bay windows are architectural features
            if 'picture' in window_type.lower():
                design_score += 0.6  # Picture windows for views
            
            # Variant/subtype (doesn't really matter for design)
            # - Intentionally NOT considering glazing type, low-e, etc. for design
            
            design_score = max(1.0, min(5.0, design_score))
            
            # Cost score
            if cost_reduction >= 30: cost_score = 5
            elif cost_reduction >= 20: cost_score = 4
            elif cost_reduction >= 15: cost_score = 3
            elif cost_reduction >= 10: cost_score = 2
            else: cost_score = 1
            
            results.append({
                'MATERIAL_ID': material_id,
                'MATERIAL_TYPE': 'Window',
                'ORIGINAL_CODE': window['RSMEANS_CODE'],
                'ORIGINAL_COST': original_cost,
                'ALT_RANK': rank,
                'ALT_CODE': alt['CODE'],
                'ALT_DESC': f"{alt['MATERIAL']} {alt['TYPE']} {alt['SIZE']}",
                'ALT_COST_MAT': alt['MAT'],
                'ALT_COST_INST': alt['INST'],
                'ALT_COST_TOTAL': alt['TOTAL'],
                'COST_REDUCTION_PCT': cost_reduction,
                'FUNCTIONAL_SCORE': func_score,
                'DESIGN_SCORE': design_score,
                'COST_SCORE': cost_score,
                'STRATEGY': alt['strategy'],
                'STRATEGY_LABEL': alt['label']
            })
    
    df = pd.DataFrame(results)
    
    # Save
    output_path = '/app/data/processed/window_alternatives_scored.csv'
    df.to_csv(output_path, index=False)
    print(f'✅ Strategic window alternatives saved to {output_path}')
    
    # Show summary
    print(f'\nGenerated alternatives for {df["MATERIAL_ID"].nunique()} windows')
    print(f'Total rows: {len(df)}')
    print(f'Expected: {df["MATERIAL_ID"].nunique() * 5} (original + 4 alternatives each)')
    
    return df


if __name__ == '__main__':
    generate_strategic_window_alternatives()

