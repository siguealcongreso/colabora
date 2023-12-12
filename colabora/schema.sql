DROP TABLE IF EXISTS iniciativas;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE iniciativas (
    id INTEGER PRIMARY KEY,
    legislatura TEXT NOT NULL,
    numero TEXT NOT NULL,
    cambios TEXT DEFAULT '',
    tema TEXT DEFAULT '',
    resumen TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    comentario TEXT DEFAULT '',
    autor TEXT DEFAULT '',
    estado TEXT DEFAULT ''
    );

CREATE TABLE areas (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
    );

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    usuario TEXT DEFAULT '',
    contrasena TEXT DEFAULT '',
    rol TEXT DEFAULT ''
    );
