-- ==========================
-- USERS TABLE
-- ==========================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('aux_compra', 'aux_almacen', 'admin'))
);

-- ==========================
-- BASIC CATALOGS
-- ==========================

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200)
);

-- ==========================
-- PRODUCTS
-- ==========================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    stock INTEGER DEFAULT 0,
    sale_price DECIMAL(10,2) DEFAULT 0,
    purchase_price DECIMAL(10,2) DEFAULT 0
);

-- ==========================
-- PURCHASE ORDERS
-- ==========================

CREATE TABLE purchase_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE purchase_order_detail (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- ==========================
-- ENTRY NOTES
-- ==========================

CREATE TABLE entry_note (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference VARCHAR(100)
);

CREATE TABLE entry_note_detail (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);

-- ==========================
-- EXIT NOTES
-- ==========================

CREATE TABLE exit_note (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    reference VARCHAR(100)
);

CREATE TABLE exit_note_detail (
    id SERIAL PRIMARY KEY,
    exit_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);

-- ==========================
-- FOREIGN KEYS
-- ==========================

-- PRODUCTS
ALTER TABLE products
ADD CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(id);

ALTER TABLE products
ADD CONSTRAINT fk_product_unit FOREIGN KEY (unit_id) REFERENCES units(id);

-- PURCHASE ORDERS
ALTER TABLE purchase_order
ADD CONSTRAINT fk_po_user FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE purchase_order
ADD CONSTRAINT fk_po_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id);

ALTER TABLE purchase_order_detail
ADD CONSTRAINT fk_pod_order FOREIGN KEY (order_id) REFERENCES purchase_order(id);

ALTER TABLE purchase_order_detail
ADD CONSTRAINT fk_pod_product FOREIGN KEY (product_id) REFERENCES products(id);

-- ENTRY NOTES
ALTER TABLE entry_note
ADD CONSTRAINT fk_entry_user FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE entry_note
ADD CONSTRAINT fk_entry_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id);

ALTER TABLE entry_note_detail
ADD CONSTRAINT fk_entryd_entry FOREIGN KEY (entry_id) REFERENCES entry_note(id);

ALTER TABLE entry_note_detail
ADD CONSTRAINT fk_entryd_product FOREIGN KEY (product_id) REFERENCES products(id);

-- EXIT NOTES
ALTER TABLE exit_note
ADD CONSTRAINT fk_exit_user FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE exit_note
ADD CONSTRAINT fk_exit_customer FOREIGN KEY (customer_id) REFERENCES customers(id);

ALTER TABLE exit_note_detail
ADD CONSTRAINT fk_exitd_exit FOREIGN KEY (exit_id) REFERENCES exit_note(id);

ALTER TABLE exit_note_detail
ADD CONSTRAINT fk_exitd_product FOREIGN KEY (product_id) REFERENCES products(id);
