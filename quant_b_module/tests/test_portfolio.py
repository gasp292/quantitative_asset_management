import unittest
import pandas as pd
import numpy as np

# This allows running the test file directly from anywhere
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# We import the class to test it
from quant_b_module.portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    
    def setUp(self):
        """This function runs before each test. We create a PortfolioManager with simple fake data."""
        self.pm = PortfolioManager()
        # We simulate 2 assets (A and B) over 3 days
        # Asset A: 100 -> 110 (+10%) -> 121 (+10%)
        # Asset B: 50 -> 50 (0%) -> 55 (+10%)
        fake_data = {
            'AssetA': [100.0, 110.0, 121.0],
            'AssetB': [50.0,  50.0,  55.0]
        }
        dates = pd.date_range(start="2024-01-01", periods=3, freq="D")
        # We force this data into the manager (no need to fetch_data)
        self.pm.data = pd.DataFrame(fake_data, index=dates)

    def test_simulation_base_100(self):
        """Test if the portfolio correctly starts at 100."""
        weights = {'AssetA': 0.5, 'AssetB': 0.5}
        res = self.pm.simulate_portfolio(weights, rebalance=False)
        # The first day MUST ALWAYS be 100
        self.assertEqual(res['Portfolio'].iloc[0], 100.0)

    def test_simulation_calculation(self):
        """Test if the portfolio calculation is mathematically correct."""
        weights = {'AssetA': 0.5, 'AssetB': 0.5}
        res = self.pm.simulate_portfolio(weights, rebalance=False)
        # Day 2:
        # Asset A is worth 110 (i.e. 110 base 100)
        # Asset B is worth 50 (i.e. 100 base 100)
        # Portfolio 50/50 = 0.5*110 + 0.5*100 = 55 + 50 = 105
        self.assertAlmostEqual(res['Portfolio'].iloc[1], 105.0)

    def test_rebalancing_logic(self):
        """(Basic) test to check if the rebalance option does not crash."""
        weights = {'AssetA': 0.5, 'AssetB': 0.5}
        # Just run to see if it runs without error
        res = self.pm.simulate_portfolio(weights, rebalance=True)
        self.assertIsNotNone(res)
        self.assertIn('Portfolio', res.columns)

if __name__ == '__main__':
    unittest.main()