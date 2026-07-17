-- Schema V1: Original database schema
-- This represents the "old" application schema

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT,
    zip_code TEXT,
    country TEXT DEFAULT 'USA',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,  -- 'credit' or 'debit'
    description TEXT,
    transaction_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Insert sample data
INSERT INTO customers (first_name, last_name, email, phone) VALUES
    ('John', 'Doe', 'john.doe@email.com', '555-0101'),
    ('Jane', 'Smith', 'jane.smith@email.com', '555-0102'),
    ('Bob', 'Johnson', 'bob.j@email.com', '555-0103'),
    ('Alice', 'Williams', 'alice.w@email.com', '555-0104'),
    ('Charlie', 'Brown', 'charlie.b@email.com', '555-0105');

INSERT INTO addresses (customer_id, street, city, state, zip_code) VALUES
    (1, '123 Main St', 'New York', 'NY', '10001'),
    (2, '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
    (3, '789 Pine Rd', 'Chicago', 'IL', '60601'),
    (4, '321 Elm Blvd', 'Houston', 'TX', '77001'),
    (5, '654 Maple Dr', 'Phoenix', 'AZ', '85001');

INSERT INTO transactions (customer_id, amount, transaction_type, description, transaction_date) VALUES
    (1, 150.00, 'credit', 'Initial deposit', '2024-01-15'),
    (1, 25.50, 'debit', 'Purchase', '2024-01-20'),
    (2, 500.00, 'credit', 'Transfer in', '2024-01-18'),
    (2, 100.00, 'debit', 'Bill payment', '2024-01-25'),
    (3, 75.00, 'credit', 'Refund', '2024-02-01'),
    (3, 200.00, 'debit', 'Purchase', '2024-02-05'),
    (4, 1000.00, 'credit', 'Salary', '2024-02-10'),
    (5, 50.00, 'debit', 'Subscription', '2024-02-15');
