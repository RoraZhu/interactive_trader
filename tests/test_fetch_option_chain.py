import unittest
from interactive_trader import fetch_option_chain
import pandas as pd


class fetch_option_chain_test_case(unittest.TestCase):

    def setUp(self):
        self.option_chain = fetch_option_chain("AAPL", "STK", 265598)

    def test_contract_details_is_dataframe(self):
        self.assertIsInstance(self.option_chain, pd.DataFrame)

    def test_contract_details_has_correct_columns(self):
        print(self.option_chain["underlying"])
        print(self.option_chain["expirations"])
        hd_colnames = self.option_chain.columns
        correct_colnames = ['exchange', 'underlying_conId', 'underlying', 'multiplier', 'expirations', 'strikes']
        self.assertListEqual(list(hd_colnames), correct_colnames)


if __name__ == '__main__':
    unittest.main()