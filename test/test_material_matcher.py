"""
Test script for material_matcher module.
"""
import sys
sys.path.insert(0, '/Users/weizhang/git/VEAgent')

from agent.data_loader import DataLoader
from agent.material_matcher import MaterialMatcher


def test_material_matcher():
    """Test material matching."""
    loader = DataLoader()
    data = loader.load_all()
    
    matcher = MaterialMatcher(data)
    
    # Test windows
    windows = matcher.match_windows()
    print(f"✓ Matched {len(windows)} window types")
    assert len(windows) > 0, "Should match some windows"
    assert 'TOTAL_COST' in windows.columns
    
    # Test doors
    doors = matcher.match_doors()
    print(f"✓ Matched {len(doors)} door types")
    assert len(doors) > 0, "Should match some doors"
    assert 'TOTAL_COST' in doors.columns
    
    # Test appliances
    appliances = matcher.match_appliances()
    print(f"✓ Matched {len(appliances)} appliance types")
    assert len(appliances) > 0, "Should match some appliances"
    assert 'TOTAL_COST_REDUCED' in appliances.columns
    
    # Calculate totals
    total_window_cost = windows['TOTAL_COST'].sum()
    total_door_cost = doors['TOTAL_COST'].sum()
    total_appliance_cost = appliances['TOTAL_COST_ORIGINAL'].sum()
    
    print(f"\n💰 Total Windows Cost: ${total_window_cost:,.2f}")
    print(f"💰 Total Doors Cost: ${total_door_cost:,.2f}")
    print(f"💰 Total Appliances Cost: ${total_appliance_cost:,.2f}")
    print(f"💰 GRAND TOTAL: ${(total_window_cost + total_door_cost + total_appliance_cost):,.2f}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_material_matcher()


