CREATE INDEX IF NOT EXISTS idx_entry_note_detail_product ON entry_note_detail(product_id);
CREATE INDEX IF NOT EXISTS idx_entry_note_detail_entry ON entry_note_detail(entry_id);
CREATE INDEX IF NOT EXISTS idx_exit_note_detail_product ON exit_note_detail(product_id);
CREATE INDEX IF NOT EXISTS idx_exit_note_detail_exit ON exit_note_detail(exit_id);
CREATE INDEX IF NOT EXISTS idx_entry_note_date ON entry_note(date);
CREATE INDEX IF NOT EXISTS idx_exit_note_date ON exit_note(date);
CREATE INDEX IF NOT EXISTS idx_purchase_order_date ON purchase_order(date);
