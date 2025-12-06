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
