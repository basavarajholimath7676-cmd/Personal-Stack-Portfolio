"""
Comprehensive automated tests for Stock Portfolio Tracker Web Application.
"""

import unittest
from app import app, STOCK_PRICES


class StockPortfolioWebTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stock Portfolio Tracker", response.data)
        self.assertIn(b"AAPL", response.data)

    def test_get_available_stocks_api(self):
        response = self.client.get("/api/stocks")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["stocks"]["AAPL"], 180)
        self.assertEqual(data["stocks"]["TSLA"], 250)

    def test_add_custom_stock_and_price(self):
        res = self.client.post("/api/stocks/add", json={"symbol": "NVDA", "price": 120})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["stocks"]["NVDA"], 120)

        # Verify we can now purchase shares of NVDA
        res_buy = self.client.post("/api/portfolio/add", json={"stock": "NVDA", "quantity": 10})
        self.assertEqual(res_buy.status_code, 200)
        data_buy = res_buy.get_json()
        self.assertEqual(data_buy["total_investment"], 1200)

    def test_add_valid_stock(self):
        # Add AAPL: 5 shares -> 5 * 180 = 900
        res = self.client.post("/api/portfolio/add", json={"stock": "aapl", "quantity": 5})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_investment"], 900)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["stock"], "AAPL")
        self.assertEqual(data["items"][0]["quantity"], 5)
        self.assertEqual(data["items"][0]["value"], 900)

    def test_accumulate_stock(self):
        self.client.post("/api/portfolio/add", json={"stock": "TSLA", "quantity": 2})
        res = self.client.post("/api/portfolio/add", json={"stock": "TSLA", "quantity": 3})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        # 5 shares of TSLA at 250 = 1250
        self.assertEqual(data["total_investment"], 1250)
        self.assertEqual(data["items"][0]["quantity"], 5)

    def test_error_empty_stock(self):
        res = self.client.post("/api/portfolio/add", json={"stock": "", "quantity": 5})
        self.assertEqual(res.status_code, 400)
        self.assertIn("cannot be empty", res.get_json()["error"])

    def test_error_invalid_stock(self):
        res = self.client.post("/api/portfolio/add", json={"stock": "INVALID_TICKER", "quantity": 5})
        self.assertEqual(res.status_code, 400)
        self.assertIn("not found", res.get_json()["error"])

    def test_error_quantity_text(self):
        res = self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": "five"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("valid whole number", res.get_json()["error"])

    def test_error_quantity_zero(self):
        res = self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": 0})
        self.assertEqual(res.status_code, 400)
        self.assertIn("greater than zero", res.get_json()["error"])

    def test_error_quantity_negative(self):
        res = self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": -3})
        self.assertEqual(res.status_code, 400)
        self.assertIn("greater than zero", res.get_json()["error"])

    def test_export_txt(self):
        with self.client:
            self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": 5})
            self.client.post("/api/portfolio/add", json={"stock": "TSLA", "quantity": 2})
            res = self.client.get("/export/txt")
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/plain", res.content_type)
            content = res.data.decode("utf-8")
            self.assertIn("PORTFOLIO SUMMARY", content)
            self.assertIn("AAPL", content)
            self.assertIn("TSLA", content)
            self.assertIn("Total Investment: $1400", content)

    def test_export_csv(self):
        with self.client:
            self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": 5})
            self.client.post("/api/portfolio/add", json={"stock": "TSLA", "quantity": 2})
            res = self.client.get("/export/csv")
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/csv", res.content_type)
            content = res.data.decode("utf-8")
            self.assertIn("Stock,Price,Quantity,Investment", content)
            self.assertIn("AAPL,$180,5,$900", content)
            self.assertIn("TSLA,$250,2,$500", content)
            self.assertIn("Total,,,$1400", content)

    def test_remove_and_clear(self):
        with self.client:
            self.client.post("/api/portfolio/add", json={"stock": "AAPL", "quantity": 1})
            self.client.post("/api/portfolio/add", json={"stock": "GOOGL", "quantity": 2})
            
            # Remove AAPL
            res = self.client.post("/api/portfolio/remove", json={"stock": "AAPL"})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(len(data["items"]), 1)
            self.assertEqual(data["items"][0]["stock"], "GOOGL")

            # Clear all
            res_clear = self.client.post("/api/portfolio/clear")
            self.assertEqual(res_clear.status_code, 200)
            data_clear = res_clear.get_json()
            self.assertEqual(len(data_clear["items"]), 0)
            self.assertEqual(data_clear["total_investment"], 0)


if __name__ == "__main__":
    unittest.main()
