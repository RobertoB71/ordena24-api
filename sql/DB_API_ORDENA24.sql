CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL,
    categoria_id INTEGER REFERENCES categorias(id),
    disponible BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cliente_nombre VARCHAR(150) NOT NULL,
    cliente_email VARCHAR(150),
    direccion_entrega TEXT NOT NULL,
    telefono VARCHAR(30),
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'Pendiente',
    registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    pedido_id INTEGER REFERENCES pedidos(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

INSERT INTO categorias (nombre, descripcion) VALUES
('Comidas rápidas', 'Hamburguesas, papas fritas y combos.'),
('Bebidas', 'Sodas, jugos y bebidas frías.'),
('Postres', 'Dulces, pasteles y postres.');

INSERT INTO productos (nombre, descripcion, precio, categoria_id, disponible) VALUES
('Hamburguesa Clásica', 'Hamburguesa con carne, queso, lechuga y tomate.', 6.50, 1, TRUE),
('Papas Fritas', 'Porción mediana de papas fritas.', 2.75, 1, TRUE),
('Soda', 'Bebida fría en lata.', 1.50, 2, TRUE);