"""
Stock Portfolio Tracker - Web Application
Version: 1.0 (Web Edition)
Framework: Flask

Description:
A web-based financial dashboard for tracking stock portfolios.
Provides real-time calculations, input validation conforming to PRD requirements,
portfolio visualization, and .txt / .csv exports.
"""

import csv
import io
import os
from flask import Flask, render_template, request, jsonify, session, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "stock-portfolio-secret-key-2026")

# ==========================================
# 8. Data Structure
# Predefined dictionary storing stock prices
# ==========================================
STOCK_PRICES = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "MSFT": 420,
    "AMZN": 180
}


def get_session_portfolio():
    """Retrieves or initializes the portfolio dictionary in user session."""
    if "portfolio" not in session:
        session["portfolio"] = {}
    return session["portfolio"]


def build_portfolio_details(portfolio):
    """
    Computes individual investment values and total portfolio value (FR4, FR5).
    Returns (items_list, total_investment).
    """
    items = []
    total_investment = 0

    for symbol, quantity in portfolio.items():
        price = STOCK_PRICES.get(symbol, 0)
        value = price * quantity
        total_investment += value
        items.append({
            "stock": symbol,
            "price": price,
            "quantity": quantity,
            "value": value
        })

    # Sort items alphabetically by symbol
    items.sort(key=lambda x: x["stock"])
    return items, total_investment


@app.route("/")
def index():
    """Renders the main dashboard page."""
    return render_template("index.html", available_stocks=STOCK_PRICES)


@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    """Returns the list of available stocks and current prices (FR1)."""
    return jsonify({
        "success": True,
        "stocks": STOCK_PRICES
    })


@app.route("/api/stocks/add", methods=["POST"])
def add_custom_stock():
    """Allows users to add a new stock symbol and price dynamically."""
    data = request.get_json() or {}
    symbol = str(data.get("symbol", "")).strip().upper()
    price_input = data.get("price", None)

    if not symbol:
        return jsonify({"success": False, "error": "Stock symbol cannot be empty."}), 400

    try:
        price = float(price_input)
        if price <= 0:
            return jsonify({"success": False, "error": "Stock price must be greater than zero."}), 400
        if price.is_integer():
            price = int(price)
        else:
            price = round(price, 2)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid price. Please enter a valid positive number."}), 400

    STOCK_PRICES[symbol] = price
    return jsonify({
        "success": True,
        "message": f"Successfully added {symbol} at ${price} to available stocks!",
        "stocks": STOCK_PRICES
    })


@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Returns the current user portfolio and calculations."""
    portfolio = get_session_portfolio()
    items, total = build_portfolio_details(portfolio)
    return jsonify({
        "success": True,
        "items": items,
        "total_investment": total,
        "stocks": STOCK_PRICES
    })


@app.route("/api/portfolio/add", methods=["POST"])
def add_stock():
    """
    Validates and adds shares to the portfolio (FR2, FR3, Section 10).
    """
    data = request.get_json() or {}
    stock_input = data.get("stock", "")
    quantity_input = data.get("quantity", None)

    # 1. Validate stock symbol (Section 10: Empty stock name & Invalid stock name)
    if not isinstance(stock_input, str) or not stock_input.strip():
        return jsonify({
            "success": False,
            "error": "Stock symbol cannot be empty. Please enter a stock symbol."
        }), 400

    symbol = stock_input.strip().upper()
    if symbol not in STOCK_PRICES:
        return jsonify({
            "success": False,
            "error": f"Stock '{symbol}' not found in available stocks. Available: {', '.join(STOCK_PRICES.keys())}."
        }), 400

    # 2. Validate quantity (Section 10: Quantity is text, zero, or negative)
    try:
        quantity = int(quantity_input)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid quantity. Please enter a valid whole number (e.g., 5)."
        }), 400

    if quantity <= 0:
        return jsonify({
            "success": False,
            "error": "Quantity must be greater than zero. Please enter a positive integer."
        }), 400

    # 3. Add or accumulate into session portfolio
    portfolio = get_session_portfolio()
    portfolio[symbol] = portfolio.get(symbol, 0) + quantity
    session["portfolio"] = portfolio
    session.modified = True

    items, total = build_portfolio_details(portfolio)
    return jsonify({
        "success": True,
        "message": f"Successfully added {quantity} share(s) of {symbol}.",
        "items": items,
        "total_investment": total
    })


@app.route("/api/portfolio/update", methods=["POST"])
def update_stock():
    """Updates the absolute quantity of an existing holding."""
    data = request.get_json() or {}
    symbol = str(data.get("stock", "")).strip().upper()
    quantity_input = data.get("quantity", None)

    if symbol not in STOCK_PRICES:
        return jsonify({"success": False, "error": f"Invalid stock symbol: {symbol}"}), 400

    try:
        quantity = int(quantity_input)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Quantity must be a valid whole number."}), 400

    portfolio = get_session_portfolio()

    if quantity <= 0:
        # If set to 0 or less, remove it
        portfolio.pop(symbol, None)
    else:
        portfolio[symbol] = quantity

    session["portfolio"] = portfolio
    session.modified = True

    items, total = build_portfolio_details(portfolio)
    return jsonify({
        "success": True,
        "items": items,
        "total_investment": total
    })


@app.route("/api/portfolio/remove", methods=["POST"])
def remove_stock():
    """Removes a stock from the user's portfolio."""
    data = request.get_json() or {}
    symbol = str(data.get("stock", "")).strip().upper()

    portfolio = get_session_portfolio()
    if symbol in portfolio:
        del portfolio[symbol]
        session["portfolio"] = portfolio
        session.modified = True

    items, total = build_portfolio_details(portfolio)
    return jsonify({
        "success": True,
        "message": f"Removed {symbol} from portfolio.",
        "items": items,
        "total_investment": total
    })


@app.route("/api/portfolio/clear", methods=["POST"])
def clear_portfolio():
    """Clears all holdings from the user's portfolio."""
    session["portfolio"] = {}
    session.modified = True
    return jsonify({
        "success": True,
        "message": "Portfolio cleared.",
        "items": [],
        "total_investment": 0
    })


@app.route("/export/txt", methods=["GET"])
def export_txt():
    """
    Generates and downloads a readable .txt portfolio report
    matching PRD Section 11 Sample Output & Section 12.
    """
    portfolio = get_session_portfolio()
    items, total = build_portfolio_details(portfolio)

    output = io.StringIO()
    output.write("========== PORTFOLIO SUMMARY ==========\n")
    output.write(f"{'Stock':<8} {'Price':<8} {'Quantity':<10} {'Value'}\n")
    for item in items:
        output.write(f"{item['stock']:<8} ${item['price']:<7} {item['quantity']:<10} ${item['value']}\n")
    output.write("-" * 41 + "\n")
    output.write(f"Total Investment: ${total}\n")
    output.write("-" * 41 + "\n")

    content = output.getvalue()
    output.close()

    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=portfolio_summary.txt"}
    )


@app.route("/export/csv", methods=["GET"])
def export_csv():
    """
    Generates and downloads a .csv portfolio report with columns and total row
    matching PRD Section 12.
    """
    portfolio = get_session_portfolio()
    items, total = build_portfolio_details(portfolio)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Stock", "Price", "Quantity", "Investment"])
    for item in items:
        writer.writerow([item["stock"], f"${item['price']}", item["quantity"], f"${item['value']}"])
    writer.writerow(["Total", "", "", f"${total}"])

    content = output.getvalue()
    output.close()

    return Response(
        content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=portfolio_summary.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Stock Portfolio Tracker Web App on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
