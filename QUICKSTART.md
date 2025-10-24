# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 2: Run the Workflow

```bash
# Option A: Use the quick start script
./run.sh

# Option B: Run manually
python3 agent/workflow.py
```

This will:
- Load all project data
- Match materials to RSMeans costs
- Find cost-effective alternatives
- Evaluate alternatives with AI
- Generate 4 optimization strategies
- Export all results

**Expected Output:**
```
✅ Baseline Cost: $5,237,041
✅ Best Cost Strategy: $2,076,904 savings (39.66%)
✅ Balanced Strategy: $1,227,829 savings (23.45%)
```

### Step 3: View the Dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser to explore:
- 4 optimization strategies
- Cost savings breakdown
- Material selections with scores
- Strategy comparisons

## 📊 What You Get

### 4 Optimization Strategies

1. **Best Functional** (🎯)
   - Maintains original functionality
   - 0% cost reduction
   - Perfect functional scores

2. **Best Cost** (💵)
   - **39.66% cost reduction**
   - **$2,076,904 savings**
   - Good functional scores (3.95/5.0)

3. **Best Design** (🎨)
   - Preserves design intent
   - 0% cost reduction
   - Perfect design scores

4. **Balanced** (⚖️) - **RECOMMENDED**
   - **23.45% cost reduction**
   - **$1,227,829 savings**
   - Excellent scores (4.96/5.0)

### Generated Files

All results saved to `data/processed/`:

```
data/processed/
├── matched_windows.csv                    # Initial matches
├── matched_doors.csv
├── matched_appliances.csv
├── window_alternatives_scored.csv         # Alternatives with scores
├── door_alternatives_scored.csv
├── appliance_alternatives_scored.csv
└── optimization/                          # Final selections
    ├── best_cost_metrics.csv
    ├── best_cost_windows_selections.csv
    ├── best_cost_doors_selections.csv
    ├── best_cost_appliances_selections.csv
    ├── balanced_metrics.csv
    ├── balanced_windows_selections.csv
    ├── ... (and more)
```

## 🔧 Configuration

### Using Claude for Better Evaluations

To enable AI-powered evaluation instead of heuristics:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
python3 agent/workflow.py
```

Without the API key, the system uses smart heuristics based on:
- Material type matching
- Dimension similarity
- Style consistency

## 📝 Testing

Each module can be tested independently:

```bash
# Test data loading
python3 test/test_data_loader.py

# Test material matching
python3 test/test_material_matcher.py

# Run individual modules
python3 agent/material_matcher.py
python3 agent/alternatives_finder.py
python3 agent/optimizer.py
```

## 💡 Understanding the Results

### Cost Reduction Score (1-5)

| Score | Reduction | Example |
|-------|-----------|---------|
| 5 | 30%+ | $1,000 → $699 |
| 4 | 20-30% | $1,000 → $799 |
| 3 | 15-20% | $1,000 → $849 |
| 2 | 10-15% | $1,000 → $899 |
| 1 | 5-10% | $1,000 → $949 |

### Functional Score (1-5)

- **5**: Same or better functionality
- **4**: Very similar with minor differences
- **3**: Moderate differences
- **2**: Significant compromises
- **1**: Major functional changes

### Design Score (1-5)

- **5**: Same or better design aesthetic
- **4**: Very similar with minor differences
- **3**: Moderate design changes
- **2**: Significant design compromises
- **1**: Major design intent deviation

## 🎯 Recommended Strategy

For most projects, we recommend the **Balanced** strategy:

✅ **$1.2M+ savings (23% reduction)**
✅ **Near-perfect functional scores (4.96/5.0)**
✅ **Near-perfect design scores (4.96/5.0)**
✅ **Good cost reduction (1.46/5.0)**

This provides substantial cost savings while maintaining the project's functional requirements and design intent.

## 📚 Next Steps

1. **Review Results**: Open the dashboard to explore all strategies
2. **Customize Weights**: Edit `optimizer.py` to add custom strategies
3. **Export Data**: Use CSV files for further analysis
4. **Iterate**: Adjust alternatives and re-run optimization

## 🆘 Troubleshooting

### "No module named 'pandas'"
```bash
pip install -r requirements.txt
```

### "No optimization results found"
```bash
python3 agent/workflow.py
```

### Dashboard not loading
```bash
# Make sure results exist
ls data/processed/optimization/

# Restart streamlit
streamlit run app.py
```

## 📖 Documentation

- **README.md**: Complete project documentation
- **DATA_CODE_MAP.md**: Detailed data flow and code connections
- **instruction.md**: Original project requirements

## 🤝 Contributing

To add new features:

1. Add module to `agent/`
2. Create test in `test/`
3. Update `workflow.py` to integrate
4. Run tests and verify results

---

**Need Help?** Check the full README.md or open a GitHub issue.


