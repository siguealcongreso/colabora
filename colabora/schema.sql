DROP TABLE IF EXISTS clasificacion;
DROP TABLE IF EXISTS asignacion;
DROP TABLE IF EXISTS entidad;
DROP TABLE IF EXISTS legislatura;
DROP TABLE IF EXISTS iniciativas;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS estado;

CREATE TABLE entidad (
    entidad_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE legislatura (
    legislatura_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    entidad_id INTEGER NOT NULL,
    FOREIGN KEY (entidad_id) REFERENCES entidad(entidad_id)
);

CREATE TABLE iniciativas (
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    cambios TEXT DEFAULT '',
    documento TEXT DEFAULT '',
    tema TEXT DEFAULT '',
    resumen TEXT DEFAULT '',
    comentario TEXT DEFAULT '',
    estado_id INTEGER REFERENCES estado(estado_id),
    PRIMARY KEY (legislatura_id, numero)
    );

CREATE TABLE areas (
    area_id INTEGER NOT NULL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
    );

CREATE TABLE usuarios (
    usuario_id INTEGER PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT DEFAULT '',
    rol TEXT DEFAULT '',
    activo DEFAULT 1,
    legislatura_id INTEGER,
    FOREIGN KEY (legislatura_id) REFERENCES legislatura(legislatura_id)
    );

CREATE TABLE clasificacion (
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    area_id INTEGER NOT NULL REFERENCES areas(area_id),
    PRIMARY KEY (legislatura_id, numero, area_id),
    FOREIGN KEY (legislatura_id, numero) REFERENCES iniciativas
);

CREATE TABLE asignacion (
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id),
    PRIMARY KEY (legislatura_id, numero, usuario_id),
    FOREIGN KEY (legislatura_id, numero) REFERENCES iniciativas
);

CREATE TABLE estado (
    estado_id INTEGER PRIMARY KEY,
    estado TEXT NOT NULL UNIQUE
);
