"""
Test script for data_loader module.
"""
import sys
sys.path.insert(0, '/Users/weizhang/git/VEAgent')

from agent.data_loader import DataLoader


def test_data_loader():
    """Test loading all data files."""
    loader = DataLoader()
    data = loader.load_all()
    
    # Check all keys are present
    expected_keys = [
        'apartment_specs', 'door_schedule', 'door_counts', 
        'window_schedule', 'window_counts', 'appliance_counts',
        'rsmeans_windows', 'rsmeans_ext_doors', 'rsmeans_int_doors', 
        'rsmeans_appliances'
    ]
    
    for key in expected_keys:
        assert key in data, f"Missing key: {key}"
        assert len(data[key]) > 0, f"Empty dataframe for {key}"
        print(f"✓ {key}: {data[key].shape}")
    
    # Specific checks
    assert 'Total Units' in data['apartment_specs'].columns
    assert 'MARK' in data['door_schedule'].columns
    assert 'MARK' in data['window_schedule'].columns
    
    print("\n✅ All tests passed!")
    

if __name__ == "__main__":
    test_data_loader()


