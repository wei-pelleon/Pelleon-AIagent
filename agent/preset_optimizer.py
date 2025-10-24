"""
Preset optimizer - calculates optimal selections for UI presets.
Creates JSON files that the UI can load to auto-select alternatives.
"""
import pandas as pd
import json
from pathlib import Path


class PresetOptimizer:
    """Calculates preset optimization strategies for the UI."""
    
    def __init__(self, data_dir: str = '/Users/weizhang/git/VEAgent/data/processed'):
        self.data_dir = Path(data_dir)
        self.windows = pd.read_csv(self.data_dir / 'window_alternatives_scored.csv')
        self.doors = pd.read_csv(self.data_dir / 'door_alternatives_scored.csv')
        self.appliances = pd.read_csv(self.data_dir / 'appliance_alternatives_scored.csv')
        
    def calculate_all_presets(self):
        """Calculate all preset configurations."""
        presets = {
            'best_functional_cost': self._best_functional_with_cost(),
            'best_cost_only': self._best_cost_only(),
            'best_design_cost': self._best_design_with_cost(),
            'balanced': self._balanced()
        }
        return presets
    
    def _best_functional_with_cost(self):
        """Best functional deviation while having best cost reduction."""
        selections = {}
        
        # For each material, find alternative with:
        # 1. Highest functional score
        # 2. Among those, highest cost reduction
        for df in [self.windows, self.doors, self.appliances]:
            for material_id in df['MATERIAL_ID'].unique():
                material_alts = df[df['MATERIAL_ID'] == material_id].copy()
                
                # Filter to alternatives with cost reduction
                with_reduction = material_alts[material_alts['COST_REDUCTION_PCT'] > 0]
                
                if len(with_reduction) > 0:
                    # Sort by functional score (desc), then cost reduction (desc)
                    best = with_reduction.sort_values(
                        ['FUNCTIONAL_SCORE', 'COST_REDUCTION_PCT'],
                        ascending=[False, False]
                    ).iloc[0]
                    selections[str(material_id)] = str(best['ALT_RANK'])
                else:
                    # Keep original if no alternatives with cost reduction
                    selections[str(material_id)] = '0'
        
        return selections
    
    def _best_cost_only(self):
        """Best cost reduction regardless of functional and design impact."""
        selections = {}
        
        # For each material, find alternative with highest cost reduction
        for df in [self.windows, self.doors, self.appliances]:
            for material_id in df['MATERIAL_ID'].unique():
                material_alts = df[df['MATERIAL_ID'] == material_id].copy()
                
                # Find max cost reduction
                best = material_alts.loc[material_alts['COST_REDUCTION_PCT'].idxmax()]
                selections[str(material_id)] = str(best['ALT_RANK'])
        
        return selections
    
    def _best_design_with_cost(self):
        """Best design deviation while having best cost reduction."""
        selections = {}
        
        # For each material, find alternative with:
        # 1. Highest design score
        # 2. Among those, highest cost reduction
        for df in [self.windows, self.doors, self.appliances]:
            for material_id in df['MATERIAL_ID'].unique():
                material_alts = df[df['MATERIAL_ID'] == material_id].copy()
                
                # Filter to alternatives with cost reduction
                with_reduction = material_alts[material_alts['COST_REDUCTION_PCT'] > 0]
                
                if len(with_reduction) > 0:
                    # Sort by design score (desc), then cost reduction (desc)
                    best = with_reduction.sort_values(
                        ['DESIGN_SCORE', 'COST_REDUCTION_PCT'],
                        ascending=[False, False]
                    ).iloc[0]
                    selections[str(material_id)] = str(best['ALT_RANK'])
                else:
                    # Keep original if no alternatives with cost reduction
                    selections[str(material_id)] = '0'
        
        return selections
    
    def _balanced(self):
        """Balanced approach - 1/3 weight for functional, design, and cost."""
        selections = {}
        
        # For each material, calculate weighted score
        for df in [self.windows, self.doors, self.appliances]:
            for material_id in df['MATERIAL_ID'].unique():
                material_alts = df[df['MATERIAL_ID'] == material_id].copy()
                
                # Normalize scores to 0-1 range for fair comparison
                # Functional and Design are already 1-5
                # Cost score is 1-5
                material_alts['normalized_functional'] = material_alts['FUNCTIONAL_SCORE'] / 5.0
                material_alts['normalized_design'] = material_alts['DESIGN_SCORE'] / 5.0
                material_alts['normalized_cost'] = material_alts['COST_SCORE'] / 5.0
                
                # Calculate weighted score
                material_alts['weighted_score'] = (
                    material_alts['normalized_functional'] * 0.333 +
                    material_alts['normalized_design'] * 0.333 +
                    material_alts['normalized_cost'] * 0.334
                )
                
                # Find best weighted score
                best = material_alts.loc[material_alts['weighted_score'].idxmax()]
                selections[str(material_id)] = str(best['ALT_RANK'])
        
        return selections
    
    def save_presets(self, output_path: str = None):
        """Save presets to JSON file."""
        if output_path is None:
            output_path = self.data_dir / 'optimization_presets.json'
        
        presets = self.calculate_all_presets()
        
        with open(output_path, 'w') as f:
            json.dump(presets, f, indent=2)
        
        print(f"✅ Presets saved to {output_path}")
        return presets


def main():
    """Generate preset configurations."""
    print("Calculating optimization presets...")
    
    optimizer = PresetOptimizer()
    presets = optimizer.save_presets()
    
    print("\n" + "="*60)
    print("PRESET CONFIGURATIONS GENERATED")
    print("="*60)
    
    for preset_name, selections in presets.items():
        total_materials = len(selections)
        alternatives_selected = sum(1 for rank in selections.values() if rank != '0')
        
        print(f"\n{preset_name.upper().replace('_', ' ')}:")
        print(f"  Total materials: {total_materials}")
        print(f"  Alternatives selected: {alternatives_selected}")
        print(f"  Originals kept: {total_materials - alternatives_selected}")
    
    print("\n" + "="*60)
    print(f"Presets saved to: data/processed/optimization_presets.json")
    print("="*60)


if __name__ == "__main__":
    main()


