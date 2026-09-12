"""
Stock Portfolio Tracker
Version: 1.0
Application Type: Python Console Application

Description:
A beginner-friendly console application that allows users to track their
stock portfolio, calculate individual and total investments using a predefined
stock-price dictionary, and optionally export the summary to a TXT or CSV file.
"""

import csv
import os

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


def display_available_stocks(stock_prices):
    """Displays the list of available stocks and their current prices (FR1)."""
    print("\n================ AVAILABLE STOCKS ================")
    print(f"{'Stock Symbol':<15} {'Price (USD)':<12}")
    print("-" * 35)
    for symbol, price in stock_prices.items():
        print(f"{symbol:<15} ${price:<12}")
    print("==================================================\n")


def get_valid_stock(stock_prices):
    """
    Prompts the user for a stock symbol and validates it (FR2, Business Rules, Error Handling).
    - Case-insensitive (e.g., 'aapl' -> 'AAPL')
    - Handles empty input
    - Handles unknown/invalid stock symbols
    """
    while True:
        user_input = input("Enter stock symbol (e.g., AAPL): ").strip()

        # Handle empty input
        if not user_input:
            print("Error: Stock symbol cannot be empty. Please enter a stock symbol.")
            continue

        symbol = user_input.upper()

        # Check if symbol exists in stock dictionary
        if symbol in stock_prices:
            return symbol
        else:
            print(f"Error: Stock '{symbol}' not found in available stocks.")
            add_choice = input(f"Would you like to add '{symbol}' as a new available stock? (yes/no): ").strip().lower()
            if add_choice in ["yes", "y"]:
                while True:
                    price_input = input(f"Enter price for {symbol} in USD: ").strip()
                    try:
                        price = float(price_input)
                        if price <= 0:
                            print("Error: Price must be greater than zero.")
                            continue
                        stock_prices[symbol] = int(price) if price.is_integer() else price
                        print(f"[SUCCESS] Added {symbol} at ${stock_prices[symbol]} to available stocks.")
                        return symbol
                    except ValueError:
                        print("Error: Please enter a valid numeric price.")
            else:
                print("Please try again.")


def get_valid_quantity():
    """
    Prompts the user for share quantity and validates it (FR3, Error Handling).
    - Must be a valid integer
    - Must be strictly greater than zero (rejects text, 0, and negative numbers)
    """
    while True:
        quantity_input = input("Enter quantity of shares: ").strip()

        # Check if quantity is empty
        if not quantity_input:
            print("Error: Quantity cannot be empty. Please enter a valid positive integer.")
            continue

        try:
            quantity = int(quantity_input)
            if quantity <= 0:
                print("Error: Quantity must be greater than zero. Please enter a positive number.")
                continue
            return quantity
        except ValueError:
            print("Error: Invalid quantity. Please enter a valid whole number (e.g., 5).")


def display_summary(portfolio_data, total_investment):
    """
    Displays the portfolio summary formatted according to Section 11 Sample Output (FR6).
    """
    print("\n========== PORTFOLIO SUMMARY ==========")
    print(f"{'Stock':<8} {'Price':<8} {'Quantity':<10} {'Value'}")
    for item in portfolio_data:
        print(f"{item['stock']:<8} ${item['price']:<7} {item['quantity']:<10} ${item['value']}")
    print("-" * 41)
    print(f"Total Investment: ${total_investment}")
    print("-" * 41)


def save_to_txt(filepath, portfolio_data, total_investment):
    """Saves the portfolio summary to a readable text file (FR7, Section 12)."""
    try:
        with open(filepath, mode="w", encoding="utf-8") as file:
            file.write("========== PORTFOLIO SUMMARY ==========\n")
            file.write(f"{'Stock':<8} {'Price':<8} {'Quantity':<10} {'Value'}\n")
            for item in portfolio_data:
                file.write(f"{item['stock']:<8} ${item['price']:<7} {item['quantity']:<10} ${item['value']}\n")
            file.write("-" * 41 + "\n")
            file.write(f"Total Investment: ${total_investment}\n")
            file.write("-" * 41 + "\n")
        print(f"[SUCCESS] Portfolio report successfully saved to: {filepath}")
    except OSError as err:
        print(f"Error: Could not save TXT file. {err}")


def save_to_csv(filepath, portfolio_data, total_investment):
    """Saves the portfolio summary to a CSV file (FR7, Section 12)."""
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Header row
            writer.writerow(["Stock", "Price", "Quantity", "Investment"])
            # Data rows
            for item in portfolio_data:
                writer.writerow([item['stock'], f"${item['price']}", item['quantity'], f"${item['value']}"])
            # Total row
            writer.writerow(["Total", "", "", f"${total_investment}"])
        print(f"[SUCCESS] Portfolio CSV successfully saved to: {filepath}")
    except OSError as err:
        print(f"Error: Could not save CSV file. {err}")


def handle_file_export(portfolio_data, total_investment):
    """
    Asks the user if they would like to save the portfolio summary to a TXT or CSV file (FR7).
    """
    while True:
        save_choice = input("\nWould you like to save the portfolio summary to a file? (yes/no): ").strip().lower()
        if save_choice in ["no", "n"]:
            print("Export skipped.")
            break
        elif save_choice in ["yes", "y"]:
            print("\nSelect file format:")
            print("1. Text file (.txt)")
            print("2. CSV file (.csv)")
            print("3. Both (.txt and .csv)")
            format_choice = input("Enter choice (1/2/3): ").strip()

            default_name = "portfolio_summary"
            custom_name = input(f"Enter filename (press Enter for default '{default_name}'): ").strip()
            filename = custom_name if custom_name else default_name

            if format_choice == "1":
                save_to_txt(f"{filename}.txt", portfolio_data, total_investment)
                break
            elif format_choice == "2":
                save_to_csv(f"{filename}.csv", portfolio_data, total_investment)
                break
            elif format_choice == "3":
                save_to_txt(f"{filename}.txt", portfolio_data, total_investment)
                save_to_csv(f"{filename}.csv", portfolio_data, total_investment)
                break
            else:
                print("Invalid choice. Please choose 1, 2, or 3.")
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def main():
    """Main execution loop adhering to the user flow in the PRD."""
    print("=" * 50)
    print("       WELCOME TO STOCK PORTFOLIO TRACKER       ")
    print("=" * 50)

    # 1. Display available stocks (FR1)
    display_available_stocks(STOCK_PRICES)

    # User portfolio dictionary to store {symbol: quantity} (Section 8)
    portfolio = {}

    # Main input loop: Add stocks to portfolio
    while True:
        # 2. Enter and validate stock symbol (FR2)
        stock_symbol = get_valid_stock(STOCK_PRICES)

        # 3. Enter and validate quantity (FR3)
        quantity = get_valid_quantity()

        # Add to portfolio (if stock already added, accumulate quantity)
        if stock_symbol in portfolio:
            portfolio[stock_symbol] += quantity
            print(f"Added {quantity} more share(s) to existing holding: {stock_symbol}. Total: {portfolio[stock_symbol]}")
        else:
            portfolio[stock_symbol] = quantity
            print(f"Added {stock_symbol} ({quantity} shares) to portfolio.")

        # Ask user whether to add another stock
        while True:
            add_more = input("\nAdd another stock? (yes/no): ").strip().lower()
            if add_more in ["yes", "y", "no", "n"]:
                break
            print("Please enter 'yes' or 'no'.")

        if add_more in ["no", "n"]:
            break

    # Calculate investment values and total portfolio value (FR4, FR5)
    portfolio_data = []
    total_investment = 0

    for symbol, qty in portfolio.items():
        price = STOCK_PRICES[symbol]
        investment_value = price * qty
        total_investment += investment_value
        portfolio_data.append({
            "stock": symbol,
            "price": price,
            "quantity": qty,
            "value": investment_value
        })

    # Display portfolio summary (FR6, Section 11)
    display_summary(portfolio_data, total_investment)

    # Optional file export (FR7, Section 12)
    handle_file_export(portfolio_data, total_investment)

    print("\nThank you for using Stock Portfolio Tracker. Goodbye!")


if __name__ == "__main__":
    main()
