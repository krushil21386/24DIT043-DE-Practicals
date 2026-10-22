# DATA ENGINEERING LAB — PRACTICAL REPORT 9

**Student Name**: Krushil Patel  
**Student ID**: 24DIT043  
**Practical No**: 9  
**Title**: Kimball Star Schema and Snowflake Dimensional Data Modeling  

---

## 1. Problem Definition & Objectives

Design and implement a robust logical and physical dimensional data model tailored for business analytics. Transform unstructured transactional sales records into a classic **Kimball Star Schema** model, explicitly breaking fields out into highly descriptive Dimension tables and organizing numeric metrics within a central Fact table. Expand into a **Snowflake Schema** to compare storage size and join efficiency.

---

## 2. Key Questions & Theoretical Analysis

### Key Point 1: What are the key architectural differences and use cases for normalized operational models (3NF) versus denormalized analytical star schemas?

| Feature | 3rd Normal Form (3NF - OLTP) | Star Schema (OLAP - Kimball) |
|---|---|---|
| **Primary Goal** | Eliminate data redundancy, prevent update/delete anomalies. | Maximize query speed, simplify ad-hoc business reporting. |
| **Data Structure** | Highly normalized (many small tables linked via foreign keys). | Denormalized Dimension tables surrounding a central Fact table. |
| **Join Complexity** | High. Typical queries require 6 to 12 joins across deep hierarchies. | Low. Flat single-hop joins between Fact and Dimensions. |
| **Write vs. Read Speed** | Fast single-row transactional writes (`INSERT`/`UPDATE`). | Fast analytical scans, aggregations (`SUM`, `AVG`, `GROUP BY`). |

### Key Point 2: Explain the concept of Slowly Changing Dimensions (SCDs) and specify how your design tracks customer state changes over time.

**Slowly Changing Dimensions (SCD)** describe methodologies for managing dimensional attribute modifications over time (e.g., when a customer changes their address or account tier):
- **SCD Type 1 (Overwrite)**: Overwrites the old attribute value with the new one. No historical record is preserved.
- **SCD Type 2 (Historical Versioning)**: Inserts a new row with a new surrogate key, marking the old row with an expiration date (`valid_to`) or flag (`is_active = 0`), and setting the new row to `is_active = 1`.
- **Implementation in `Dim_Customer`**:
  Our design incorporates an `is_active_scd` flag and `scd_start_date` to preserve customer state transitions without altering historical Fact sales links.

### Key Point 3: How do surrogate keys protect an analytical data warehouse model from changes or migrations in source system business keys?

1. **Source Decoupling**: Operational natural keys (`customer_id`, `product_sku`) are controlled by upstream CRM/ERP systems that may re-format, truncate, or re-use IDs upon system migration. Surrogate keys are integer sequences wholly managed by the warehouse.
2. **Handling SCD Type 2**: A single customer can have multiple surrogate keys representing different chronological snapshots, while sharing the same business key.
3. **Storage & Join Optimization**: Integer surrogate keys (4 or 8 bytes) are dramatically faster to join and index than wide alphanumeric UUID or string business keys.

---

## 3. Visual ERD Schema (dbdiagram.io DBML Definition)

The schema definition has been generated and saved to `schema_erd.dbml`. It can be viewed visually by pasting into [dbdiagram.io](https://dbdiagram.io):

```dbml
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
```

---

## 4. Supplementary Problem: Star vs. Snowflake Schema Comparison

| Criteria | Star Schema | Snowflake Schema |
|---|---|---|
| **Hierarchy Storage** | Denormalized within `Dim_Product` | Normalized into `Dim_Category` & `Dim_Subcategory` |
| **Join Overhead** | 2 Joins (Fact + Date + Product) | 4 Joins (Fact + Date + Product + Subcategory + Category) |
| **Query Performance** | **1.5x - 2.5x Faster** | Slower due to multi-table join tree traversals |
| **Best Used For** | Fast interactive BI dashboards | Massive dimension tables with severe storage limits |

---
*Verified and submitted by: 24DIT043 Krushil Patel*
