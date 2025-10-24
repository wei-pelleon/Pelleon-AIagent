# VE Agent UI

A beautiful, professional React-based user interface for the Value Engineering Agent.

## Features

- **Material Selection**: Interactive dropdown to select alternatives for each material
- **Real-time Updates**: Automatically recalculates metrics when selections change
- **Category Breakdown**: View metrics by Windows, Doors, and Appliances
- **Professional Design**: Clean white and light gray theme with intuitive layout
- **Responsive**: Works on desktop, tablet, and mobile devices

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Authentication (Optional)

**For Development (Skip Auth):**
- Auth is bypassed by default using `.env.development`
- No setup needed!

**For Production (AWS Cognito):**
1. Follow `COGNITO_SETUP.md` to create Cognito User Pool
2. Copy `.env.example` to `.env`
3. Add your Cognito credentials to `.env`
4. Remove or set `VITE_SKIP_AUTH=false` in `.env.development`

### 3. Start Development Server
```bash
npm run dev
```

The UI will open automatically at http://localhost:3000

## Usage

### Viewing Materials
- The UI displays all materials grouped by category (Windows, Doors, Appliances)
- Each material card shows:
  - Material ID and type
  - Original material description and cost
  - Alternative selector dropdown

### Selecting Alternatives
1. Click the dropdown menu for any material
2. Choose an alternative (or keep original)
3. View the detailed metrics:
   - Functional deviation score (1-5)
   - Design deviation score (1-5)
   - Cost reduction percentage
   - Cost comparison and savings

### Understanding the Summary Panel
The top summary panel shows:
- **Total Original Cost**: Sum of all original material costs
- **Total Selected Cost**: Sum of currently selected alternatives
- **Total Savings**: Money saved from selections
- **Average Scores**: Weighted averages for functional, design, and cost reduction
- **Category Breakdown**: Metrics for Windows, Doors, and Appliances separately

## Data Source

The UI reads from CSV files in `../data/processed/`:
- `window_alternatives_scored.csv`
- `door_alternatives_scored.csv`
- `appliance_alternatives_scored.csv`

Make sure you've run the Python pipeline first to generate these files:
```bash
cd ..
python3 agent/workflow.py
```

## Color Coding

### Scores (Functional & Design)
- 🟢 Green (4.5-5.0): Excellent - minimal deviation
- 🟡 Amber (3.5-4.4): Good - moderate deviation
- 🔴 Red (<3.5): Poor - significant deviation

### Cost Reduction
- 🟢 Green (20%+): Excellent savings
- 🟡 Amber (10-20%): Good savings
- 🔵 Blue (>0%): Some savings
- ⚫ Gray (0%): No savings

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

## Project Structure

```
ux/
├── src/
│   ├── components/
│   │   ├── MaterialCard.jsx    # Individual material selector
│   │   ├── MaterialCard.css
│   │   ├── SummaryPanel.jsx    # Overall metrics display
│   │   └── SummaryPanel.css
│   ├── App.jsx                  # Main application
│   ├── App.css
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Technologies

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **PapaParse**: CSV parsing
- **CSS3**: Styling with modern features

## Customization

### Changing Theme Colors
Edit the CSS files to customize colors:
- Primary: `#667eea` (purple gradient)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (amber)
- Danger: `#ef4444` (red)

### Adjusting Layout
- Modify grid columns in `App.css` for material cards
- Adjust padding/margins in component CSS files

## Troubleshooting

### "No data" or loading forever
- Make sure the CSV files exist in `../data/processed/`
- Run the Python pipeline first: `python3 agent/workflow.py`
- Check browser console for errors

### Port already in use
- Change port in `vite.config.js`
- Or kill the process using port 3000

### Dependencies errors
```bash
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- [ ] Export selections to CSV
- [ ] Save/load different scenarios
- [ ] Comparison view (side-by-side alternatives)
- [ ] Advanced filtering and sorting
- [ ] Print-friendly report view
- [ ] Dark mode toggle

---

Built with ❤️ for Value Engineering optimization

