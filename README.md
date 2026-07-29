# Sample Store Database

A small sample PostgreSQL database representing a simple e-commerce store,
with customers, products, and orders. Used throughout this project as the
data source for a setup script, a Streamlit admin app, and a REST API.

## Overview

- **Database name:** `sample_store`
- **Engine:** PostgreSQL
- **Tables:** 4 (`customers`, `products`, `orders`, `order_items`)

```
customers ──< orders ──< order_items >── products
```

A customer can place many orders. Each order can contain many items, and
each item references one product. This is a standard star-shaped
order/line-item schema.

## Tables

### `customers`

Stores customer contact information.

| Column      | Type          | Constraints                  | Description                  |
|-------------|---------------|-------------------------------|-------------------------------|
| customer_id | SERIAL        | PRIMARY KEY                   | Unique customer ID (auto)     |
| first_name  | VARCHAR(50)   | NOT NULL                      | Customer's first name         |
| last_name   | VARCHAR(50)   | NOT NULL                      | Customer's last name          |
| email       | VARCHAR(100)  | UNIQUE, NOT NULL               | Customer's email address      |
| created_at  | TIMESTAMP     | DEFAULT NOW()                  | When the customer was added   |

### `products`

Stores the catalog of items available for purchase.

| Column      | Type           | Constraints              | Description                     |
|-------------|----------------|----------------------------|-----------------------------------|
| product_id  | SERIAL         | PRIMARY KEY                 | Unique product ID (auto)          |
| name        | VARCHAR(100)   | NOT NULL                    | Product name                      |
| description | TEXT           |                              | Product description               |
| price       | NUMERIC(10,2)  | NOT NULL, CHECK (price >= 0) | Unit price                        |
| stock_qty   | INTEGER        | NOT NULL, DEFAULT 0          | Units currently in stock          |

### `orders`

One row per order placed by a customer.

| Column      | Type         | Constraints                          | Description                          |
|-------------|--------------|----------------------------------------|----------------------------------------|
| order_id    | SERIAL       | PRIMARY KEY                             | Unique order ID (auto)                  |
| customer_id | INTEGER      | NOT NULL, FOREIGN KEY → customers        | Who placed the order                    |
| order_date  | TIMESTAMP    | DEFAULT NOW()                            | When the order was placed               |
| status      | VARCHAR(20)  | DEFAULT 'pending'                        | pending / shipped / completed / cancelled |

### `order_items`

Line items belonging to an order — the "many-to-many" join between
`orders` and `products`, with quantity and price captured per line.

| Column         | Type           | Constraints                          | Description                        |
|----------------|----------------|----------------------------------------|--------------------------------------|
| order_item_id  | SERIAL         | PRIMARY KEY                             | Unique line item ID (auto)           |
| order_id       | INTEGER        | NOT NULL, FOREIGN KEY → orders           | Which order this line belongs to     |
| product_id     | INTEGER        | NOT NULL, FOREIGN KEY → products         | Which product was ordered            |
| quantity       | INTEGER        | NOT NULL, CHECK (quantity > 0)           | How many units                       |
| unit_price     | NUMERIC(10,2)  | NOT NULL                                 | Price per unit at time of order      |

> **Why store `unit_price` on `order_items` instead of just looking it up
> from `products`?** Product prices can change over time. Recording the
> price at the moment of purchase keeps historical orders accurate even if
> a product's price is later updated.

## Relationships

- `orders.customer_id` → `customers.customer_id` (many orders per customer)
- `order_items.order_id` → `orders.order_id` (many items per order)
- `order_items.product_id` → `products.product_id` (a product can appear in many order items)

Because of these foreign keys:
- You can't delete a customer who still has orders.
- You can't delete an order that still has order items.
- You can't delete a product that's referenced by an order item.
- Deleting the "child" records first (order_items → orders → customers/products) is required.

## Sample data

The setup script seeds the database with:
- 3 customers
- 4 products
- 3 orders
- 4 order items

## Related project files

| File                     | Purpose                                                         |
|--------------------------|-------------------------------------------------------------------|
| `setup_sample_db.py`     | Creates the database, tables, and inserts sample data (re-runnable) |
| `view_all_data.py`       | Prints all rows from every table to the console                    |
| `app.py`                 | Streamlit admin UI — Add/Update/Delete/Inquiry for all 4 tables    |
| `sample_store_api/`      | FastAPI REST API — full CRUD endpoints for all 4 tables             |

## Connecting

All scripts use the same connection settings, configurable at the top of
each file:

```python
DB_NAME = "sample_store"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

To connect manually via `psql`:

```
psql -U postgres -d sample_store -h localhost
```

## Example queries

```sql
-- All orders with customer name and order total
SELECT o.order_id, c.first_name, c.last_name, o.status,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, c.first_name, c.last_name, o.status
ORDER BY o.order_id;

-- Products low on stock
SELECT name, stock_qty FROM products WHERE stock_qty < 100 ORDER BY stock_qty;

-- A customer's order history
SELECT o.order_id, o.order_date, o.status
FROM orders o
WHERE o.customer_id = 1
ORDER BY o.order_date DESC;
```
