import json
from flask import Flask, jsonify, request, Response
import pandas as pd
from datetime import datetime, timedelta

# Importing data
commissions = pd.read_csv('commissions.csv', parse_dates=['date'])
order_lines = pd.read_csv('order_lines.csv')
orders = pd.read_csv('orders.csv', parse_dates=['created_at'])
product_promotions = pd.read_csv('product_promotions.csv', parse_dates=['date'])
products = pd.read_csv('products.csv')
promotions = pd.read_csv('promotions.csv')

app = Flask(__name__)

@app.route('/report/')
def report():
    # Date input
    date_str = request.args.get("date")
    
    # Checking if the date is in a valid format
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y").date() 
    except ValueError:
        return Response(f"Invalid date: {date_str}, use dd/mm/yyyy format.", status=400)
    
    # Creating a combined dataframe containing  information from:
    # commissions, order_lines, orders and product_promotions for the given date
    orders_on_date = orders.loc[orders["created_at"].dt.date == date]
    promotions_on_date = product_promotions.loc[product_promotions["date"].dt.date == date]
    commissions_on_date = commissions.loc[commissions["date"].dt.date == date]
    orderLines_on_date = order_lines.loc[order_lines["order_id"].isin(orders_on_date["id"])]
    merged_orders_on_date = pd.merge(orderLines_on_date, orders_on_date, left_on="order_id", right_on="id")
    merged_orders_on_date = pd.merge(merged_orders_on_date, commissions_on_date, left_on="vendor_id", right_on="vendor_id")
    merged_orders_on_date = pd.merge(merged_orders_on_date, promotions_on_date.iloc[:,1:],
                                     how="left", left_on="product_id", right_on="product_id")

    # Finding the total number of items sold on the given date
    items_sold = merged_orders_on_date["quantity"].sum()

    # Finding the total number of unique customers that made an order that day
    unique_customers = merged_orders_on_date["customer_id"].unique().shape[0]

    # Finding the total amount of discount given that day
    total_discount_amount = (merged_orders_on_date["discount_rate"]*merged_orders_on_date["full_price_amount"]).sum()

    # Finding the average discount rate applied to the items sold that day
    discount_rate_avg = (merged_orders_on_date["discount_rate"]*merged_orders_on_date["quantity"]).sum()/items_sold

    # Finding the average total_amount per order for that day
    order_total_avg = merged_orders_on_date.groupby("order_id").sum()["total_amount"].mean()

    # Finding the total amount of commissions generated that day
    merged_orders_on_date["commission"] = merged_orders_on_date["total_amount"]*merged_orders_on_date["rate"]
    total_commissions = merged_orders_on_date["commission"].sum()

    # Finding the average amount of commissions per order for that day
    order_avg_commission = merged_orders_on_date.groupby("order_id").sum()["commission"].mean()

    # Finding the total amount of commissions earned per promotion that day
    commissions_by_promotion = merged_orders_on_date.groupby("promotion_id").sum()["commission"]
    # Mapping index value to the description from the promotions dataframe
    new_idx = commissions_by_promotion.index.map(promotions.set_index("id").squeeze())
    commissions_by_promotion = commissions_by_promotion.set_axis(new_idx).to_dict()
    
    return jsonify({"date": str(date),
                    "unique_customers": unique_customers,
                    "total_discount_amount": total_discount_amount,
                    "items_sold": int(items_sold),
                    "order_total_avg": order_total_avg,
                    "discount_rate_avg": discount_rate_avg,
                    "commissions": {"promotions" : commissions_by_promotion,
                                   "total": total_commissions,
                                   "order_average": order_avg_commission}})

app.run()