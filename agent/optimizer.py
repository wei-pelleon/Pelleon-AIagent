"""
Optimizer module - selects optimal alternatives based on different strategies.

Strategies:
1. Best Functional: Prioritize functional score
2. Best Cost: Prioritize cost reduction score
3. Best Design: Prioritize design score
4. Balanced: Equal weight to all three criteria (1/3 each)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class VEOptimizer:
    """Value Engineering optimizer for material selection."""
    
    def __init__(self, evaluated_alternatives: Dict[str, pd.DataFrame],
                 matched_materials: Dict[str, pd.DataFrame]):
        self.evaluated_alts = evaluated_alternatives
        self.matched_materials = matched_materials
        
    def optimize_all_strategies(self) -> Dict[str, Dict]:
        """Run all optimization strategies and return results."""
        strategies = {
            'best_functional': {'functional': 1.0, 'design': 0.0, 'cost': 0.0},
            'best_cost': {'functional': 0.0, 'design': 0.0, 'cost': 1.0},
            'best_design': {'functional': 0.0, 'design': 1.0, 'cost': 0.0},
            'balanced': {'functional': 1/3, 'design': 1/3, 'cost': 1/3},
        }
        
        results = {}
        for strategy_name, weights in strategies.items():
            results[strategy_name] = self._optimize_with_weights(
                weights['functional'], weights['design'], weights['cost']
            )
        
        return results
    
    def _optimize_with_weights(self, w_func: float, w_design: float, 
                                w_cost: float) -> Dict:
        """Optimize material selection with given weights."""
        # Select best alternative for each material
        window_selections = self._select_best(
            self.evaluated_alts['window_alternatives'],
            w_func, w_design, w_cost
        )
        door_selections = self._select_best(
            self.evaluated_alts['door_alternatives'],
            w_func, w_design, w_cost
        )
        appliance_selections = self._select_best(
            self.evaluated_alts['appliance_alternatives'],
            w_func, w_design, w_cost
        )
        
        # Calculate aggregated metrics
        window_metrics = self._calculate_category_metrics(
            window_selections, self.matched_materials['windows']
        )
        door_metrics = self._calculate_category_metrics(
            door_selections, self.matched_materials['doors']
        )
        appliance_metrics = self._calculate_category_metrics(
            appliance_selections, self.matched_materials['appliances']
        )
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics([
            window_metrics, door_metrics, appliance_metrics
        ])
        
        return {
            'selections': {
                'windows': window_selections,
                'doors': door_selections,
                'appliances': appliance_selections,
            },
            'metrics': {
                'windows': window_metrics,
                'doors': door_metrics,
                'appliances': appliance_metrics,
                'overall': overall_metrics,
            }
        }
    
    def _select_best(self, alternatives_df: pd.DataFrame,
                     w_func: float, w_design: float, w_cost: float) -> pd.DataFrame:
        """Select the best alternative for each material based on weighted score."""
        df = alternatives_df.copy()
        
        # Calculate weighted score
        df['WEIGHTED_SCORE'] = (
            df['FUNCTIONAL_SCORE'] * w_func +
            df['DESIGN_SCORE'] * w_design +
            df['COST_SCORE'] * w_cost
        )
        
        # For each material, select the alternative with highest weighted score
        selected = []
        for material_id in df['MATERIAL_ID'].unique():
            material_alts = df[df['MATERIAL_ID'] == material_id]
            best_alt = material_alts.loc[material_alts['WEIGHTED_SCORE'].idxmax()]
            selected.append(best_alt)
        
        return pd.DataFrame(selected)
    
    def _calculate_category_metrics(self, selections: pd.DataFrame,
                                     original_materials: pd.DataFrame) -> Dict:
        """Calculate metrics for a material category."""
        # Get cost column name (different for appliances)
        if 'TOTAL_COST' in original_materials.columns:
            cost_col = 'TOTAL_COST'
        elif 'TOTAL_COST_ORIGINAL' in original_materials.columns:
            cost_col = 'TOTAL_COST_ORIGINAL'
        else:
            cost_col = 'TOTAL_COST'  # fallback
        
        # Merge with original materials to get quantities
        merge_cols = ['MATERIAL_ID', 'QUANTITY']
        if cost_col in original_materials.columns:
            merge_cols.append(cost_col)
        
        merged = selections.merge(
            original_materials[merge_cols],
            on='MATERIAL_ID',
            how='left',
            suffixes=('', '_orig')
        )
        
        # Calculate totals
        total_original_cost = merged['ORIGINAL_COST'].multiply(
            merged['QUANTITY'], fill_value=0
        ).sum()
        
        total_selected_cost = merged['ALT_COST_TOTAL'].multiply(
            merged['QUANTITY'], fill_value=0
        ).sum()
        
        total_cost_savings = total_original_cost - total_selected_cost
        cost_reduction_pct = (total_cost_savings / total_original_cost * 100) if total_original_cost > 0 else 0
        
        # Calculate average scores (weighted by quantity)
        total_quantity = merged['QUANTITY'].sum()
        if total_quantity > 0:
            avg_functional = (merged['FUNCTIONAL_SCORE'] * merged['QUANTITY']).sum() / total_quantity
            avg_design = (merged['DESIGN_SCORE'] * merged['QUANTITY']).sum() / total_quantity
            avg_cost_score = (merged['COST_SCORE'] * merged['QUANTITY']).sum() / total_quantity
        else:
            avg_functional = 0
            avg_design = 0
            avg_cost_score = 0
        
        return {
            'total_original_cost': total_original_cost,
            'total_selected_cost': total_selected_cost,
            'total_cost_savings': total_cost_savings,
            'cost_reduction_pct': cost_reduction_pct,
            'avg_functional_score': avg_functional,
            'avg_design_score': avg_design,
            'avg_cost_score': avg_cost_score,
            'num_materials': len(selections),
        }
    
    def _calculate_overall_metrics(self, category_metrics: List[Dict]) -> Dict:
        """Calculate overall metrics across all categories."""
        total_original = sum(m['total_original_cost'] for m in category_metrics)
        total_selected = sum(m['total_selected_cost'] for m in category_metrics)
        total_savings = total_original - total_selected
        overall_reduction = (total_savings / total_original * 100) if total_original > 0 else 0
        
        # Calculate weighted average scores
        total_num = sum(m['num_materials'] for m in category_metrics)
        if total_num > 0:
            avg_functional = sum(
                m['avg_functional_score'] * m['num_materials'] for m in category_metrics
            ) / total_num
            avg_design = sum(
                m['avg_design_score'] * m['num_materials'] for m in category_metrics
            ) / total_num
            avg_cost_score = sum(
                m['avg_cost_score'] * m['num_materials'] for m in category_metrics
            ) / total_num
        else:
            avg_functional = 0
            avg_design = 0
            avg_cost_score = 0
        
        return {
            'total_original_cost': total_original,
            'total_selected_cost': total_selected,
            'total_cost_savings': total_savings,
            'cost_reduction_pct': overall_reduction,
            'avg_functional_score': avg_functional,
            'avg_design_score': avg_design,
            'avg_cost_score': avg_cost_score,
        }
    
    def export_results(self, results: Dict[str, Dict], output_dir: str):
        """Export optimization results to CSV files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for strategy_name, strategy_results in results.items():
            # Save selections
            selections = strategy_results['selections']
            for category, df in selections.items():
                filepath = f"{output_dir}/{strategy_name}_{category}_selections.csv"
                df.to_csv(filepath, index=False)
            
            # Save metrics summary
            metrics = strategy_results['metrics']
            metrics_rows = []
            
            for category in ['windows', 'doors', 'appliances', 'overall']:
                m = metrics[category]
                metrics_rows.append({
                    'Category': category.title(),
                    'Original Cost': f"${m['total_original_cost']:,.2f}",
                    'Selected Cost': f"${m['total_selected_cost']:,.2f}",
                    'Cost Savings': f"${m['total_cost_savings']:,.2f}",
                    'Cost Reduction %': f"{m['cost_reduction_pct']:.2f}%",
                    'Avg Functional Score': f"{m['avg_functional_score']:.2f}",
                    'Avg Design Score': f"{m['avg_design_score']:.2f}",
                    'Avg Cost Score': f"{m['avg_cost_score']:.2f}",
                })
            
            metrics_df = pd.DataFrame(metrics_rows)
            metrics_df.to_csv(f"{output_dir}/{strategy_name}_metrics.csv", index=False)


def main():
    """Test the optimizer."""
    from data_loader import DataLoader
    from material_matcher import MaterialMatcher
    from alternatives_finder import AlternativesFinder
    from llm_evaluator import LLMEvaluator
    
    # Load and process
    print("Loading data...")
    loader = DataLoader()
    data = loader.load_all()
    
    print("Matching materials...")
    matcher = MaterialMatcher(data)
    matched_materials = {
        'windows': matcher.match_windows(),
        'doors': matcher.match_doors(),
        'appliances': matcher.match_appliances(),
    }
    
    print("Finding alternatives...")
    finder = AlternativesFinder(data, matched_materials)
    alternatives = finder.find_all_alternatives()
    
    print("Evaluating alternatives...")
    evaluator = LLMEvaluator()
    evaluated = evaluator.evaluate_alternatives(alternatives)
    
    print("Optimizing selections...")
    optimizer = VEOptimizer(evaluated, matched_materials)
    results = optimizer.optimize_all_strategies()
    
    # Print summary
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS SUMMARY")
    print("="*80)
    
    for strategy_name, strategy_results in results.items():
        print(f"\n{strategy_name.upper().replace('_', ' ')}:")
        print("-" * 80)
        metrics = strategy_results['metrics']['overall']
        print(f"  Original Cost:     ${metrics['total_original_cost']:>15,.2f}")
        print(f"  Optimized Cost:    ${metrics['total_selected_cost']:>15,.2f}")
        print(f"  Cost Savings:      ${metrics['total_cost_savings']:>15,.2f}")
        print(f"  Reduction:         {metrics['cost_reduction_pct']:>15.2f}%")
        print(f"  Avg Functional:    {metrics['avg_functional_score']:>15.2f} / 5.0")
        print(f"  Avg Design:        {metrics['avg_design_score']:>15.2f} / 5.0")
        print(f"  Avg Cost Score:    {metrics['avg_cost_score']:>15.2f} / 5.0")
    
    # Export results
    print("\nExporting results...")
    optimizer.export_results(results, '/app/data/processed/optimization')
    
    print("\n✅ Optimization complete! Results saved to data/processed/optimization/")


if __name__ == "__main__":
    main()

