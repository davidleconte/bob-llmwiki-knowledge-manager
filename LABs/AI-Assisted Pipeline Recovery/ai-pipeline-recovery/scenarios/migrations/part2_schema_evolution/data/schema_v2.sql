-- Schema V2: Updated database schema
-- Changes from V1:
-- 1. customers table: first_name + last_name → full_name
-- 2. customers table: added 'status' column (active/inactive)
-- 3. addresses table: renamed to 'customer_addresses'
-- 4. addresses table: added 'address_type' column (billing/shipping)
-- 5. transactions table: renamed to 'financial_transactions'
-- 6. transactions table: added 'currency' column
-- 7. transactions table: transaction_type changed to 'credit'/'debit' → 'CR'/'DR'

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,              -- CHANGED: was first_name + last_name
    email TEXT UNIQUE,
    phone TEXT,
    status TEXT DEFAULT 'active',          -- NEW: active/inactive
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT                        -- NEW
);

CREATE TABLE IF NOT EXISTS customer_addresses (  -- RENAMED from 'addresses'
    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    address_type TEXT DEFAULT 'billing',   -- NEW: billing/shipping
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT,
    postal_code TEXT,                      -- RENAMED from zip_code
    country_code TEXT DEFAULT 'US',        -- RENAMED from country, different format
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS financial_transactions (  -- RENAMED from 'transactions'
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',           -- NEW
    transaction_type TEXT NOT NULL,        -- CHANGED: now 'CR'/'DR' instead of 'credit'/'debit'
    category TEXT,                         -- RENAMED from description
    transaction_date TEXT NOT NULL,
    processed_at TEXT,                     -- NEW
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
