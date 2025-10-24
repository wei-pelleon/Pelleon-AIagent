"""
Streamlit UI for Value Engineering Agent results visualization.
"""
import streamlit as st
import pandas as pd
import os
from pathlib import Path


# Page config
st.set_page_config(
    page_title="VE Agent - Value Engineering Optimizer",
    page_icon="💰",
    layout="wide"
)

# Paths
PROCESSED_DIR = Path("/Users/weizhang/git/VEAgent/data/processed")
OPT_DIR = PROCESSED_DIR / "optimization"


def load_optimization_results():
    """Load optimization results from CSV files."""
    strategies = ['best_functional', 'best_cost', 'best_design', 'balanced']
    results = {}
    
    for strategy in strategies:
        metrics_file = OPT_DIR / f"{strategy}_metrics.csv"
        if metrics_file.exists():
            results[strategy] = {
                'metrics': pd.read_csv(metrics_file),
                'windows': pd.read_csv(OPT_DIR / f"{strategy}_windows_selections.csv"),
                'doors': pd.read_csv(OPT_DIR / f"{strategy}_doors_selections.csv"),
                'appliances': pd.read_csv(OPT_DIR / f"{strategy}_appliances_selections.csv"),
            }
    
    return results


def main():
    """Main Streamlit app."""
    st.title("💰 Value Engineering Optimizer")
    st.markdown("### Construction Materials Cost Optimization Dashboard")
    
    # Check if results exist
    if not OPT_DIR.exists():
        st.error("No optimization results found. Please run the workflow first.")
        st.code("python3 agent/workflow.py", language="bash")
        return
    
    # Load results
    try:
        results = load_optimization_results()
    except Exception as e:
        st.error(f"Error loading results: {e}")
        return
    
    if not results:
        st.error("No optimization results found. Please run the workflow first.")
        return
    
    # Strategy selector
    st.sidebar.header("Optimization Strategy")
    strategy_names = {
        'best_functional': '🎯 Best Functional',
        'best_cost': '💵 Best Cost',
        'best_design': '🎨 Best Design',
        'balanced': '⚖️ Balanced'
    }
    
    selected_strategy = st.sidebar.selectbox(
        "Select Strategy",
        options=list(strategy_names.keys()),
        format_func=lambda x: strategy_names[x]
    )
    
    # Display strategy description
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Strategy Descriptions")
    st.sidebar.markdown("""
    - **Best Functional**: Prioritizes maintaining original functionality
    - **Best Cost**: Maximizes cost reduction
    - **Best Design**: Prioritizes design intent preservation
    - **Balanced**: Equal weight to all three criteria
    """)
    
    # Get selected strategy data
    strategy_data = results[selected_strategy]
    metrics_df = strategy_data['metrics']
    
    # Display header
    st.header(f"{strategy_names[selected_strategy]}")
    
    # Overall metrics
    overall_row = metrics_df[metrics_df['Category'] == 'Overall']
    if len(overall_row) > 0:
        overall = overall_row.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Original Cost", overall['Original Cost'])
        with col2:
            st.metric("Optimized Cost", overall['Selected Cost'])
        with col3:
            st.metric("Cost Savings", overall['Cost Savings'], 
                     delta=f"-{overall['Cost Reduction %']}")
        with col4:
            st.metric("Cost Reduction", overall['Cost Reduction %'])
    
    # Score metrics
    st.markdown("### Average Scores")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        functional_score = float(overall['Avg Functional Score'])
        st.metric("Functional Score", f"{functional_score:.2f} / 5.0")
        st.progress(functional_score / 5.0)
    
    with col2:
        design_score = float(overall['Avg Design Score'])
        st.metric("Design Score", f"{design_score:.2f} / 5.0")
        st.progress(design_score / 5.0)
    
    with col3:
        cost_score = float(overall['Avg Cost Score'])
        st.metric("Cost Reduction Score", f"{cost_score:.2f} / 5.0")
        st.progress(cost_score / 5.0)
    
    # Category breakdown
    st.markdown("---")
    st.markdown("### Category Breakdown")
    
    # Display metrics table for categories (excluding overall)
    category_metrics = metrics_df[metrics_df['Category'] != 'Overall']
    st.dataframe(category_metrics, use_container_width=True, hide_index=True)
    
    # Material details tabs
    st.markdown("---")
    st.markdown("### Material Selections")
    
    tab1, tab2, tab3 = st.tabs(["🪟 Windows", "🚪 Doors", "🍳 Appliances"])
    
    with tab1:
        windows = strategy_data['windows']
        st.markdown(f"**{len(windows)} window types selected**")
        
        # Show key columns
        display_cols = ['MATERIAL_ID', 'ALT_RANK', 'ALT_DESC', 'ALT_COST_TOTAL', 
                       'FUNCTIONAL_SCORE', 'DESIGN_SCORE', 'COST_SCORE', 'COST_REDUCTION_PCT']
        available_cols = [col for col in display_cols if col in windows.columns]
        
        st.dataframe(windows[available_cols], use_container_width=True, hide_index=True)
    
    with tab2:
        doors = strategy_data['doors']
        st.markdown(f"**{len(doors)} door types selected**")
        
        display_cols = ['MATERIAL_ID', 'MATERIAL_TYPE', 'ALT_RANK', 'ALT_DESC', 'ALT_COST_TOTAL',
                       'FUNCTIONAL_SCORE', 'DESIGN_SCORE', 'COST_SCORE', 'COST_REDUCTION_PCT']
        available_cols = [col for col in display_cols if col in doors.columns]
        
        st.dataframe(doors[available_cols], use_container_width=True, hide_index=True)
    
    with tab3:
        appliances = strategy_data['appliances']
        st.markdown(f"**{len(appliances)} appliance types selected**")
        
        display_cols = ['MATERIAL_ID', 'ALT_RANK', 'ALT_DESC', 'ALT_COST_TOTAL',
                       'FUNCTIONAL_SCORE', 'DESIGN_SCORE', 'COST_SCORE', 'COST_REDUCTION_PCT']
        available_cols = [col for col in display_cols if col in appliances.columns]
        
        st.dataframe(appliances[available_cols], use_container_width=True, hide_index=True)
    
    # Comparison section
    st.markdown("---")
    st.markdown("### Strategy Comparison")
    
    # Build comparison table
    comparison_data = []
    for strategy_key, strategy_name in strategy_names.items():
        if strategy_key in results:
            metrics = results[strategy_key]['metrics']
            overall_row = metrics[metrics['Category'] == 'Overall'].iloc[0]
            
            comparison_data.append({
                'Strategy': strategy_name,
                'Cost Savings': overall_row['Cost Savings'],
                'Cost Reduction %': overall_row['Cost Reduction %'],
                'Functional Score': overall_row['Avg Functional Score'],
                'Design Score': overall_row['Avg Design Score'],
                'Cost Score': overall_row['Avg Cost Score'],
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    Value Engineering Agent - Construction Materials Optimization System<br>
    Data processed from apartment specs, RSMeans cost database, and LLM evaluation
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


