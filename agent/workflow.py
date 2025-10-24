"""
Simple workflow orchestrator for the VE Agent pipeline.
For MVP, we use a simple sequential workflow rather than full Temporal.
"""
import time
from typing import Dict, Optional
from data_loader import DataLoader
from material_matcher import MaterialMatcher
from alternatives_finder import AlternativesFinder
from llm_evaluator import LLMEvaluator
from optimizer import VEOptimizer


class VEWorkflow:
    """Orchestrates the complete VE analysis workflow."""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.api_key = anthropic_api_key
        self.results = {}
        
    def run_complete_workflow(self, output_dir: str = '/Users/weizhang/git/VEAgent/data/processed') -> Dict:
        """Run the complete VE workflow from start to finish."""
        print("\n" + "="*80)
        print("VALUE ENGINEERING WORKFLOW")
        print("="*80)
        
        # Step 1: Load Data
        print("\n[1/6] Loading project data...")
        start = time.time()
        loader = DataLoader()
        data = loader.load_all()
        print(f"  ✓ Loaded {len(data)} data sources in {time.time() - start:.2f}s")
        self.results['data'] = data
        
        # Step 2: Match Materials
        print("\n[2/6] Matching materials to RSMeans cost data...")
        start = time.time()
        matcher = MaterialMatcher(data)
        matched_materials = {
            'windows': matcher.match_windows(),
            'doors': matcher.match_doors(),
            'appliances': matcher.match_appliances(),
        }
        
        # Calculate baseline costs
        baseline_windows = matched_materials['windows']['TOTAL_COST'].sum()
        baseline_doors = matched_materials['doors']['TOTAL_COST'].sum()
        baseline_appliances = matched_materials['appliances']['TOTAL_COST_ORIGINAL'].sum()
        baseline_total = baseline_windows + baseline_doors + baseline_appliances
        
        print(f"  ✓ Matched {len(matched_materials['windows'])} windows: ${baseline_windows:,.2f}")
        print(f"  ✓ Matched {len(matched_materials['doors'])} doors: ${baseline_doors:,.2f}")
        print(f"  ✓ Matched {len(matched_materials['appliances'])} appliances: ${baseline_appliances:,.2f}")
        print(f"  ✓ Baseline total cost: ${baseline_total:,.2f}")
        print(f"  ✓ Completed in {time.time() - start:.2f}s")
        self.results['matched_materials'] = matched_materials
        self.results['baseline_cost'] = baseline_total
        
        # Save matched materials
        matched_materials['windows'].to_csv(f"{output_dir}/matched_windows.csv", index=False)
        matched_materials['doors'].to_csv(f"{output_dir}/matched_doors.csv", index=False)
        matched_materials['appliances'].to_csv(f"{output_dir}/matched_appliances.csv", index=False)
        
        # Step 3: Find Alternatives
        print("\n[3/6] Finding cost-effective alternatives...")
        start = time.time()
        finder = AlternativesFinder(data, matched_materials)
        alternatives = finder.find_all_alternatives()
        
        print(f"  ✓ Found alternatives for {len(alternatives['window_alternatives']['MATERIAL_ID'].unique())} window types")
        print(f"  ✓ Found alternatives for {len(alternatives['door_alternatives']['MATERIAL_ID'].unique())} door types")
        print(f"  ✓ Found alternatives for {len(alternatives['appliance_alternatives']['MATERIAL_ID'].unique())} appliance types")
        print(f"  ✓ Completed in {time.time() - start:.2f}s")
        self.results['alternatives'] = alternatives
        
        # Save alternatives
        alternatives['window_alternatives'].to_csv(f"{output_dir}/window_alternatives.csv", index=False)
        alternatives['door_alternatives'].to_csv(f"{output_dir}/door_alternatives.csv", index=False)
        alternatives['appliance_alternatives'].to_csv(f"{output_dir}/appliance_alternatives.csv", index=False)
        
        # Step 4: Evaluate with LLM
        print("\n[4/6] Evaluating alternatives with LLM...")
        start = time.time()
        evaluator = LLMEvaluator(api_key=self.api_key)
        evaluated = evaluator.evaluate_alternatives(alternatives)
        
        print(f"  ✓ Evaluated functional, design, and cost scores")
        print(f"  ✓ Completed in {time.time() - start:.2f}s")
        self.results['evaluated'] = evaluated
        
        # Save evaluated alternatives
        evaluated['window_alternatives'].to_csv(
            f"{output_dir}/window_alternatives_scored.csv", index=False
        )
        evaluated['door_alternatives'].to_csv(
            f"{output_dir}/door_alternatives_scored.csv", index=False
        )
        evaluated['appliance_alternatives'].to_csv(
            f"{output_dir}/appliance_alternatives_scored.csv", index=False
        )
        
        # Step 5: Optimize Selections
        print("\n[5/6] Optimizing material selections...")
        start = time.time()
        optimizer = VEOptimizer(evaluated, matched_materials)
        optimization_results = optimizer.optimize_all_strategies()
        
        print(f"  ✓ Generated 4 optimization strategies")
        print(f"  ✓ Completed in {time.time() - start:.2f}s")
        self.results['optimization'] = optimization_results
        
        # Step 6: Export Results
        print("\n[6/6] Exporting results...")
        start = time.time()
        optimizer.export_results(optimization_results, f"{output_dir}/optimization")
        print(f"  ✓ Saved optimization results to {output_dir}/optimization/")
        print(f"  ✓ Completed in {time.time() - start:.2f}s")
        
        # Print Summary
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE - RESULTS SUMMARY")
        print("="*80)
        
        for strategy_name, strategy_results in optimization_results.items():
            metrics = strategy_results['metrics']['overall']
            print(f"\n{strategy_name.upper().replace('_', ' ')}:")
            print(f"  Cost Savings:    ${metrics['total_cost_savings']:>12,.2f} ({metrics['cost_reduction_pct']:.2f}%)")
            print(f"  Functional Avg:  {metrics['avg_functional_score']:>12.2f} / 5.0")
            print(f"  Design Avg:      {metrics['avg_design_score']:>12.2f} / 5.0")
        
        print("\n" + "="*80)
        print(f"✅ All results saved to: {output_dir}")
        print("="*80 + "\n")
        
        return self.results


def main():
    """Run the complete workflow."""
    workflow = VEWorkflow()
    results = workflow.run_complete_workflow()
    print("🎉 Value Engineering analysis complete!")


if __name__ == "__main__":
    main()


