# Data and Code Connection Map

This document describes how data files connect to code modules and flow through the system.

## Data Files → Code Modules

### Input Data Files

#### 1. Apartment Specifications
**File**: `data/apartment_specs.csv`

**Columns**: Unit Description, Description, Unit Area, Floor locations, Total Units, Total Leasable Area, Percent

**Used by**:
- `data_loader.py`: `load_apartment_specs()`
  - Filters units where `Total Units > 0`
  - Used to determine which unit types are active in project

- `material_matcher.py`: `_calculate_door_count()`
  - Validates unit types
  - Multiplies door counts by `Total Units` per unit type

**Purpose**: Determines which apartment units exist and how many, used to calculate total material quantities.

---

#### 2. Door Schedule
**File**: `data/schedule/schedule_unit_doors.tsv`

**Columns**: MARK, LOCATION, TYPE, WIDTH, HEIGHT, THICKNESS, MATERIAL, LABEL, HARDWARE SET, FRAME TYPE, FRAME MATERIAL

**Used by**:
- `data_loader.py`: `load_door_schedule()`
- `material_matcher.py`: `match_doors()`
  - `MARK`: Unique door identifier
  - `LOCATION`: Determines if exterior ("balcony") or interior
  - `WIDTH`, `HEIGHT`: Used for RSMeans matching
  - `MATERIAL`: Wood, metal, glass matching

**Purpose**: Specifications for each door type in the project.

---

#### 3. Door Counts
**File**: `data/counts/count_unit_doors.tsv`

**Columns**: Unit Description, Description, Unit Area, 1-22 (door MARK numbers)

**Used by**:
- `data_loader.py`: `load_door_counts()`
- `material_matcher.py`: `_calculate_door_count()`
  - Maps unit types to door MARKs
  - Each number column represents count of that door MARK in unit
  - Cross-references with `apartment_specs.csv` to get total counts

**Purpose**: Links unit types to door quantities.

---

#### 4. Window Schedule
**File**: `data/schedule/schedule_window.tsv`

**Columns**: MARK, STYLE, UNIT SIZE WIDTH, UNIT SIZE HEIGHT, MATERIAL, HEAD HEIGHT, SILL HEIGHT, GLAZING INSUL, GLAZING LOW-E, GLAZING TINT, DETAIL, ventilation calculations, REMARKS

**Used by**:
- `data_loader.py`: `load_window_schedule()`
- `material_matcher.py`: `match_windows()`
  - `MARK`: Unique window identifier (W1, W2, etc.)
  - `STYLE`: Casement, sliding, fixed, etc.
  - `UNIT SIZE WIDTH/HEIGHT`: Parsed to calculate area
  - `MATERIAL`: V=Vinyl, W=Wood, A=Aluminum

**Purpose**: Specifications for each window type.

---

#### 5. Window Counts
**File**: `data/counts/count_windows.tsv`

**Columns**: MARK, North-outside, South-outside, West-outside, East-outside, North-inside, South-inside, West-inside, East-inside

**Used by**:
- `data_loader.py`: `load_window_counts()`
- `material_matcher.py`: `match_windows()`
  - Sums all facade columns to get total count per window MARK
  - Multiplied by unit cost to get total window cost

**Purpose**: Window quantities by building facade.

---

#### 6. Appliance Counts
**File**: `data/counts/count_appliance.tsv`

**Columns**: UNIT TYPE, Appliance, Manufacturer, Model, Finish, Notes, Count

**Used by**:
- `data_loader.py`: `load_appliance_counts()`
- `material_matcher.py`: `match_appliances()`
  - `Appliance`: Type (Refrigerator, Microwave, etc.)
  - `Count`: Total quantity needed
  - Manufacturer/Model for reference

**Purpose**: Lists all appliances needed and quantities.

---

#### 7. RSMeans Windows
**File**: `rsmeans/rsmeams_B2020_ext_windows_unit_cost.tsv`

**Columns**: CODE, MATERIAL, TYPE, GLAZING, SIZE, DETAIL, MAT, INST, TOTAL

**Used by**:
- `data_loader.py`: `load_rsmeans_windows()`
  - Cleans numeric columns (removes commas)
- `material_matcher.py`: `_find_best_window_match()`
  - Filters by MATERIAL (Wood, Vinyl, Aluminum)
  - Filters by TYPE (casement, sliding, etc.)
  - Calculates area from SIZE and finds closest match
- `alternatives_finder.py`: `_find_window_alts()`
  - Finds alternatives with similar area and style
  - Filters cheaper options

**Purpose**: Cost database for windows (material, labor, total).

---

#### 8. RSMeans Exterior Doors
**File**: `rsmeans/rsmeans_B2030_110_ext_doors_unit_cost.tsv`

**Columns**: CODE, MATERIAL, TYPE, DOORS, SPECIFICATION, OPENING, MAT., INST., TOTAL

**Used by**:
- `data_loader.py`: `load_rsmeans_ext_doors()`
- `material_matcher.py`: `_find_best_door_match()` (for balcony doors)
  - Filters by TYPE containing "glass"
  - Parses OPENING for width matching
- `alternatives_finder.py`: `_find_door_alts()`
  - Filters height > 7' (84 inches)
  - Finds similar materials

**Purpose**: Cost database for exterior doors.

---

#### 9. RSMeans Interior Doors
**File**: `rsmeans/rsmenas_C1020_102_int_doors_unit_cost.tsv`

**Columns**: CODE, DOOR SHAPE, Material, Core type, DESCRIPTION, DIMENSIONS, MAT., INST., TOTAL

**Used by**:
- `data_loader.py`: `load_rsmeans_int_doors()`
- `material_matcher.py`: `_find_best_door_match()` (for interior doors)
  - Filters by Material (wood, metal)
  - Parses DIMENSIONS for width matching
- `alternatives_finder.py`: `_find_door_alts()`
  - Filters by material similarity
  - Width within 6 inches

**Purpose**: Cost database for interior doors.

---

#### 10. RSMeans Appliances
**File**: `rsmeans/rsmeams_appliances_unit_cost.tsv`

**Columns**: Description, Unit, $ Cost (note: two-column format)

**Used by**:
- `data_loader.py`: `load_rsmeans_appliances()`
  - Custom parser for unusual two-column format
- `material_matcher.py`: `_find_best_appliance_match()`
  - Keyword matching (refrigerator, microwave, etc.)
  - Parses cost ranges (e.g., "885 - 1300" → average)

**Purpose**: Cost database for appliances.

---

## Data Processing Flow

### Step 1: Data Loading (`data_loader.py`)

```
Input Files → DataLoader.load_all() → Dict of DataFrames
```

**Output**: 10 cleaned DataFrames ready for processing

---

### Step 2: Material Matching (`material_matcher.py`)

```
DataFrames → MaterialMatcher → Matched Materials
```

**Process**:
1. `match_windows()`:
   - Join window_schedule + window_counts on MARK
   - Calculate total count (sum facades)
   - Find best RSMeans match
   - Calculate costs: unit × quantity
   
2. `match_doors()`:
   - For each door in door_schedule:
     - Determine if exterior (balcony) or interior
     - Calculate count across all units (door_counts × apartment_specs)
     - Find best RSMeans match (ext or int database)
     - Calculate total costs

3. `match_appliances()`:
   - For each appliance in appliance_counts:
     - Find best RSMeans match by keyword
     - Parse cost (handle ranges)
     - Apply 10% reduction
     - Calculate totals

**Output Files**:
- `data/processed/matched_windows.csv`
- `data/processed/matched_doors.csv`
- `data/processed/matched_appliances.csv`

**Key Columns Added**: RSMEANS_CODE, UNIT_COST_*, TOTAL_COST_*

---

### Step 3: Finding Alternatives (`alternatives_finder.py`)

```
Matched Materials + RSMeans Data → AlternativesFinder → Alternatives
```

**Process**:
1. `find_window_alternatives()`:
   - For each matched window:
     - Filter RSMeans: same style, area ±30%, cheaper
     - Sort by cost, take top 3
     - Add as ALT_RANK 1-3 (original is rank 0)

2. `find_door_alternatives()`:
   - For each matched door:
     - Exterior: height > 7', glass/aluminum materials
     - Interior: same material, width ±6"
     - Filter cheaper, take top 3

3. `create_appliance_alternatives()`:
   - Only 1 alternative: 10% reduction (rank 1)
   - No additional alternatives needed

**Output Files**:
- `data/processed/window_alternatives.csv`
- `data/processed/door_alternatives.csv`
- `data/processed/appliance_alternatives.csv`

**Key Columns Added**: ALT_RANK, ALT_CODE, ALT_DESC, ALT_COST_*, COST_REDUCTION_PCT

---

### Step 4: LLM Evaluation (`llm_evaluator.py`)

```
Alternatives → LLMEvaluator → Scored Alternatives
```

**Process**:
1. For each alternative (rank > 0):
   - Build prompt with original vs alternative descriptions
   - Call Claude API (or use heuristic if no key)
   - Parse JSON response: {functional: X, design: Y}
   - Calculate cost score from reduction %

2. Original (rank 0) always gets:
   - FUNCTIONAL_SCORE = 5
   - DESIGN_SCORE = 5
   - COST_SCORE = 1

3. Appliances get predefined:
   - Rank 0: 5, 5, 1
   - Rank 1 (10% off): 5, 5, 2

**Output Files**:
- `data/processed/window_alternatives_scored.csv`
- `data/processed/door_alternatives_scored.csv`
- `data/processed/appliance_alternatives_scored.csv`

**Key Columns Added**: FUNCTIONAL_SCORE, DESIGN_SCORE, COST_SCORE

---

### Step 5: Optimization (`optimizer.py`)

```
Scored Alternatives + Matched Materials → VEOptimizer → Optimized Selections
```

**Process**:
1. For each strategy (best_functional, best_cost, best_design, balanced):
   - Apply weights to scores
   - Calculate WEIGHTED_SCORE for each alternative
   - Select highest scoring alternative per material

2. Calculate metrics:
   - Merge selections with matched_materials for quantities
   - Calculate total costs (original vs selected)
   - Calculate weighted average scores
   - Aggregate by category and overall

**Output Files**:
- `data/processed/optimization/{strategy}_windows_selections.csv`
- `data/processed/optimization/{strategy}_doors_selections.csv`
- `data/processed/optimization/{strategy}_appliances_selections.csv`
- `data/processed/optimization/{strategy}_metrics.csv`

**Metrics Calculated**:
- Total original cost
- Total selected cost
- Total cost savings
- Cost reduction %
- Average functional score
- Average design score
- Average cost score

---

### Step 6: Visualization (`app.py`)

```
Optimization Results → Streamlit → Interactive Dashboard
```

**Reads**:
- All `{strategy}_metrics.csv` files
- All `{strategy}_*_selections.csv` files

**Displays**:
- Strategy comparison table
- Cost metrics and progress bars
- Category breakdowns
- Material selections with scores
- Interactive tabs for windows/doors/appliances

---

## Key Data Transformations

### Dimension Parsing
**Function**: `parse_dimension()` in `material_matcher.py`

```
"5'-0"" → (5, 0) → 60 inches
"3'-0"" → (3, 0) → 36 inches
```

Used for width, height matching.

### Area Calculation
**Function**: `dim_to_sqft()` in `material_matcher.py`

```
Width: "5'-0"" → 60 inches
Height: "6'-0"" → 72 inches
Area: (60 × 72) / 144 = 30 sq ft
```

Used for window matching.

### Cost Parsing
**Function**: `_parse_cost()` in `material_matcher.py`

```
"885 - 1300" → (885 + 1300) / 2 = 1092.5
"$1,250" → 1250.0
```

Used for appliance costs.

### Score to Cost Reduction
**Function**: `_cost_reduction_to_score()` in `llm_evaluator.py`

```
30%+ → 5
20-30% → 4
15-20% → 3
10-15% → 2
5-10% → 1
<5% → 1
```

### Weighted Score Calculation
**Function**: `_select_best()` in `optimizer.py`

```
Best Cost: score = functional×0 + design×0 + cost×1
Balanced: score = functional×0.33 + design×0.33 + cost×0.33
```

---

## Summary Table

| Data File | Loader Function | Matcher Function | Finder Function | Output |
|-----------|----------------|------------------|-----------------|--------|
| apartment_specs.csv | load_apartment_specs() | _calculate_door_count() | - | Unit filtering |
| schedule_unit_doors.tsv | load_door_schedule() | match_doors() | find_door_alternatives() | matched_doors.csv → door_alternatives_scored.csv |
| count_unit_doors.tsv | load_door_counts() | _calculate_door_count() | - | Door quantities |
| schedule_window.tsv | load_window_schedule() | match_windows() | find_window_alternatives() | matched_windows.csv → window_alternatives_scored.csv |
| count_windows.tsv | load_window_counts() | match_windows() | - | Window quantities |
| count_appliance.tsv | load_appliance_counts() | match_appliances() | create_appliance_alternatives() | matched_appliances.csv → appliance_alternatives_scored.csv |
| RSMeans windows | load_rsmeans_windows() | _find_best_window_match() | _find_window_alts() | Cost matching |
| RSMeans ext doors | load_rsmeans_ext_doors() | _find_best_door_match() | _find_door_alts() | Cost matching |
| RSMeans int doors | load_rsmeans_int_doors() | _find_best_door_match() | _find_door_alts() | Cost matching |
| RSMeans appliances | load_rsmeans_appliances() | _find_best_appliance_match() | - | Cost matching |

---

## Complete Data Flow Diagram

```
apartment_specs.csv ─┐
schedule_unit_doors.tsv ─┤
count_unit_doors.tsv ─┤
schedule_window.tsv ─┤
count_windows.tsv ─┤
count_appliance.tsv ─┤
RSMeans (4 files) ─┘
                    │
                    ↓
            [DataLoader]
                    │
                    ↓
            10 DataFrames
                    │
                    ↓
        [MaterialMatcher]
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Windows     Doors    Appliances
        │           │           │
        └───────────┴───────────┘
                    │
                    ↓
        matched_materials
                    │
                    ↓
      [AlternativesFinder]
                    │
                    ↓
      alternatives (3 types)
                    │
                    ↓
        [LLMEvaluator]
                    │
                    ↓
    evaluated_alternatives
                    │
                    ↓
         [VEOptimizer]
                    │
        ┌───────────┼───────────┬──────────┐
        ↓           ↓           ↓          ↓
  best_functional best_cost best_design balanced
        │           │           │          │
        └───────────┴───────────┴──────────┘
                    │
                    ↓
        optimization_results
                    │
            ┌───────┴───────┐
            ↓               ↓
        [Files]         [Streamlit]
     (CSV exports)      (Dashboard)
```

This map shows exactly how every data file flows through the system to produce the final optimized material selections.


