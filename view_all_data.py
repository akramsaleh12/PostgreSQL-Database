"""
view_all_data.py

Connects to the sample_store PostgreSQL database and displays all rows
from each table (customers, products, orders, order_items), one table
at a time.

Requirements:
    pip install psycopg2-binary tabulate

Usage:
    python view_all_data.py
"""

import psycopg2
from tabulate import tabulate

# ----------------------------------------------------------------------
# CONFIG - adjust to match your local PostgreSQL setup
# ----------------------------------------------------------------------
DB_NAME = "sample_store"
DB_USER = "postgres"
DB_PASSWORD = "***********"   # change to your actual password
DB_HOST = "localhost"
DB_PORT = "5432"

TABLES = ["customers", "products", "orders", "order_items"]


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def display_table(cur, table_name):
    cur.execute(f"SELECT * FROM {table_name} ORDER BY 1")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    print(f"\n{'=' * 60}")
    print(f" Table: {table_name}  ({len(rows)} row(s))")
    print(f"{'=' * 60}")

    if rows:
        print(tabulate(rows, headers=columns, tablefmt="psql"))
    else:
        print("  (no rows)")


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        for table in TABLES:
            display_table(cur, table)
        cur.close()
    finally:
        conn.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
