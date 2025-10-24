# VE Agent UI - User Guide

## 🎨 Overview

The VE Agent UI provides an interactive interface for selecting material alternatives and viewing real-time cost and quality metrics.

## 🚀 Launching the UI

```bash
cd ux
npm run dev
```

The UI will automatically open at **http://localhost:3000**

## 📊 Main Components

### 1. Summary Panel (Top)

Shows real-time aggregated metrics:

**Overall Metrics:**
- Total Original Cost
- Total Selected Cost
- Total Savings (with percentage)

**Average Scores:**
- Functional Deviation (1-5 scale, 5 = best)
- Design Deviation (1-5 scale, 5 = best)
- Cost Reduction (percentage)

**Category Breakdown:**
- Separate metrics for Windows, Doors, and Appliances

### 2. Material Cards (Below)

Each material displays:
- **Material ID**: Unique identifier (e.g., W2, Door-1, Refrigerator)
- **Material Type**: Category classification
- **Original**: Description and cost of original material
- **Alternative Selector**: Dropdown to choose alternatives

When you select an alternative, it expands to show:
- Full description
- Functional score (how well it maintains function)
- Design score (how well it preserves design intent)
- Cost reduction percentage
- Cost comparison (original vs alternative vs savings)

## 🎯 How to Use

### Basic Workflow

1. **Review Original Materials**
   - Scroll through all materials organized by category
   - Each card shows the original specification

2. **Select Alternatives**
   - Click any dropdown menu
   - Choose from up to 3 alternatives
   - Or keep the original

3. **View Details**
   - When an alternative is selected, see:
     - Functional & Design scores
     - Cost reduction
     - Detailed cost breakdown

4. **Monitor Overall Impact**
   - The summary panel updates automatically
   - See total savings and average scores
   - Check category-specific metrics

### Making Selections

**Example:** Selecting a window alternative

1. Find window card (e.g., "W2")
2. Original shows: "Wood casement 5'-11" x 5'-2"" - $1,715.00
3. Click dropdown: Select "Alternative 1"
4. View expanded details:
   - Functional: 4 / 5 (good)
   - Design: 3 / 5 (moderate)
   - Cost Reduction: 22.2%
   - Savings: $380.00

5. Summary panel updates showing new totals

## 📈 Understanding Scores

### Functional Score (1-5)
- **5**: Perfect - maintains all functionality
- **4**: Excellent - minor functional differences
- **3**: Good - moderate differences
- **2**: Fair - significant compromises
- **1**: Poor - major functional changes

### Design Score (1-5)
- **5**: Perfect - maintains design intent
- **4**: Excellent - minor aesthetic differences
- **3**: Good - moderate design changes
- **2**: Fair - significant design compromises
- **1**: Poor - major design deviation

### Cost Reduction
- Percentage saved compared to original
- Higher is better
- Color coded:
  - Green: 20%+ savings
  - Amber: 10-20% savings
  - Blue: 0-10% savings

## 🎨 Color Coding

**Score Quality:**
- 🟢 Green (4.5-5.0): Excellent
- 🟡 Yellow (3.5-4.4): Good
- 🔴 Red (<3.5): Needs attention

**Cost Savings:**
- 🟢 Green: High savings (20%+)
- 🟡 Amber: Moderate savings (10-20%)
- 🔵 Blue: Some savings (<10%)

## 💡 Tips

### Finding Best Value
1. Look for alternatives with:
   - Green functional & design scores (4.5+)
   - High cost reduction percentage

2. Check the summary panel:
   - Aim for overall savings while maintaining quality
   - Balance functional and design scores

### Category Strategy
- **Windows**: Focus on maintaining functional scores (ventilation)
- **Doors**: Prioritize functional scores (security, insulation)
- **Appliances**: Usually safe to select alternatives (uniform discounts)

### Resetting Selections
- Choose "Keep Original" from any dropdown
- This resets that material to original specification

## 📱 Responsive Design

The UI works on all screen sizes:
- **Desktop**: Full grid layout
- **Tablet**: 2-column layout
- **Mobile**: Single column, optimized for touch

## 🔄 Real-time Updates

All metrics update instantly when you change selections:
- Total costs recalculate
- Average scores adjust
- Category breakdowns refresh

No need to click "Update" or "Calculate" - it's automatic!

## 📁 Data Source

The UI reads from these CSV files:
```
data/processed/
├── window_alternatives_scored.csv
├── door_alternatives_scored.csv
└── appliance_alternatives_scored.csv
```

**Important:** Run the Python pipeline first to generate these files:
```bash
cd ..
python3 agent/workflow.py
```

## 🎯 Example Scenarios

### Scenario 1: Maximum Cost Savings
1. Go through each material
2. Select the alternative with highest cost reduction
3. Watch total savings grow in summary panel
4. Review functional/design scores to ensure quality

### Scenario 2: Balanced Approach
1. Filter for alternatives with:
   - Functional score ≥ 4.0
   - Design score ≥ 4.0
   - Cost reduction ≥ 10%
2. Select these balanced alternatives
3. Achieve good savings while maintaining quality

### Scenario 3: Quality First
1. Only select alternatives with:
   - Functional score = 5.0
   - Design score = 5.0
2. Accept whatever cost reduction comes with it
3. Maintain perfect quality standards

## 🐛 Troubleshooting

### UI won't load
- Check that CSV files exist in `data/processed/`
- Run Python pipeline if files are missing
- Check browser console for errors (F12)

### Metrics not updating
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Restart dev server

### Slow performance
- Modern browser recommended (Chrome, Firefox, Safari, Edge)
- Close other tabs to free memory
- Check for browser extensions that might interfere

## 🎓 Advanced Features

### Keyboard Navigation
- Tab: Move between dropdowns
- Arrow keys: Navigate dropdown options
- Enter: Select highlighted option

### Browser DevTools
- F12: Open developer console
- View real-time state changes
- Debug any issues

## 📊 Expected Results

With smart selections, you should see:
- **Total Savings**: 15-40% of original cost
- **Avg Functional**: 4.0-5.0
- **Avg Design**: 4.0-5.0
- **Cost Reduction**: 10-30%

This represents a balanced optimization - significant savings with minimal quality compromise.

---

**Ready to optimize!** Open http://localhost:3000 and start selecting alternatives! 🚀


