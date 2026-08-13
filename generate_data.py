"""Generates a synthetic retail Superstore-style dataset and saves it to data/retail_data.csv"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 5000

categories = {
    "Furniture": {
        "sub": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "products": {
            "Chairs": ["Office Chair Pro", "Ergonomic Chair", "Gaming Chair", "Executive Chair"],
            "Tables": ["Dining Table Oak", "Coffee Table Glass", "Standing Desk", "Conference Table"],
            "Bookcases": ["5-Shelf Bookcase", "Corner Bookcase", "Wood Bookcase", "Modern Bookcase"],
            "Furnishings": ["Lamp Set", "Wall Clock", "Curtains Set", "Area Rug"],
        },
        "base_price": (80, 900),
    },
    "Technology": {
        "sub": ["Phones", "Computers", "Accessories", "Copiers"],
        "products": {
            "Phones": ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12"],
            "Computers": ["MacBook Pro", "Dell XPS 15", "Lenovo ThinkPad", "HP Spectre"],
            "Accessories": ["USB Hub", "Wireless Mouse", "Mechanical Keyboard", "Monitor Stand"],
            "Copiers": ["LaserJet Pro", "OfficeJet 8015", "WorkForce Pro", "PIXMA G6020"],
        },
        "base_price": (15, 2500),
    },
    "Office Supplies": {
        "sub": ["Paper", "Binders", "Storage", "Art"],
        "products": {
            "Paper": ["A4 Ream 500", "Legal Pad 3-pack", "Photo Paper 100", "Cardstock 200"],
            "Binders": ["3-Ring Binder", "Portfolio Binder", "Spine Label Kit", "Binder Clips"],
            "Storage": ["Banker's Box", "File Cabinet", "Drawer Organizer", "Label Maker"],
            "Art": ["Marker Set 24", "Colored Pencils", "Watercolor Kit", "Sketchpad A3"],
        },
        "base_price": (5, 120),
    },
}

regions = {
    "West": ["California", "Washington", "Oregon", "Nevada", "Arizona"],
    "East": ["New York", "Pennsylvania", "New Jersey", "Massachusetts", "Virginia"],
    "Central": ["Texas", "Illinois", "Ohio", "Michigan", "Wisconsin"],
    "South": ["Florida", "Georgia", "North Carolina", "Tennessee", "Alabama"],
}

state_cities = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Bellevue"],
    "Oregon": ["Portland", "Eugene", "Salem", "Bend"],
    "Nevada": ["Las Vegas", "Reno", "Henderson", "Carson City"],
    "Arizona": ["Phoenix", "Tucson", "Scottsdale", "Tempe"],
    "New York": ["New York City", "Buffalo", "Albany", "Rochester"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
    "New Jersey": ["Newark", "Jersey City", "Trenton", "Camden"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Cambridge"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Illinois": ["Chicago", "Aurora", "Rockford", "Naperville"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Savannah"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
    "Alabama": ["Birmingham", "Montgomery", "Huntsville", "Mobile"],
}

segments = ["Consumer", "Corporate", "Home Office"]
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Barbara", "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]

start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

rows = []
for i in range(N):
    order_date = start_date + timedelta(days=random.randint(0, date_range))
    ship_days = {"Standard Class": 5, "Second Class": 3, "First Class": 2, "Same Day": 0}
    ship_mode = random.choice(ship_modes)
    ship_date = order_date + timedelta(days=ship_days[ship_mode] + random.randint(0, 2))

    category = random.choice(list(categories.keys()))
    cat_data = categories[category]
    sub_cat = random.choice(cat_data["sub"])
    product = random.choice(cat_data["products"][sub_cat])

    low, high = cat_data["base_price"]
    base = np.random.uniform(low, high)
    quantity = random.randint(1, 10)
    discount = random.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.5])
    sales = round(base * quantity * (1 - discount), 2)
    profit_margin = np.random.uniform(0.05, 0.45) if discount < 0.3 else np.random.uniform(-0.15, 0.1)
    profit = round(sales * profit_margin, 2)

    region = random.choice(list(regions.keys()))
    state = random.choice(regions[region])
    city = random.choice(state_cities[state])

    customer_id = f"CU-{random.randint(1000, 9999)}"
    customer_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    segment = random.choice(segments)

    rows.append({
        "order_id": f"ORD-{2021 + (order_date - start_date).days // 365}-{i+1:04d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "ship_date": ship_date.strftime("%Y-%m-%d"),
        "ship_mode": ship_mode,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "segment": segment,
        "city": city,
        "state": state,
        "region": region,
        "category": category,
        "sub_category": sub_cat,
        "product_name": product,
        "sales": sales,
        "quantity": quantity,
        "discount": discount,
        "profit": profit,
    })

df = pd.DataFrame(rows)
df.to_csv("data/retail_data.csv", index=False)
print(f"Dataset generated: {len(df)} rows")
print(df.head())
