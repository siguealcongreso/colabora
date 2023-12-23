DROP TABLE IF EXISTS clasificacion;
DROP TABLE IF EXISTS asignacion;
DROP TABLE IF EXISTS entidad;
DROP TABLE IF EXISTS legislatura;
DROP TABLE IF EXISTS iniciativas;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE entidad (
    entidad_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE legislatura (
    legislatura_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE iniciativas (
    entidad_id INTEGER NOT NULL,
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    cambios TEXT DEFAULT '',
    tema TEXT DEFAULT '',
    resumen TEXT DEFAULT '',
    comentario TEXT DEFAULT '',
    estado TEXT DEFAULT '',
    PRIMARY KEY (entidad_id, legislatura_id, numero)
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
    activo DEFAULT 1
    );

CREATE TABLE clasificacion (
    entidad_id INTEGER NOT NULL,
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    area_id INTEGER NOT NULL REFERENCES areas(area_id),
    PRIMARY KEY (entidad_id, legislatura_id, numero, area_id),
    FOREIGN KEY (entidad_id, legislatura_id, numero) REFERENCES iniciativas
);

CREATE TABLE asignacion (
    entidad_id INTEGER NOT NULL,
    legislatura_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id),
    PRIMARY KEY (entidad_id, legislatura_id, numero, usuario_id),
    FOREIGN KEY (entidad_id, legislatura_id, numero) REFERENCES iniciativas
);
