-- ==========================
-- R1. KARDEX FÍSICO
-- Combina movimientos de entrada (positivo) y salida (negativo)
-- ==========================

CREATE OR REPLACE FUNCTION SP_GET_KARDEX_FISICO(
    p_product_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    movement_date TIMESTAMP,
    movement_type VARCHAR(10),
    reference VARCHAR(100),
    quantity INTEGER,
    running_balance INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH movements AS (
        -- Entradas (saldo positivo)
        SELECT 
            en.date AS mov_date,
            'ENTRADA'::VARCHAR(10) AS mov_type,
            COALESCE(en.reference, 'N/A')::VARCHAR(100) AS ref,
            end_det.quantity AS qty
        FROM entry_note_detail end_det
        INNER JOIN entry_note en ON en.id = end_det.entry_id
        WHERE end_det.product_id = p_product_id
          AND en.date::DATE BETWEEN p_start_date AND p_end_date
        
        UNION ALL
        
        -- Salidas (saldo negativo)
        SELECT 
            ex.date AS mov_date,
            'SALIDA'::VARCHAR(10) AS mov_type,
            COALESCE(ex.reference, 'N/A')::VARCHAR(100) AS ref,
            -exd.quantity AS qty
        FROM exit_note_detail exd
        INNER JOIN exit_note ex ON ex.id = exd.exit_id
        WHERE exd.product_id = p_product_id
          AND ex.date::DATE BETWEEN p_start_date AND p_end_date
    )
    SELECT 
        m.mov_date AS movement_date,
        m.mov_type AS movement_type,
        m.ref AS reference,
        m.qty AS quantity,
        SUM(m.qty) OVER (ORDER BY m.mov_date ROWS UNBOUNDED PRECEDING)::INTEGER AS running_balance
    FROM movements m
    ORDER BY m.mov_date;
END;
$$ LANGUAGE plpgsql;


-- ==========================
-- R2. STOCK ACTUAL POR CATEGORÍA
-- JOIN entre products, categories y units
-- ==========================

CREATE OR REPLACE FUNCTION SP_GET_STOCK_CATEGORIA(
    p_category_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR(150),
    category_name VARCHAR(100),
    unit_name VARCHAR(50),
    stock INTEGER,
    sale_price DECIMAL(10,2),
    purchase_price DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        p.stock,
        p.sale_price,
        p.purchase_price
    FROM products p
    INNER JOIN categories c ON c.id = p.category_id
    INNER JOIN units u ON u.id = p.unit_id
    WHERE (p_category_id IS NULL OR p.category_id = p_category_id)
    ORDER BY c.name, p.name;
END;
$$ LANGUAGE plpgsql;


-- ==========================
-- R3. HISTORIAL DE COMPRAS
-- Órdenes de compra por proveedor y rango de fechas
-- ==========================

CREATE OR REPLACE FUNCTION SP_GET_PURCHASE_HISTORY(
    p_supplier_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    order_id INTEGER,
    order_date TIMESTAMP,
    supplier_name VARCHAR(150),
    user_fullname VARCHAR(100),
    total DECIMAL(10,2),
    status VARCHAR(20),
    items_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        po.id AS order_id,
        po.date AS order_date,
        s.name AS supplier_name,
        u.fullname AS user_fullname,
        po.total,
        po.status,
        COUNT(pod.id) AS items_count
    FROM purchase_order po
    INNER JOIN suppliers s ON s.id = po.supplier_id
    INNER JOIN users u ON u.id = po.user_id
    LEFT JOIN purchase_order_detail pod ON pod.order_id = po.id
    WHERE po.supplier_id = p_supplier_id
      AND po.date::DATE BETWEEN p_start_date AND p_end_date
    GROUP BY po.id, po.date, s.name, u.fullname, po.total, po.status
    ORDER BY po.date DESC;
END;
$$ LANGUAGE plpgsql;


-- ==========================
-- R4. PRODUCTOS MÁS VENDIDOS
-- Top productos por cantidad vendida (exit_note_detail)
-- ==========================

CREATE OR REPLACE FUNCTION SP_GET_TOP_SELLING(
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR(150),
    category_name VARCHAR(100),
    unit_name VARCHAR(50),
    total_quantity_sold BIGINT,
    current_stock INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        COALESCE(SUM(exd.quantity), 0)::BIGINT AS total_quantity_sold,
        p.stock AS current_stock
    FROM products p
    INNER JOIN categories c ON c.id = p.category_id
    INNER JOIN units u ON u.id = p.unit_id
    LEFT JOIN exit_note_detail exd ON exd.product_id = p.id
    GROUP BY p.id, p.name, c.name, u.name, p.stock
    ORDER BY total_quantity_sold DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- ==========================
-- R5. PRODUCTOS BAJO STOCK
-- Productos con stock menor al umbral
-- ==========================

CREATE OR REPLACE FUNCTION SP_GET_LOW_STOCK(
    p_stock_threshold INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR(150),
    category_name VARCHAR(100),
    unit_name VARCHAR(50),
    current_stock INTEGER,
    purchase_price DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        p.stock AS current_stock,
        p.purchase_price
    FROM products p
    INNER JOIN categories c ON c.id = p.category_id
    INNER JOIN units u ON u.id = p.unit_id
    WHERE p.stock < p_stock_threshold
    ORDER BY p.stock ASC, p.name;
END;
$$ LANGUAGE plpgsql;
