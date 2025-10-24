"""
Data tools for LangGraph agent - each table is a tool.
"""
from langchain.tools import tool
import pandas as pd
from pathlib import Path


BASE_PATH = Path("/app")


@tool
def get_apartment_specs() -> str:
    """Get apartment specifications including unit types, areas, and floor distributions.
    Returns the complete apartment_specs dataset."""
    df = pd.read_csv(BASE_PATH / "data" / "apartment_specs.csv")
    return f"Apartment Specifications:\n{df.to_string()}"


@tool
def get_door_schedule() -> str:
    """Get door schedule with specifications (mark, location, type, dimensions, materials).
    Returns the complete door schedule."""
    df = pd.read_csv(BASE_PATH / "data" / "schedule" / "schedule_unit_doors.tsv", sep="\t")
    return f"Door Schedule:\n{df.to_string()}"


@tool
def get_door_counts() -> str:
    """Get door counts by unit type showing which units have which door marks.
    Returns door quantity data."""
    df = pd.read_csv(BASE_PATH / "data" / "counts" / "count_unit_doors.tsv", sep="\t")
    return f"Door Counts:\n{df.to_string()}"


@tool
def get_window_schedule() -> str:
    """Get window schedule with specifications (mark, style, size, material, glazing).
    Returns the complete window schedule."""
    df = pd.read_csv(BASE_PATH / "data" / "schedule" / "schedule_window.tsv", sep="\t")
    return f"Window Schedule:\n{df.to_string()}"


@tool
def get_window_counts() -> str:
    """Get window counts by building facade (North/South/East/West, inside/outside).
    Returns window quantity data."""
    df = pd.read_csv(BASE_PATH / "data" / "counts" / "count_windows.tsv", sep="\t")
    return f"Window Counts:\n{df.to_string()}"


@tool
def get_appliance_counts() -> str:
    """Get appliance specifications and counts including manufacturer, model, and quantities.
    Returns complete appliance data."""
    df = pd.read_csv(BASE_PATH / "data" / "counts" / "count_appliance.tsv", sep="\t")
    return f"Appliance Counts:\n{df.to_string()}"


@tool
def get_total_areas() -> str:
    """Get total area calculations for the building.
    Returns area summary data."""
    df = pd.read_csv(BASE_PATH / "data" / "total_areas.tsv", sep="\t")
    return f"Total Areas:\n{df.to_string()}"


@tool
def get_matched_windows() -> str:
    """Get windows matched to RSMeans costs with quantities and total costs.
    Returns processed window cost data."""
    df = pd.read_csv(BASE_PATH / "data" / "processed" / "matched_windows.csv")
    return f"Matched Windows (with costs):\n{df.to_string()}"


@tool
def get_matched_doors() -> str:
    """Get doors matched to RSMeans costs with quantities and total costs.
    Returns processed door cost data."""
    df = pd.read_csv(BASE_PATH / "data" / "processed" / "matched_doors.csv")
    return f"Matched Doors (with costs):\n{df.to_string()}"


@tool
def get_matched_appliances() -> str:
    """Get appliances matched to RSMeans costs with quantities and total costs.
    Returns processed appliance cost data."""
    df = pd.read_csv(BASE_PATH / "data" / "processed" / "matched_appliances.csv")
    return f"Matched Appliances (with costs):\n{df.to_string()}"


@tool
def get_rsmeans_windows() -> str:
    """Get RSMeans window cost database with material, labor, and total costs.
    Returns RSMeans window pricing data."""
    df = pd.read_csv(BASE_PATH / "rsmeans" / "rsmeams_B2020_ext_windows_unit_cost.tsv", sep="\t")
    return f"RSMeans Windows Unit Costs:\n{df.head(50).to_string()}\n... ({len(df)} total entries)"


@tool
def get_rsmeans_doors() -> str:
    """Get RSMeans door cost database (interior and exterior).
    Returns RSMeans door pricing data."""
    df_ext = pd.read_csv(BASE_PATH / "rsmeans" / "rsmeans_B2030_110_ext_doors_unit_cost.tsv", sep="\t")
    df_int = pd.read_csv(BASE_PATH / "rsmeans" / "rsmenas_C1020_102_int_doors_unit_cost.tsv", sep="\t")
    return f"RSMeans Exterior Doors:\n{df_ext.head(20).to_string()}\n\nRSMeans Interior Doors:\n{df_int.to_string()}"


@tool
def get_window_alternatives() -> str:
    """Get window alternatives with strategic options and scores.
    Returns window alternatives with functional, design, and cost scores."""
    df = pd.read_csv(BASE_PATH / "data" / "processed" / "window_alternatives_scored.csv")
    return f"Window Alternatives (with scores):\n{df.to_string()}"


@tool
def get_door_alternatives() -> str:
    """Get door alternatives with scores.
    Returns door alternatives with functional, design, and cost scores."""
    df = pd.read_csv(BASE_PATH / "data" / "processed" / "door_alternatives_scored.csv")
    return f"Door Alternatives (with scores):\n{df.to_string()}"


# List all tools
ALL_TOOLS = [
    get_apartment_specs,
    get_door_schedule,
    get_door_counts,
    get_window_schedule,
    get_window_counts,
    get_appliance_counts,
    get_total_areas,
    get_matched_windows,
    get_matched_doors,
    get_matched_appliances,
    get_rsmeans_windows,
    get_rsmeans_doors,
    get_window_alternatives,
    get_door_alternatives,
]


