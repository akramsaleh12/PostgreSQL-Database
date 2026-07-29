"""
setup_sample_db.py

Creates a sample PostgreSQL database ("sample_store") with a few related
tables (customers, products, orders, order_items) and populates them
with some sample data.

Requirements:
    pip install psycopg2-binary

Usage:
    python setup_sample_db.py

Edit the CONFIG section below to match your PostgreSQL credentials.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ----------------------------------------------------------------------
# CONFIG - adjust these to match your local PostgreSQL setup
# ----------------------------------------------------------------------
DB_NAME = "sample_store"
DB_USER = "postgres"
DB_PASSWORD = "Ameena12"   # change to your actual password
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to the default 'postgres' database first, since we need an
# existing database to connect to before we can create a new one.
ADMIN_DB = "postgres"


def create_database():
    """Create the sample database if it doesn't already exist."""
    conn = psycopg2.connect(
        dbname=ADMIN_DB,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"Database '{DB_NAME}' already exists, skipping creation.")

    cur.close()
    conn.close()


def create_tables_and_data():
    """Create sample tables and insert some sample rows."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # Table definitions
    # ------------------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            first_name  VARCHAR(50) NOT NULL,
            last_name   VARCHAR(50) NOT NULL,
            email       VARCHAR(100) UNIQUE NOT NULL,
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id  SERIAL PRIMARY KEY,
            name        VARCHAR(100) NOT NULL,
            description TEXT,
            price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
            stock_qty   INTEGER NOT NULL DEFAULT 0
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id    SERIAL PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
            order_date  TIMESTAMP DEFAULT NOW(),
            status      VARCHAR(20) DEFAULT 'pending'
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id      INTEGER NOT NULL REFERENCES orders(order_id),
            product_id    INTEGER NOT NULL REFERENCES products(product_id),
            quantity      INTEGER NOT NULL CHECK (quantity > 0),
            unit_price    NUMERIC(10, 2) NOT NULL
        );
    """)

    print("Tables created (or already existed).")

    # ------------------------------------------------------------------
    # Sample data (only insert if tables are empty, to keep this
    # script safely re-runnable)
    # ------------------------------------------------------------------
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO customers (first_name, last_name, email) VALUES
                ('Alice', 'Johnson', 'alice.johnson@example.com'),
                ('Bob', 'Smith', 'bob.smith@example.com'),
                ('Carol', 'Davis', 'carol.davis@example.com');
        """)

        cur.execute("""
            INSERT INTO products (name, description, price, stock_qty) VALUES
                ('Wireless Mouse', 'Ergonomic wireless mouse', 19.99, 150),
                ('Mechanical Keyboard', 'RGB backlit mechanical keyboard', 59.99, 80),
                ('USB-C Hub', '7-in-1 USB-C hub', 29.99, 200),
                ('Monitor Stand', 'Adjustable aluminum monitor stand', 39.99, 60);
        """)

        cur.execute("""
            INSERT INTO orders (customer_id, status) VALUES
                (1, 'completed'),
                (2, 'pending'),
                (1, 'shipped');
        """)

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
                (1, 1, 2, 19.99),
                (1, 3, 1, 29.99),
                (2, 2, 1, 59.99),
                (3, 4, 1, 39.99);
        """)

        print("Sample data inserted.")
    else:
        print("Sample data already present, skipping inserts.")

    conn.commit()
    cur.close()
    conn.close()


def verify():
    """Print a quick summary of what's in the database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cur = conn.cursor()

    for table in ("customers", "products", "orders", "order_items"):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table}: {count} rows")

    cur.close()
    conn.close()


if __name__ == "__main__":
    print("Step 1: Creating database (if needed)...")
    create_database()

    print("\nStep 2: Creating tables and inserting sample data...")
    create_tables_and_data()

    print("\nStep 3: Verifying...")
    verify()

    print("\nDone! Connect with:")
    print(f"  psql -U {DB_USER} -d {DB_NAME} -h {DB_HOST}")
