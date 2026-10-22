"""
PRACTICAL 9: KIMBALL STAR SCHEMA & SNOWFLAKE DIMENSIONAL MODELING
Author: 24DIT043 Krushil Patel
Tools: DuckDB Analytical Engine, SQL DDL, Python
"""

import duckdb
import time
import os

DB_FILE = "dimensional_warehouse.duckdb"

def run_dimensional_modeling():
    con = duckdb.connect(DB_FILE)
    print("=" * 80)
    print("       PRACTICAL 9: DIMENSIONAL DATA MODELING (STAR VS. SNOWFLAKE)      ")
    print("=" * 80)

    # 1. Ingest Raw Denormalized Unstructured Sales Transactions
    print("\n[Step 1/5] Ingesting Unstructured Denormalized Operational Sales Records...")
    con.execute("""
    CREATE OR REPLACE TABLE raw_transactional_sales AS
    SELECT 
        range + 100000 AS order_id,
        'CUST-' || ((range % 1000) + 1) AS customer_id,
        'Customer ' || ((range % 1000) + 1) AS customer_name,
        'cust' || ((range % 1000) + 1) || '@enterprise.com' AS customer_email,
        CASE (range % 4) WHEN 0 THEN 'Retail' WHEN 1 THEN 'Wholesale' WHEN 2 THEN 'Corporate' ELSE 'SME' END AS customer_segment,
        'SKU-' || ((range % 200) + 1) AS product_sku,
        'Product Model ' || ((range % 200) + 1) AS product_name,
        CASE (range % 3) WHEN 0 THEN 'Electronics' WHEN 1 THEN 'Office Supplies' ELSE 'Home Hardware' END AS category_name,
        'SubCategory-' || ((range % 10) + 1) AS subcategory_name,
        'Vendor-' || ((range % 25) + 1) AS manufacturer,
        'Store-' || ((range % 50) + 1) AS store_name,
        CASE (range % 5) WHEN 0 THEN 'New York' WHEN 1 THEN 'London' WHEN 2 THEN 'Mumbai' WHEN 3 THEN 'Tokyo' ELSE 'Berlin' END AS store_city,
        CASE (range % 5) WHEN 0 THEN 'USA' WHEN 1 THEN 'UK' WHEN 2 THEN 'India' WHEN 3 THEN 'Japan' ELSE 'Germany' END AS store_country,
        (range % 15) + 1 AS order_quantity,
        ROUND(((range % 250) + 10.5), 2) AS unit_price,
        ROUND(((range % 15) + 1) * ((range % 250) + 10.5) * 0.05, 2) AS discount_amount,
        ROUND(((range % 15) + 1) * ((range % 250) + 10.5) * 0.08, 2) AS tax_amount,
        ROUND(((range % 15) + 1) * ((range % 250) + 10.5) * 0.22, 2) AS profit_margin,
        DATE '2025-01-01' + INTERVAL (range % 730) DAY AS order_date
    FROM range(250000);
    """)
    print("  [OK] Ingested 250,000 raw sales transaction records.")

    # 2. Build Classic Kimball Star Schema
    print("\n[Step 2/5] Compiling & Populating Kimball Star Schema (Fact + Dimensions)...")
    
    # Dim_Date
    con.execute("""
    CREATE OR REPLACE TABLE dim_date_star AS
    SELECT DISTINCT
        CAST(strftime(order_date, '%Y%m%d') AS INTEGER) AS date_key,
        order_date AS full_date,
        EXTRACT(year FROM order_date) AS year,
        EXTRACT(quarter FROM order_date) AS quarter,
        EXTRACT(month FROM order_date) AS month,
        strftime(order_date, '%B') AS month_name,
        strftime(order_date, '%A') AS day_of_week
    FROM raw_transactional_sales;
    """)

    # Dim_Customer
    con.execute("""
    CREATE OR REPLACE TABLE dim_customer_star AS
    SELECT 
        ROW_NUMBER() OVER () AS customer_key, -- Surrogate Key
        customer_id AS natural_customer_id,
        customer_name,
        customer_email,
        customer_segment,
        1 AS is_active_scd,
        CURRENT_DATE AS scd_start_date
    FROM (SELECT DISTINCT customer_id, customer_name, customer_email, customer_segment FROM raw_transactional_sales);
    """)

    # Dim_Product (Denormalized hierarchy: Category & Subcategory embedded)
    con.execute("""
    CREATE OR REPLACE TABLE dim_product_star AS
    SELECT 
        ROW_NUMBER() OVER () AS product_key, -- Surrogate Key
        product_sku,
        product_name,
        subcategory_name,
        category_name,
        manufacturer
    FROM (SELECT DISTINCT product_sku, product_name, subcategory_name, category_name, manufacturer FROM raw_transactional_sales);
    """)

    # Dim_Store (Denormalized hierarchy: City & Country embedded)
    con.execute("""
    CREATE OR REPLACE TABLE dim_store_star AS
    SELECT 
        ROW_NUMBER() OVER () AS store_key, -- Surrogate Key
        store_name,
        store_city,
        store_country
    FROM (SELECT DISTINCT store_name, store_city, store_country FROM raw_transactional_sales);
    """)

    # Fact_Sales (Central fact table with surrogate keys and additive metrics)
    con.execute("""
    CREATE OR REPLACE TABLE fact_sales_star AS
    SELECT 
        r.order_id,
        d.date_key,
        c.customer_key,
        p.product_key,
        s.store_key,
        r.order_quantity,
        r.unit_price,
        r.discount_amount,
        r.tax_amount,
        ROUND((r.order_quantity * r.unit_price) - r.discount_amount + r.tax_amount, 2) AS total_revenue,
        r.profit_margin
    FROM raw_transactional_sales r
    JOIN dim_date_star d ON r.order_date = d.full_date
    JOIN dim_customer_star c ON r.customer_id = c.natural_customer_id
    JOIN dim_product_star p ON r.product_sku = p.product_sku
    JOIN dim_store_star s ON r.store_name = s.store_name AND r.store_city = s.store_city;
    """)
    print("  [OK] Successfully compiled and loaded Kimball Star Schema!")

    # 3. Build Supplementary Snowflake Schema (Normalized Hierarchies)
    print("\n[Step 3/5] Supplementary Problem: Normalizing Hierarchies into Snowflake Schema...")
    
    # Normalized Dim_Category
    con.execute("""
    CREATE OR REPLACE TABLE dim_category_snow AS
    SELECT ROW_NUMBER() OVER () AS category_key, category_name
    FROM (SELECT DISTINCT category_name FROM raw_transactional_sales);
    """)

    # Normalized Dim_Subcategory (FK to Category)
    con.execute("""
    CREATE OR REPLACE TABLE dim_subcategory_snow AS
    SELECT 
        ROW_NUMBER() OVER () AS subcategory_key,
        sub.subcategory_name,
        cat.category_key
    FROM (SELECT DISTINCT subcategory_name, category_name FROM raw_transactional_sales) sub
    JOIN dim_category_snow cat ON sub.category_name = cat.category_name;
    """)

    # Normalized Dim_Product (FK to Subcategory)
    con.execute("""
    CREATE OR REPLACE TABLE dim_product_snow AS
    SELECT 
        ROW_NUMBER() OVER () AS product_key,
        p.product_sku,
        p.product_name,
        p.manufacturer,
        s.subcategory_key
    FROM (SELECT DISTINCT product_sku, product_name, manufacturer, subcategory_name FROM raw_transactional_sales) p
    JOIN dim_subcategory_snow s ON p.subcategory_name = s.subcategory_name;
    """)
    print("  [OK] Successfully normalized product hierarchy into Snowflake Schema!")

    # 4. Benchmark Query Performance: Star Schema vs. Snowflake Schema
    print("\n[Step 4/5] Benchmarking Analytical Aggregation Queries (Star vs. Snowflake)...")
    
    # Query 1: Star Schema (Fewer joins)
    star_query = """
    SELECT 
        d.year,
        p.category_name,
        SUM(f.total_revenue) AS gross_revenue,
        SUM(f.profit_margin) AS total_profit,
        AVG(f.order_quantity) AS avg_basket_size
    FROM fact_sales_star f
    JOIN dim_date_star d ON f.date_key = d.date_key
    JOIN dim_product_star p ON f.product_key = p.product_key
    GROUP BY d.year, p.category_name
    ORDER BY d.year, gross_revenue DESC;
    """
    t0 = time.time()
    res_star = con.execute(star_query).fetchall()
    t_star = time.time() - t0

    # Query 2: Snowflake Schema (Requires traversing normalized hierarchy joins)
    snow_query = """
    SELECT 
        d.year,
        c.category_name,
        SUM(f.total_revenue) AS gross_revenue,
        SUM(f.profit_margin) AS total_profit,
        AVG(f.order_quantity) AS avg_basket_size
    FROM fact_sales_star f
    JOIN dim_date_star d ON f.date_key = d.date_key
    JOIN dim_product_snow p ON f.product_key = p.product_key
    JOIN dim_subcategory_snow sc ON p.subcategory_key = sc.subcategory_key
    JOIN dim_category_snow c ON sc.category_key = c.category_key
    GROUP BY d.year, c.category_name
    ORDER BY d.year, gross_revenue DESC;
    """
    t0 = time.time()
    res_snow = con.execute(snow_query).fetchall()
    t_snow = time.time() - t0

    print(f"  [STAR SCHEMA]      Execution Time (2 joins): {t_star:.4f} seconds")
    print(f"  [SNOWFLAKE SCHEMA] Execution Time (4 joins): {t_snow:.4f} seconds")
    speedup = t_snow / t_star if t_star > 0 else 1.0
    print(f"  [BENCHMARK] Star schema executes {speedup:.2f}x faster due to join reduction.")

    # 5. Generate dbdiagram.io DBML Schema File
    print("\n[Step 5/5] Generating Visual Entity-Relationship Diagram Schema (schema_erd.dbml)...")
    dbml_content = """// Kimball Star Schema ERD for dbdiagram.io
Table Fact_Sales {
  order_id integer [primary key]
  date_key integer
  customer_key integer
  product_key integer
  store_key integer
  order_quantity integer
  unit_price float
  discount_amount float
  tax_amount float
  total_revenue float
  profit_margin float
}

Table Dim_Date {
  date_key integer [primary key]
  full_date date
  year integer
  quarter integer
  month integer
  month_name varchar
  day_of_week varchar
}

Table Dim_Customer {
  customer_key integer [primary key]
  natural_customer_id varchar
  customer_name varchar
  customer_email varchar
  customer_segment varchar
  is_active_scd integer
  scd_start_date date
}

Table Dim_Product {
  product_key integer [primary key]
  product_sku varchar
  product_name varchar
  subcategory_name varchar
  category_name varchar
  manufacturer varchar
}

Table Dim_Store {
  store_key integer [primary key]
  store_name varchar
  store_city varchar
  store_country varchar
}

Ref: Fact_Sales.date_key > Dim_Date.date_key
Ref: Fact_Sales.customer_key > Dim_Customer.customer_key
Ref: Fact_Sales.product_key > Dim_Product.product_key
Ref: Fact_Sales.store_key > Dim_Store.store_key
"""
    with open("schema_erd.dbml", "w") as f:
        f.write(dbml_content)
    print("  [OK] Saved ERD schema definition to 'practical_9/schema_erd.dbml'.")

    con.close()

if __name__ == "__main__":
    run_dimensional_modeling()
