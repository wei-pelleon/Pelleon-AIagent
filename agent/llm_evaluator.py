"""
LLM evaluator module - uses Claude to evaluate alternatives on 3 criteria:
1. Functional deviation (1-5, 5 = most faithful to original function)
2. Design deviation (1-5, 5 = most faithful to original design intent)
3. Cost reduction score (1-5, based on reduction percentage)
"""
import pandas as pd
from anthropic import Anthropic
import os
import json
from typing import Dict, List, Optional
import time


class LLMEvaluator:
    """Evaluates material alternatives using Claude LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️  No ANTHROPIC_API_KEY found. Using mock evaluations.")
    
    def evaluate_alternatives(self, alternatives: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Evaluate all alternatives and add scores."""
        results = {}
        
        # Evaluate windows
        print("Evaluating window alternatives...")
        results['window_alternatives'] = self._evaluate_window_alts(
            alternatives['window_alternatives']
        )
        
        # Evaluate doors
        print("Evaluating door alternatives...")
        results['door_alternatives'] = self._evaluate_door_alts(
            alternatives['door_alternatives']
        )
        
        # Appliances - predefined scores
        print("Evaluating appliance alternatives...")
        results['appliance_alternatives'] = self._evaluate_appliance_alts(
            alternatives['appliance_alternatives']
        )
        
        return results
    
    def _evaluate_window_alts(self, window_alts: pd.DataFrame) -> pd.DataFrame:
        """Evaluate window alternatives."""
        df = window_alts.copy()
        
        # Add score columns
        df['FUNCTIONAL_SCORE'] = 0
        df['DESIGN_SCORE'] = 0
        df['COST_SCORE'] = 0
        
        # Group by material ID
        for material_id in df['MATERIAL_ID'].unique():
            material_df = df[df['MATERIAL_ID'] == material_id].copy()
            
            # Original always gets 5, 5, 1 (no cost reduction)
            original_mask = (df['MATERIAL_ID'] == material_id) & (df['ALT_RANK'] == 0)
            df.loc[original_mask, 'FUNCTIONAL_SCORE'] = 5
            df.loc[original_mask, 'DESIGN_SCORE'] = 5
            df.loc[original_mask, 'COST_SCORE'] = 1
            
            # Evaluate alternatives
            alternatives = material_df[material_df['ALT_RANK'] > 0]
            for _, alt in alternatives.iterrows():
                scores = self._get_window_scores(
                    original_desc=material_df[material_df['ALT_RANK'] == 0].iloc[0]['ALT_DESC'],
                    alt_desc=alt['ALT_DESC'],
                    cost_reduction=alt['COST_REDUCTION_PCT']
                )
                
                alt_mask = (df['MATERIAL_ID'] == material_id) & (df['ALT_RANK'] == alt['ALT_RANK'])
                df.loc[alt_mask, 'FUNCTIONAL_SCORE'] = scores['functional']
                df.loc[alt_mask, 'DESIGN_SCORE'] = scores['design']
                df.loc[alt_mask, 'COST_SCORE'] = scores['cost']
        
        return df
    
    def _evaluate_door_alts(self, door_alts: pd.DataFrame) -> pd.DataFrame:
        """Evaluate door alternatives."""
        df = door_alts.copy()
        
        # Add score columns
        df['FUNCTIONAL_SCORE'] = 0
        df['DESIGN_SCORE'] = 0
        df['COST_SCORE'] = 0
        
        # Group by material ID
        for material_id in df['MATERIAL_ID'].unique():
            material_df = df[df['MATERIAL_ID'] == material_id].copy()
            
            # Original always gets 5, 5, 1
            original_mask = (df['MATERIAL_ID'] == material_id) & (df['ALT_RANK'] == 0)
            df.loc[original_mask, 'FUNCTIONAL_SCORE'] = 5
            df.loc[original_mask, 'DESIGN_SCORE'] = 5
            df.loc[original_mask, 'COST_SCORE'] = 1
            
            # Evaluate alternatives
            alternatives = material_df[material_df['ALT_RANK'] > 0]
            for _, alt in alternatives.iterrows():
                scores = self._get_door_scores(
                    original_desc=material_df[material_df['ALT_RANK'] == 0].iloc[0]['ALT_DESC'],
                    alt_desc=alt['ALT_DESC'],
                    material_type=alt['MATERIAL_TYPE'],
                    cost_reduction=alt['COST_REDUCTION_PCT']
                )
                
                alt_mask = (df['MATERIAL_ID'] == material_id) & (df['ALT_RANK'] == alt['ALT_RANK'])
                df.loc[alt_mask, 'FUNCTIONAL_SCORE'] = scores['functional']
                df.loc[alt_mask, 'DESIGN_SCORE'] = scores['design']
                df.loc[alt_mask, 'COST_SCORE'] = scores['cost']
        
        return df
    
    def _evaluate_appliance_alts(self, app_alts: pd.DataFrame) -> pd.DataFrame:
        """Evaluate appliance alternatives (predefined scores)."""
        df = app_alts.copy()
        
        # Add score columns
        df['FUNCTIONAL_SCORE'] = 0
        df['DESIGN_SCORE'] = 0
        df['COST_SCORE'] = 0
        
        # Original: 5, 5, 1
        df.loc[df['ALT_RANK'] == 0, 'FUNCTIONAL_SCORE'] = 5
        df.loc[df['ALT_RANK'] == 0, 'DESIGN_SCORE'] = 5
        df.loc[df['ALT_RANK'] == 0, 'COST_SCORE'] = 1
        
        # 10% reduction: 5, 5, 2 (same function/design, 10% cost reduction)
        df.loc[df['ALT_RANK'] == 1, 'FUNCTIONAL_SCORE'] = 5
        df.loc[df['ALT_RANK'] == 1, 'DESIGN_SCORE'] = 5
        df.loc[df['ALT_RANK'] == 1, 'COST_SCORE'] = 2
        
        return df
    
    def _get_window_scores(self, original_desc: str, alt_desc: str, 
                           cost_reduction: float) -> Dict[str, int]:
        """Get scores for a window alternative."""
        # Calculate cost score based on reduction percentage
        cost_score = self._cost_reduction_to_score(cost_reduction)
        
        if self.client:
            # Use LLM to evaluate functional and design scores
            prompt = f"""You are evaluating a window alternative for a construction project.

Original window: {original_desc}
Alternative window: {alt_desc}
Cost reduction: {cost_reduction:.1f}%

Please evaluate the alternative on two criteria:

1. Functional deviation (1-5 scale):
   - 5: Same or better functionality (ventilation, light, etc.)
   - 4: Very similar functionality with minor differences
   - 3: Moderate functional differences
   - 2: Significant functional differences
   - 1: Major functional compromises

2. Design deviation (1-5 scale):
   - 5: Same or better design aesthetic and intent
   - 4: Very similar design with minor aesthetic differences
   - 3: Moderate design differences but acceptable
   - 2: Significant design compromises
   - 1: Major design intent deviation

Respond ONLY with a JSON object in this format:
{{"functional": X, "design": Y}}

Where X and Y are integers from 1 to 5."""

            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse response
                content = response.content[0].text.strip()
                # Extract JSON from response
                if '```' in content:
                    content = content.split('```')[1].replace('json', '').strip()
                
                scores = json.loads(content)
                return {
                    'functional': int(scores['functional']),
                    'design': int(scores['design']),
                    'cost': cost_score
                }
            except Exception as e:
                print(f"  Error evaluating with LLM: {e}, using heuristic")
                # Fallback to heuristic
                return self._heuristic_window_scores(original_desc, alt_desc, cost_score)
        else:
            # Use heuristic scoring
            return self._heuristic_window_scores(original_desc, alt_desc, cost_score)
    
    def _get_door_scores(self, original_desc: str, alt_desc: str,
                         material_type: str, cost_reduction: float) -> Dict[str, int]:
        """Get scores for a door alternative."""
        cost_score = self._cost_reduction_to_score(cost_reduction)
        
        if self.client:
            prompt = f"""You are evaluating a door alternative for a construction project.

Original door: {original_desc}
Door type: {material_type}
Alternative door: {alt_desc}
Cost reduction: {cost_reduction:.1f}%

Please evaluate the alternative on two criteria:

1. Functional deviation (1-5 scale):
   - 5: Same or better functionality (security, access, insulation)
   - 4: Very similar functionality with minor differences
   - 3: Moderate functional differences
   - 2: Significant functional differences
   - 1: Major functional compromises

2. Design deviation (1-5 scale):
   - 5: Same or better design aesthetic and intent
   - 4: Very similar design with minor aesthetic differences
   - 3: Moderate design differences but acceptable
   - 2: Significant design compromises
   - 1: Major design intent deviation

Respond ONLY with a JSON object in this format:
{{"functional": X, "design": Y}}

Where X and Y are integers from 1 to 5."""

            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text.strip()
                if '```' in content:
                    content = content.split('```')[1].replace('json', '').strip()
                
                scores = json.loads(content)
                return {
                    'functional': int(scores['functional']),
                    'design': int(scores['design']),
                    'cost': cost_score
                }
            except Exception as e:
                print(f"  Error evaluating with LLM: {e}, using heuristic")
                return self._heuristic_door_scores(original_desc, alt_desc, material_type, cost_score)
        else:
            return self._heuristic_door_scores(original_desc, alt_desc, material_type, cost_score)
    
    def _heuristic_window_scores(self, original_desc: str, alt_desc: str, 
                                  cost_score: int) -> Dict[str, int]:
        """Heuristic scoring for windows when LLM is not available."""
        original_lower = original_desc.lower()
        alt_lower = alt_desc.lower()
        
        # Check if same window type
        window_types = ['casement', 'sliding', 'fixed', 'awning', 'double hung']
        same_type = any(wtype in original_lower and wtype in alt_lower for wtype in window_types)
        
        # Check if same material
        same_material = (
            ('wood' in original_lower and 'wood' in alt_lower) or
            ('vinyl' in original_lower and 'vinyl' in alt_lower) or
            ('aluminum' in original_lower and 'aluminum' in alt_lower)
        )
        
        # Heuristic scoring
        if same_type and same_material:
            functional = 5
            design = 5
        elif same_type:
            functional = 4
            design = 3
        else:
            functional = 3
            design = 3
        
        return {'functional': functional, 'design': design, 'cost': cost_score}
    
    def _heuristic_door_scores(self, original_desc: str, alt_desc: str,
                               material_type: str, cost_score: int) -> Dict[str, int]:
        """Heuristic scoring for doors when LLM is not available."""
        original_lower = original_desc.lower()
        alt_lower = alt_desc.lower()
        
        # Check material similarity
        same_material = (
            ('wood' in original_lower and 'wood' in alt_lower) or
            ('metal' in original_lower and 'metal' in alt_lower) or
            ('glass' in original_lower and 'glass' in alt_lower)
        )
        
        # Heuristic scoring
        if same_material:
            functional = 4
            design = 4
        else:
            functional = 3
            design = 3
        
        return {'functional': functional, 'design': design, 'cost': cost_score}
    
    def _cost_reduction_to_score(self, reduction_pct: float) -> int:
        """Convert cost reduction percentage to 1-5 score."""
        if reduction_pct >= 30:
            return 5
        elif reduction_pct >= 20:
            return 4
        elif reduction_pct >= 15:
            return 3
        elif reduction_pct >= 10:
            return 2
        elif reduction_pct >= 5:
            return 1
        else:
            return 1


def main():
    """Test the LLM evaluator."""
    from data_loader import DataLoader
    from material_matcher import MaterialMatcher
    from alternatives_finder import AlternativesFinder
    
    # Load and process
    loader = DataLoader()
    data = loader.load_all()
    
    matcher = MaterialMatcher(data)
    matched_materials = {
        'windows': matcher.match_windows(),
        'doors': matcher.match_doors(),
        'appliances': matcher.match_appliances(),
    }
    
    finder = AlternativesFinder(data, matched_materials)
    alternatives = finder.find_all_alternatives()
    
    # Evaluate
    evaluator = LLMEvaluator()
    evaluated = evaluator.evaluate_alternatives(alternatives)
    
    print("="*60)
    print("EVALUATED WINDOW ALTERNATIVES")
    print("="*60)
    print(evaluated['window_alternatives'][['MATERIAL_ID', 'ALT_RANK', 'ALT_DESC', 
                                             'COST_REDUCTION_PCT', 'FUNCTIONAL_SCORE', 
                                             'DESIGN_SCORE', 'COST_SCORE']].head(15).to_string())
    
    print("\n" + "="*60)
    print("EVALUATED DOOR ALTERNATIVES")
    print("="*60)
    print(evaluated['door_alternatives'][['MATERIAL_ID', 'ALT_RANK', 'ALT_DESC', 
                                           'COST_REDUCTION_PCT', 'FUNCTIONAL_SCORE', 
                                           'DESIGN_SCORE', 'COST_SCORE']].head(15).to_string())
    
    print("\n" + "="*60)
    print("EVALUATED APPLIANCE ALTERNATIVES")
    print("="*60)
    print(evaluated['appliance_alternatives'][['MATERIAL_ID', 'ALT_RANK', 'ALT_DESC', 
                                                'COST_REDUCTION_PCT', 'FUNCTIONAL_SCORE', 
                                                'DESIGN_SCORE', 'COST_SCORE']].head(10).to_string())
    
    # Save
    evaluated['window_alternatives'].to_csv(
        '/app/data/processed/window_alternatives_scored.csv', index=False
    )
    evaluated['door_alternatives'].to_csv(
        '/app/data/processed/door_alternatives_scored.csv', index=False
    )
    evaluated['appliance_alternatives'].to_csv(
        '/app/data/processed/appliance_alternatives_scored.csv', index=False
    )
    
    print("\n✅ Evaluated alternatives saved to data/processed/")


if __name__ == "__main__":
    main()


