-- ==============================================================================
-- SECCIÓN 1: TRIGGERS PARA CONTROL DE STOCK
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_INCREMENT
-- DESCRIPCIÓN: Incrementa automáticamente el stock de un producto cuando se 
--              inserta un detalle en una nota de ingreso (entry_note_detail).
-- DISPARA: AFTER INSERT en entry_note_detail
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_INCREMENT
AFTER INSERT ON entry_note_detail
FOR EACH ROW
BEGIN
    -- Incrementar el stock del producto
    UPDATE products 
    SET stock = stock + NEW.quantity
    WHERE id = NEW.product_id;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_DECREMENT
-- DESCRIPCIÓN: Decrementa automáticamente el stock de un producto cuando se 
--              inserta un detalle en una nota de salida (exit_note_detail).
-- DISPARA: AFTER INSERT en exit_note_detail
-- NOTA: La validación de stock suficiente debe hacerse ANTES de insertar
--       mediante el SP_VALIDATE_STOCK
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_DECREMENT
AFTER INSERT ON exit_note_detail
FOR EACH ROW
BEGIN
    -- Decrementar el stock del producto
    UPDATE products 
    SET stock = stock - NEW.quantity
    WHERE id = NEW.product_id;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_INCREMENT_UPDATE
-- DESCRIPCIÓN: Ajusta el stock cuando se actualiza la cantidad en entry_note_detail
-- DISPARA: AFTER UPDATE en entry_note_detail
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_INCREMENT_UPDATE
AFTER UPDATE ON entry_note_detail
FOR EACH ROW
BEGIN
    DECLARE quantity_diff INT;
    
    -- Si cambió el producto, revertir el viejo y aplicar al nuevo
    IF OLD.product_id != NEW.product_id THEN
        -- Revertir stock del producto anterior
        UPDATE products 
        SET stock = stock - OLD.quantity
        WHERE id = OLD.product_id;
        
        -- Aplicar stock al nuevo producto
        UPDATE products 
        SET stock = stock + NEW.quantity
        WHERE id = NEW.product_id;
    ELSE
        -- Mismo producto, ajustar por diferencia
        SET quantity_diff = NEW.quantity - OLD.quantity;
        UPDATE products 
        SET stock = stock + quantity_diff
        WHERE id = NEW.product_id;
    END IF;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_DECREMENT_UPDATE
-- DESCRIPCIÓN: Ajusta el stock cuando se actualiza la cantidad en exit_note_detail
-- DISPARA: AFTER UPDATE en exit_note_detail
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_DECREMENT_UPDATE
AFTER UPDATE ON exit_note_detail
FOR EACH ROW
BEGIN
    DECLARE quantity_diff INT;
    
    -- Si cambió el producto, revertir el viejo y aplicar al nuevo
    IF OLD.product_id != NEW.product_id THEN
        -- Revertir stock del producto anterior (sumando lo que se había restado)
        UPDATE products 
        SET stock = stock + OLD.quantity
        WHERE id = OLD.product_id;
        
        -- Aplicar descuento al nuevo producto
        UPDATE products 
        SET stock = stock - NEW.quantity
        WHERE id = NEW.product_id;
    ELSE
        -- Mismo producto, ajustar por diferencia
        SET quantity_diff = NEW.quantity - OLD.quantity;
        UPDATE products 
        SET stock = stock - quantity_diff
        WHERE id = NEW.product_id;
    END IF;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_REVERT_ENTRY_DELETE
-- DESCRIPCIÓN: Revierte el stock cuando se elimina un detalle de entrada
-- DISPARA: AFTER DELETE en entry_note_detail
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_REVERT_ENTRY_DELETE
AFTER DELETE ON entry_note_detail
FOR EACH ROW
BEGIN
    UPDATE products 
    SET stock = stock - OLD.quantity
    WHERE id = OLD.product_id;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- TRIGGER: TR_STOCK_REVERT_EXIT_DELETE
-- DESCRIPCIÓN: Revierte el stock cuando se elimina un detalle de salida
-- DISPARA: AFTER DELETE en exit_note_detail
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE TRIGGER TR_STOCK_REVERT_EXIT_DELETE
AFTER DELETE ON exit_note_detail
FOR EACH ROW
BEGIN
    UPDATE products 
    SET stock = stock + OLD.quantity
    WHERE id = OLD.product_id;
END //

DELIMITER ;

-- ==============================================================================
-- SECCIÓN 2: PROCEDIMIENTOS ALMACENADOS
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- SP: SP_VALIDATE_STOCK
-- DESCRIPCIÓN: Valida si hay stock suficiente para una salida de producto.
--              Retorna 1 si hay stock suficiente, 0 si no hay.
-- PARÁMETROS:
--   - p_product_id: ID del producto a validar
--   - p_requested_quantity: Cantidad solicitada para la salida
-- RETORNA: Resultado con is_valid (1/0), current_stock, requested_quantity, message
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_VALIDATE_STOCK(
    IN p_product_id INT,
    IN p_requested_quantity INT
)
BEGIN
    DECLARE v_current_stock INT DEFAULT 0;
    DECLARE v_product_name VARCHAR(150);
    DECLARE v_is_valid BOOLEAN DEFAULT FALSE;
    
    -- Obtener el stock actual y nombre del producto
    SELECT stock, name 
    INTO v_current_stock, v_product_name
    FROM products 
    WHERE id = p_product_id AND is_active = TRUE;
    
    -- Verificar si el producto existe
    IF v_current_stock IS NULL THEN
        SELECT 
            0 AS is_valid,
            0 AS current_stock,
            p_requested_quantity AS requested_quantity,
            'Producto no encontrado o inactivo' AS message;
    ELSEIF v_current_stock >= p_requested_quantity THEN
        SELECT 
            1 AS is_valid,
            v_current_stock AS current_stock,
            p_requested_quantity AS requested_quantity,
            CONCAT('Stock suficiente para ', v_product_name) AS message;
    ELSE
        SELECT 
            0 AS is_valid,
            v_current_stock AS current_stock,
            p_requested_quantity AS requested_quantity,
            CONCAT('Stock insuficiente para ', v_product_name, '. Disponible: ', v_current_stock, ', Solicitado: ', p_requested_quantity) AS message;
    END IF;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_RECALCULATE_PO_TOTAL
-- DESCRIPCIÓN: Recalcula el total de una orden de compra basándose en sus detalles.
--              total = SUM(quantity * unit_price) de todos los detalles activos.
-- PARÁMETROS:
--   - p_order_id: ID de la orden de compra a recalcular
-- RETORNA: Nuevo total calculado y estado de la operación
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_RECALCULATE_PO_TOTAL(
    IN p_order_id INT
)
BEGIN
    DECLARE v_new_total DECIMAL(10, 2) DEFAULT 0;
    DECLARE v_order_exists BOOLEAN DEFAULT FALSE;
    
    -- Verificar si la orden existe
    SELECT EXISTS(
        SELECT 1 FROM purchase_order WHERE id = p_order_id AND is_active = TRUE
    ) INTO v_order_exists;
    
    IF NOT v_order_exists THEN
        SELECT 
            FALSE AS success,
            0 AS new_total,
            'Orden de compra no encontrada o inactiva' AS message;
    ELSE
        -- Calcular el nuevo total
        SELECT COALESCE(SUM(quantity * unit_price), 0)
        INTO v_new_total
        FROM purchase_order_detail 
        WHERE order_id = p_order_id AND is_active = TRUE;
        
        -- Actualizar el total en la orden
        UPDATE purchase_order 
        SET total = v_new_total
        WHERE id = p_order_id;
        
        -- Retornar resultado
        SELECT 
            TRUE AS success,
            v_new_total AS new_total,
            CONCAT('Total actualizado correctamente a ', v_new_total) AS message;
    END IF;
END //

DELIMITER ;

-- ==============================================================================
-- SECCIÓN 3: PROCEDIMIENTOS ALMACENADOS PARA REPORTES
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- SP: SP_GET_KARDEX_FISICO
-- DESCRIPCIÓN: Obtiene el kardex físico (movimientos de entrada y salida) de un
--              producto en un rango de fechas.
-- PARÁMETROS:
--   - p_product_id: ID del producto
--   - p_start_date: Fecha de inicio (YYYY-MM-DD)
--   - p_end_date: Fecha de fin (YYYY-MM-DD)
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_KARDEX_FISICO(
    IN p_product_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    -- Unión de movimientos de entrada y salida
    SELECT 
        movement_date,
        movement_type,
        reference,
        quantity,
        balance,
        supplier_customer_name
    FROM (
        -- Entradas (saldo positivo)
        SELECT 
            en.date AS movement_date,
            'ENTRADA' AS movement_type,
            en.reference,
            end.quantity,
            end.quantity AS balance,
            s.name AS supplier_customer_name
        FROM entry_note_detail end
        INNER JOIN entry_note en ON end.entry_id = en.id
        INNER JOIN suppliers s ON en.supplier_id = s.id
        WHERE end.product_id = p_product_id
            AND end.is_active = TRUE
            AND en.date BETWEEN p_start_date AND p_end_date
        
        UNION ALL
        
        -- Salidas (saldo negativo)
        SELECT 
            exn.date AS movement_date,
            'SALIDA' AS movement_type,
            exn.reference,
            exd.quantity,
            -exd.quantity AS balance,
            c.name AS supplier_customer_name
        FROM exit_note_detail exd
        INNER JOIN exit_note exn ON exd.exit_id = exn.id
        INNER JOIN customers c ON exn.customer_id = c.id
        WHERE exd.product_id = p_product_id
            AND exd.is_active = TRUE
            AND exn.date BETWEEN p_start_date AND p_end_date
    ) AS kardex
    ORDER BY movement_date ASC;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_GET_STOCK_CATEGORIA
-- DESCRIPCIÓN: Obtiene el stock actual de productos, opcionalmente filtrado por
--              categoría.
-- PARÁMETROS:
--   - p_category_id: ID de la categoría (NULL para todos)
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_STOCK_CATEGORIA(
    IN p_category_id INT
)
BEGIN
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        p.stock,
        p.sale_price,
        p.purchase_price
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN units u ON p.unit_id = u.id
    WHERE p.is_active = TRUE
        AND (p_category_id IS NULL OR p.category_id = p_category_id)
    ORDER BY c.name, p.name;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_GET_PURCHASE_HISTORY
-- DESCRIPCIÓN: Obtiene el historial de compras filtrado por proveedor y/o fechas.
--              Soporta parámetros nulos para consultas flexibles.
-- PARÁMETROS:
--   - p_supplier_id: ID del proveedor (NULL para todos)
--   - p_start_date: Fecha de inicio (NULL para sin límite inferior)
--   - p_end_date: Fecha de fin (NULL para sin límite superior)
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_PURCHASE_HISTORY(
    IN p_supplier_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        po.id AS order_id,
        po.date AS order_date,
        s.id AS supplier_id,
        s.name AS supplier_name,
        po.total,
        po.status,
        u.fullname AS created_by
    FROM purchase_order po
    INNER JOIN suppliers s ON po.supplier_id = s.id
    INNER JOIN users u ON po.user_id = u.id
    WHERE po.is_active = TRUE
        AND (p_supplier_id IS NULL OR po.supplier_id = p_supplier_id)
        AND (p_start_date IS NULL OR po.date >= p_start_date)
        AND (p_end_date IS NULL OR po.date <= p_end_date)
    ORDER BY po.date DESC;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_GET_TOP_SELLING
-- DESCRIPCIÓN: Obtiene los productos más vendidos ordenados por cantidad total.
-- PARÁMETROS:
--   - p_limit: Número máximo de productos a retornar
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_TOP_SELLING(
    IN p_limit INT
)
BEGIN
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        SUM(exd.quantity) AS total_sold,
        p.stock AS current_stock,
        p.sale_price
    FROM products p
    INNER JOIN exit_note_detail exd ON p.id = exd.product_id
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN units u ON p.unit_id = u.id
    WHERE p.is_active = TRUE AND exd.is_active = TRUE
    GROUP BY p.id, p.name, c.name, u.name, p.stock, p.sale_price
    ORDER BY total_sold DESC
    LIMIT p_limit;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_GET_LOW_STOCK
-- DESCRIPCIÓN: Obtiene productos con stock menor al umbral especificado.
-- PARÁMETROS:
--   - p_stock_threshold: Umbral mínimo de stock
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_LOW_STOCK(
    IN p_stock_threshold INT
)
BEGIN
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        u.name AS unit_name,
        p.stock AS current_stock,
        p_stock_threshold AS threshold,
        (p_stock_threshold - p.stock) AS deficit,
        p.purchase_price,
        s.name AS last_supplier
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN units u ON p.unit_id = u.id
    LEFT JOIN (
        -- Obtener el último proveedor de cada producto
        SELECT DISTINCT ON (end.product_id)
            end.product_id,
            s.name
        FROM entry_note_detail end
        INNER JOIN entry_note en ON end.entry_id = en.id
        INNER JOIN suppliers s ON en.supplier_id = s.id
        WHERE end.is_active = TRUE
        ORDER BY end.product_id, en.date DESC
    ) s ON p.id = s.product_id
    WHERE p.is_active = TRUE
        AND p.stock < p_stock_threshold
    ORDER BY p.stock ASC, p.name ASC;
END //

DELIMITER ;

-- ------------------------------------------------------------------------------
-- SP: SP_GET_STOCK_BY_PRODUCT
-- DESCRIPCIÓN: Obtiene el stock de un producto específico con su información completa.
-- PARÁMETROS:
--   - p_product_id: ID del producto (NULL para todos)
-- ------------------------------------------------------------------------------

DELIMITER //

CREATE PROCEDURE SP_GET_STOCK_BY_PRODUCT(
    IN p_product_id INT
)
BEGIN
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        c.id AS category_id,
        c.name AS category_name,
        u.id AS unit_id,
        u.name AS unit_name,
        p.stock,
        p.sale_price,
        p.purchase_price,
        (
            SELECT COALESCE(SUM(end.quantity), 0)
            FROM entry_note_detail end
            INNER JOIN entry_note en ON end.entry_id = en.id
            WHERE end.product_id = p.id AND end.is_active = TRUE
        ) AS total_entries,
        (
            SELECT COALESCE(SUM(exd.quantity), 0)
            FROM exit_note_detail exd
            INNER JOIN exit_note exn ON exd.exit_id = exn.id
            WHERE exd.product_id = p.id AND exd.is_active = TRUE
        ) AS total_exits
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN units u ON p.unit_id = u.id
    WHERE p.is_active = TRUE
        AND (p_product_id IS NULL OR p.id = p_product_id)
    ORDER BY p.name;
END //

DELIMITER ;

-- ==============================================================================
-- SECCIÓN 4: ÍNDICES PARA OPTIMIZACIÓN
-- ==============================================================================

-- Índices para mejorar el rendimiento de las consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_entry_note_detail_product ON entry_note_detail(product_id);
CREATE INDEX IF NOT EXISTS idx_entry_note_detail_entry ON entry_note_detail(entry_id);
CREATE INDEX IF NOT EXISTS idx_exit_note_detail_product ON exit_note_detail(product_id);
CREATE INDEX IF NOT EXISTS idx_exit_note_detail_exit ON exit_note_detail(exit_id);
CREATE INDEX IF NOT EXISTS idx_entry_note_date ON entry_note(date);
CREATE INDEX IF NOT EXISTS idx_exit_note_date ON exit_note(date);
CREATE INDEX IF NOT EXISTS idx_purchase_order_date ON purchase_order(date);
CREATE INDEX IF NOT EXISTS idx_purchase_order_supplier ON purchase_order(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);

-- ==============================================================================
-- FIN DEL ARCHIVO
-- ==============================================================================
