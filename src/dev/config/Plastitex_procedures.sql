-- ------------------------------------------------------------------------------
-- SECCIÓN 1: FUNCIONES PARA TRIGGERS (LÓGICA)
-- ------------------------------------------------------------------------------

-- 1.1 Función para Incrementar Stock (Entradas)
CREATE OR REPLACE FUNCTION tf_stock_increment()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock = stock + NEW.quantity
    WHERE id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.2 Función para Decrementar Stock (Salidas)
CREATE OR REPLACE FUNCTION tf_stock_decrement()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock = stock - NEW.quantity
    WHERE id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.3 Función para Actualizar Stock en Entrada (Update)
CREATE OR REPLACE FUNCTION tf_stock_increment_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Si cambió el producto, revertir el viejo y aplicar al nuevo
    IF OLD.product_id != NEW.product_id THEN
        -- Revertir stock del producto anterior
        UPDATE products SET stock = stock - OLD.quantity WHERE id = OLD.product_id;
        -- Aplicar stock al nuevo producto
        UPDATE products SET stock = stock + NEW.quantity WHERE id = NEW.product_id;
    ELSE
        -- Mismo producto, ajustar por diferencia
        UPDATE products SET stock = stock + (NEW.quantity - OLD.quantity) WHERE id = NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.4 Función para Actualizar Stock en Salida (Update)
CREATE OR REPLACE FUNCTION tf_stock_decrement_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Si cambió el producto, revertir el viejo y aplicar al nuevo
    IF OLD.product_id != NEW.product_id THEN
        -- Revertir stock del producto anterior (sumando lo que se había restado)
        UPDATE products SET stock = stock + OLD.quantity WHERE id = OLD.product_id;
        -- Aplicar descuento al nuevo producto
        UPDATE products SET stock = stock - NEW.quantity WHERE id = NEW.product_id;
    ELSE
        -- Mismo producto, ajustar por diferencia (si qty aumenta, stock baja)
        UPDATE products SET stock = stock - (NEW.quantity - OLD.quantity) WHERE id = NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.5 Función para Revertir Stock al Borrar Entrada
CREATE OR REPLACE FUNCTION tf_stock_revert_entry_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock = stock - OLD.quantity
    WHERE id = OLD.product_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- 1.6 Función para Revertir Stock al Borrar Salida
CREATE OR REPLACE FUNCTION tf_stock_revert_exit_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock = stock + OLD.quantity
    WHERE id = OLD.product_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- SECCIÓN 2: PROCEDIMIENTOS OPERATIVOS
-- ------------------------------------------------------------------------------

-- 2.1 Validar Stock
CREATE OR REPLACE FUNCTION sp_validate_stock(
    p_product_id INT,
    p_requested_quantity INT
)
RETURNS TABLE (
    is_valid BOOLEAN,
    current_stock INT,
    requested_quantity INT,
    message TEXT
) AS $$
DECLARE 
    v_current_stock INT;
    v_product_name VARCHAR(150);
BEGIN
    -- Obtener stock
    SELECT stock, name INTO v_current_stock, v_product_name
    FROM products WHERE id = p_product_id AND is_active = TRUE;
    
    IF v_current_stock IS NULL THEN
        RETURN QUERY SELECT FALSE, 0, p_requested_quantity, 'Producto no encontrado o inactivo'::TEXT;
    ELSEIF v_current_stock >= p_requested_quantity THEN
        RETURN QUERY SELECT TRUE, v_current_stock, p_requested_quantity, ('Stock suficiente para ' || v_product_name)::TEXT;
    ELSE
        RETURN QUERY SELECT FALSE, v_current_stock, p_requested_quantity, ('Stock insuficiente para ' || v_product_name || '. Disp: ' || v_current_stock)::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 2.2 Recalcular Total de Orden de Compra
CREATE OR REPLACE FUNCTION sp_recalculate_po_total(
    p_order_id INT
)
RETURNS TABLE (
    success BOOLEAN,
    new_total DECIMAL(10, 2),
    message TEXT
) AS $$
DECLARE
    v_new_total DECIMAL(10, 2) := 0;
    v_order_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM purchase_order WHERE id = p_order_id AND is_active = TRUE) INTO v_order_exists;
    
    IF NOT v_order_exists THEN
        RETURN QUERY SELECT FALSE, 0::DECIMAL, 'Orden no encontrada'::TEXT;
    ELSE
        SELECT COALESCE(SUM(quantity * unit_price), 0) INTO v_new_total
        FROM purchase_order_detail 
        WHERE order_id = p_order_id AND is_active = TRUE;
        
        UPDATE purchase_order SET total = v_new_total WHERE id = p_order_id;
        
        RETURN QUERY SELECT TRUE, v_new_total, ('Total actualizado a ' || v_new_total)::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- SECCIÓN 3: FUNCIONES DE REPORTE
-- ------------------------------------------------------------------------------

-- 3.1 Kardex Físico (Con saldo acumulado)
CREATE OR REPLACE FUNCTION sp_get_kardex_fisico(
    p_product_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    movement_date TIMESTAMP,
    movement_type VARCHAR,
    reference VARCHAR,
    quantity INTEGER,
    running_balance INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH movements AS (
        SELECT en.date AS mov_date, 'ENTRADA'::VARCHAR AS mov_type, COALESCE(en.reference, 'N/A')::VARCHAR AS ref, end_det.quantity AS qty
        FROM entry_note_detail end_det
        JOIN entry_note en ON en.id = end_det.entry_id
        WHERE end_det.product_id = p_product_id AND en.date::DATE BETWEEN p_start_date AND p_end_date
        UNION ALL
        SELECT ex.date AS mov_date, 'SALIDA'::VARCHAR AS mov_type, COALESCE(ex.reference, 'N/A')::VARCHAR AS ref, -exd.quantity AS qty
        FROM exit_note_detail exd
        JOIN exit_note ex ON ex.id = exd.exit_id
        WHERE exd.product_id = p_product_id AND ex.date::DATE BETWEEN p_start_date AND p_end_date
    )
    SELECT 
        m.mov_date, m.mov_type, m.ref, m.qty,
        SUM(m.qty) OVER (ORDER BY m.mov_date ROWS UNBOUNDED PRECEDING)::INTEGER
    FROM movements m
    ORDER BY m.mov_date;
END;
$$ LANGUAGE plpgsql;

-- 3.2 Stock por Categoría
CREATE OR REPLACE FUNCTION sp_get_stock_categoria(
    p_category_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    category_name VARCHAR,
    unit_name VARCHAR,
    stock INTEGER,
    sale_price DECIMAL,
    purchase_price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, c.name, u.name, p.stock, p.sale_price, p.purchase_price
    FROM products p
    JOIN categories c ON c.id = p.category_id
    JOIN units u ON u.id = p.unit_id
    WHERE (p_category_id IS NULL OR p.category_id = p_category_id)
    ORDER BY c.name, p.name;
END;
$$ LANGUAGE plpgsql;

-- 3.3 Historial de Compras
CREATE OR REPLACE FUNCTION sp_get_purchase_history(
    p_supplier_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    order_id INTEGER,
    order_date TIMESTAMP,
    supplier_name VARCHAR,
    total DECIMAL,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT po.id, po.date, s.name, po.total, po.status
    FROM purchase_order po
    JOIN suppliers s ON s.id = po.supplier_id
    WHERE (p_supplier_id IS NULL OR po.supplier_id = p_supplier_id)
      AND (p_start_date IS NULL OR po.date >= p_start_date)
      AND (p_end_date IS NULL OR po.date <= p_end_date)
    ORDER BY po.date DESC;
END;
$$ LANGUAGE plpgsql;

-- 3.4 Productos más Vendidos
CREATE OR REPLACE FUNCTION sp_get_top_selling(
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    category_name VARCHAR,
    total_sold BIGINT,
    current_stock INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, c.name, COALESCE(SUM(exd.quantity), 0)::BIGINT, p.stock
    FROM products p
    JOIN categories c ON c.id = p.category_id
    LEFT JOIN exit_note_detail exd ON exd.product_id = p.id
    WHERE p.is_active = TRUE
    GROUP BY p.id, p.name, c.name, p.stock
    ORDER BY COALESCE(SUM(exd.quantity), 0) DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 3.5 Productos con Bajo Stock
CREATE OR REPLACE FUNCTION sp_get_low_stock(
    p_stock_threshold INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    category_name VARCHAR,
    current_stock INTEGER,
    deficit INTEGER,
    last_supplier VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id, 
        p.name, 
        c.name, 
        p.stock, 
        (p_stock_threshold - p.stock) AS deficit,
        ls.supplier_name
    FROM products p
    JOIN categories c ON c.id = p.category_id
    LEFT JOIN (
        SELECT DISTINCT ON (end_det.product_id) 
            end_det.product_id, s.name as supplier_name
        FROM entry_note_detail end_det
        JOIN entry_note en ON en.id = end_det.entry_id
        JOIN suppliers s ON s.id = en.supplier_id
        ORDER BY end_det.product_id, en.date DESC
    ) ls ON p.id = ls.product_id
    WHERE p.stock < p_stock_threshold AND p.is_active = TRUE
    ORDER BY p.stock ASC;
END;
$$ LANGUAGE plpgsql;

-- 3.6 Stock Detallado por Producto
CREATE OR REPLACE FUNCTION sp_get_stock_by_product(
    p_product_id INT DEFAULT NULL
)
RETURNS TABLE (
    product_id INT,
    product_name VARCHAR,
    current_stock INT,
    total_entries BIGINT,
    total_exits BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id, 
        p.name, 
        p.stock,
        (SELECT COALESCE(SUM(quantity), 0) FROM entry_note_detail WHERE product_id = p.id AND is_active = TRUE)::BIGINT,
        (SELECT COALESCE(SUM(quantity), 0) FROM exit_note_detail WHERE product_id = p.id AND is_active = TRUE)::BIGINT
    FROM products p
    WHERE p.is_active = TRUE 
      AND (p_product_id IS NULL OR p.id = p_product_id)
    ORDER BY p.name;
END;
$$ LANGUAGE plpgsql;
