# VE Agent - Value Engineering Optimizer

A comprehensive value engineering system for construction materials that analyzes costs, finds alternatives, and optimizes material selections using AI-powered evaluation.

## Overview

This system helps optimize construction costs by:
1. Matching project materials (windows, doors, appliances) to RSMeans cost data
2. Finding cost-effective alternatives
3. Using LLM (Claude) to evaluate alternatives on functional/design/cost criteria
4. Providing 4 optimization strategies with detailed cost-benefit analysis

## Features

- **Automated Material Matching**: Intelligently matches project specifications to RSMeans cost database
- **Alternative Discovery**: Finds up to 3 alternatives per material based on similarity and cost
- **AI Evaluation**: Uses Claude LLM to score alternatives on:
  - Functional deviation (1-5)
  - Design deviation (1-5)  
  - Cost reduction (1-5)
- **4 Optimization Strategies**:
  - Best Functional: Maintains original functionality
  - Best Cost: Maximizes cost savings (39.66% reduction)
  - Best Design: Preserves design intent
  - Balanced: Equal weights (23.45% reduction)
- **Interactive Dashboard**: Streamlit UI for exploring results

## Project Structure

```
VEAgent/
├── agent/                      # Core modules
│   ├── data_loader.py         # Loads all data files
│   ├── material_matcher.py    # Matches materials to RSMeans
│   ├── alternatives_finder.py # Finds cost alternatives
│   ├── llm_evaluator.py       # AI evaluation of alternatives
│   ├── optimizer.py           # Optimization algorithms
│   └── workflow.py            # Workflow orchestrator
├── data/                      # Input data
│   ├── apartment_specs.csv    # Unit specifications
│   ├── schedule/              # Material schedules
│   ├── counts/                # Material counts
│   └── processed/             # Generated results
├── rsmeans/                   # RSMeans cost database
├── test/                      # Test scripts
├── app.py                     # Streamlit dashboard
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Data Flow

### Input Data

1. **Apartment Specifications** (`data/apartment_specs.csv`)
   - Defines all apartment units by type
   - Total units determines material quantities

2. **Material Schedules** (`data/schedule/`)
   - `schedule_unit_doors.tsv`: Door specifications (MARK, TYPE, WIDTH, HEIGHT, MATERIAL)
   - `schedule_window.tsv`: Window specifications (MARK, STYLE, SIZE, MATERIAL)

3. **Material Counts** (`data/counts/`)
   - `count_unit_doors.tsv`: Door counts by unit type
   - `count_windows.tsv`: Window counts by facade
   - `count_appliance.tsv`: Appliance counts

4. **RSMeans Cost Data** (`rsmeans/`)
   - `rsmeams_B2020_ext_windows_unit_cost.tsv`: Window costs
   - `rsmeans_B2030_110_ext_doors_unit_cost.tsv`: Exterior door costs
   - `rsmenas_C1020_102_int_doors_unit_cost.tsv`: Interior door costs
   - `rsmeams_appliances_unit_cost.tsv`: Appliance costs

### Processing Pipeline

```
Load Data → Match Materials → Find Alternatives → Evaluate with LLM → Optimize → Export
```

1. **Load Data**: Parse all CSV/TSV files
2. **Match Materials**: 
   - Match each window/door/appliance to best RSMeans entry
   - Consider dimensions, materials, style
   - Calculate baseline costs
3. **Find Alternatives**:
   - Windows: Similar area (±30%), same style
   - Doors: Similar materials, height >7' for exterior
   - Appliances: Uniform 10% reduction
4. **Evaluate**:
   - Original always scores: Functional=5, Design=5, Cost=1
   - LLM evaluates alternatives on all 3 criteria
   - Cost score based on reduction %: 5=30%+, 4=20%+, 3=15%+, 2=10%+, 1=5%+
5. **Optimize**:
   - Apply 4 different weighting strategies
   - Select best alternative for each material
   - Calculate aggregated metrics

### Output Data

All results saved to `data/processed/`:

- `matched_*.csv`: Initial material matches with costs
- `*_alternatives.csv`: All alternatives found
- `*_alternatives_scored.csv`: Alternatives with LLM scores
- `optimization/`: Final selections and metrics by strategy

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Run Complete Workflow

```bash
# Set API key for LLM evaluation (optional - will use heuristics if not set)
export ANTHROPIC_API_KEY=your_key_here

# Run the complete pipeline
python3 agent/workflow.py
```

This will:
- Process all data
- Match materials
- Find alternatives  
- Evaluate with LLM
- Optimize selections
- Export results to `data/processed/`

**Expected Results:**
- Baseline Cost: $5,237,041
- Best Cost Strategy: **$2,076,904 savings (39.66%)**
- Balanced Strategy: **$1,227,829 savings (23.45%)**

### 2. Launch Dashboard

```bash
streamlit run app.py
```

Then open http://localhost:8501 to view the interactive dashboard.

### 3. Run Individual Modules

```bash
# Test data loader
python3 test/test_data_loader.py

# Test material matcher
python3 test/test_material_matcher.py

# Run any module directly
python3 agent/material_matcher.py
python3 agent/alternatives_finder.py
python3 agent/llm_evaluator.py
python3 agent/optimizer.py
```

## Module Details

### data_loader.py
Loads all project data files. Handles:
- CSV/TSV parsing
- Numeric cleaning (removes commas)
- Apartment unit filtering (Total Units > 0)
- Appliance file special format

### material_matcher.py
Matches project materials to RSMeans:
- **Windows**: Match by area, style (casement/sliding/etc), material (vinyl/wood/aluminum)
- **Doors**: 
  - Exterior: Match by width, contains "glass" for balcony doors
  - Interior: Match by material (wood/metal) and dimensions
- **Appliances**: Match by keywords (refrigerator, microwave, etc.)

Outputs: Matched materials with unit costs and total costs

### alternatives_finder.py
Finds cost-effective alternatives:
- **Windows**: Same style, area within 30%, cheaper
- **Doors**: 
  - Exterior: Height > 7', similar materials
  - Interior: Same material, width within 6"
- **Appliances**: Uniform 10% discount

Returns: Up to 3 alternatives per material

### llm_evaluator.py
Evaluates alternatives using Claude LLM:
- Functional score: How well it maintains original function (1-5)
- Design score: How well it preserves design intent (1-5)
- Cost score: Based on reduction % (1-5)

Falls back to heuristic scoring if no API key.

### optimizer.py
Selects optimal materials:
- Calculates weighted score per strategy
- Selects best alternative for each material
- Aggregates metrics by category and overall
- Exports selections and summaries

### workflow.py
Orchestrates complete pipeline:
- Sequential execution of all steps
- Progress tracking and timing
- Results export
- Summary reporting

## Cost Reduction Scoring

| Reduction % | Score |
|-------------|-------|
| 30%+        | 5     |
| 20-30%      | 4     |
| 15-20%      | 3     |
| 10-15%      | 2     |
| 5-10%       | 1     |

## Optimization Strategies

| Strategy | Weights | Use Case |
|----------|---------|----------|
| Best Functional | Functional: 100% | When function is critical |
| Best Cost | Cost: 100% | When budget is primary concern |
| Best Design | Design: 100% | When aesthetics matter most |
| Balanced | All: 33.3% | General purpose optimization |

## Testing

Each module has a corresponding test file in `test/`:
- `test_data_loader.py`: Verifies data loading
- `test_material_matcher.py`: Checks material matching

Run tests:
```bash
python3 test/test_data_loader.py
python3 test/test_material_matcher.py
```

## Results

Sample optimization results:

| Strategy | Cost Savings | Reduction % | Functional | Design |
|----------|-------------|-------------|------------|---------|
| Best Functional | $0 | 0% | 5.00 | 5.00 |
| **Best Cost** | **$2,076,904** | **39.66%** | 3.95 | 3.81 |
| Best Design | $0 | 0% | 5.00 | 5.00 |
| **Balanced** | **$1,227,829** | **23.45%** | 4.96 | 4.96 |

The **Balanced** strategy is recommended as it saves $1.2M+ (23%) while maintaining near-perfect functional and design scores.

## Future Enhancements

- Integrate full Temporal workflow for scalability
- Add more material categories (finishes, fixtures)
- Enhanced LLM prompting for better evaluations
- Material substitution constraints
- Cost trend analysis over time
- Export to construction management systems

## License

MIT

## Contact

For questions or issues, please open a GitHub issue.


