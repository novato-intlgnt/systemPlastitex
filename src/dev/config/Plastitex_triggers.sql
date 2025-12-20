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
-- Triggers para entry_note_detail
-- ------------------------------------------------------------------------------

-- Incremento de stock al insertar
DROP TRIGGER IF EXISTS tr_stock_increment ON entry_note_detail;
CREATE TRIGGER tr_stock_increment
AFTER INSERT ON entry_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_increment();

-- Ajuste de stock al actualizar cantidad/producto
DROP TRIGGER IF EXISTS tr_stock_increment_update ON entry_note_detail;
CREATE TRIGGER tr_stock_increment_update
AFTER UPDATE ON entry_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_increment_update();

-- Reversión de stock al eliminar entrada
DROP TRIGGER IF EXISTS tr_stock_revert_entry_delete ON entry_note_detail;
CREATE TRIGGER tr_stock_revert_entry_delete
AFTER DELETE ON entry_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_revert_entry_delete();

-- ------------------------------------------------------------------------------
-- Triggers para exit_note_detail
-- ------------------------------------------------------------------------------

-- Decremento de stock al insertar
DROP TRIGGER IF EXISTS tr_stock_decrement ON exit_note_detail;
CREATE TRIGGER tr_stock_decrement
AFTER INSERT ON exit_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_decrement();

-- Ajuste de stock al actualizar cantidad/producto
DROP TRIGGER IF EXISTS tr_stock_decrement_update ON exit_note_detail;
CREATE TRIGGER tr_stock_decrement_update
AFTER UPDATE ON exit_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_decrement_update();

-- Reversión de stock al eliminar salida
DROP TRIGGER IF EXISTS tr_stock_revert_exit_delete ON exit_note_detail;
CREATE TRIGGER tr_stock_revert_exit_delete
AFTER DELETE ON exit_note_detail
FOR EACH ROW EXECUTE FUNCTION tf_stock_revert_exit_delete();
