-- ============================================
-- 1. TABLAS DE SEGURIDAD
-- ============================================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    pass TEXT NOT NULL,
    rol_id INT NOT NULL,
    estado BOOLEAN DEFAULT TRUE
);


-- ============================================
-- 2. TABLAS BASE
-- ============================================

CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE unidades_medida (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    abreviatura VARCHAR(10) NOT NULL
);


-- ============================================
-- 3. PRODUCTOS
-- ============================================

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria_id INT,
    unidad_id INT,
    stock_actual NUMERIC(10,2) DEFAULT 0,
    stock_min NUMERIC(10,2) DEFAULT 0,
    stock_max NUMERIC(10,2) DEFAULT 0,
    precio NUMERIC(10,2) DEFAULT 0,
    estado BOOLEAN DEFAULT TRUE
);


-- ============================================
-- 4. PROVEEDORES Y CLIENTES
-- ============================================

CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    ruc VARCHAR(11),
    telefono VARCHAR(20),
    direccion TEXT,
    correo VARCHAR(100),
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    correo VARCHAR(100),
    estado BOOLEAN DEFAULT TRUE
);


-- ============================================
-- 5. MOVIMIENTOS (INGRESOS / SALIDAS)
-- ============================================

CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,   -- 'INGRESO' | 'SALIDA'
    usuario_id INT,
    proveedor_id INT,
    cliente_id INT,
    fecha TIMESTAMP DEFAULT NOW(),
    observacion TEXT,
    estado VARCHAR(20) DEFAULT 'REGISTRADO'
);


-- ============================================
-- 6. DETALLE DE MOVIMIENTOS
-- ============================================

CREATE TABLE detalle_movimientos (
    id SERIAL PRIMARY KEY,
    movimiento_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad NUMERIC(10,2) NOT NULL,
    precio NUMERIC(10,2)
);


-- ============================================
-- 7. ORDENES DE COMPRA
-- ============================================

CREATE TABLE ordenes_compra (
    id SERIAL PRIMARY KEY,
    proveedor_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT NOW(),
    total NUMERIC(10,2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'PENDIENTE'
);


-- ============================================
-- 8. DETALLE DE ORDENES DE COMPRA
-- ============================================

CREATE TABLE detalle_orden_compra (
    id SERIAL PRIMARY KEY,
    orden_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad NUMERIC(10,2) NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL
);

-- ============================================
-- FOREIGN KEYS (Después de crear tablas)
-- ============================================

-- Usuarios → Roles
ALTER TABLE usuarios
ADD CONSTRAINT fk_usuarios_rol
FOREIGN KEY (rol_id) REFERENCES roles(id);

-- Productos → Categorías
ALTER TABLE productos
ADD CONSTRAINT fk_productos_categoria
FOREIGN KEY (categoria_id) REFERENCES categorias(id);

-- Productos → Unidades de medida
ALTER TABLE productos
ADD CONSTRAINT fk_productos_unidad
FOREIGN KEY (unidad_id) REFERENCES unidades_medida(id);

-- Movimientos → Usuarios
ALTER TABLE movimientos
ADD CONSTRAINT fk_movimientos_usuario
FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Movimientos → Proveedores
ALTER TABLE movimientos
ADD CONSTRAINT fk_movimientos_proveedor
FOREIGN KEY (proveedor_id) REFERENCES proveedores(id);

-- Movimientos → Clientes
ALTER TABLE movimientos
ADD CONSTRAINT fk_movimientos_cliente
FOREIGN KEY (cliente_id) REFERENCES clientes(id);

-- Detalle movimientos → Movimiento
ALTER TABLE detalle_movimientos
ADD CONSTRAINT fk_detalle_mov_mov
FOREIGN KEY (movimiento_id) 
REFERENCES movimientos(id)
ON DELETE CASCADE;

-- Detalle movimientos → Producto
ALTER TABLE detalle_movimientos
ADD CONSTRAINT fk_detalle_mov_prod
FOREIGN KEY (producto_id) REFERENCES productos(id);

-- Orden compra → Proveedor
ALTER TABLE ordenes_compra
ADD CONSTRAINT fk_orden_proveedor
FOREIGN KEY (proveedor_id) REFERENCES proveedores(id);

-- Detalle orden compra → Orden compra
ALTER TABLE detalle_orden_compra
ADD CONSTRAINT fk_detalle_orden
FOREIGN KEY (orden_id) 
REFERENCES ordenes_compra(id)
ON DELETE CASCADE;

-- Detalle orden compra → Producto
ALTER TABLE detalle_orden_compra
ADD CONSTRAINT fk_detalle_prod
FOREIGN KEY (producto_id) REFERENCES productos(id);
