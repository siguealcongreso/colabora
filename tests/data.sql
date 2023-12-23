INSERT INTO entidad (nombre) VALUES ('entidad1');
INSERT INTO legislatura (nombre) VALUES ('legislatura1');

INSERT INTO iniciativas (entidad_id, legislatura_id, numero,
cambios, tema, resumen, comentario, estado)
VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1, 'Cambios 1', 'tema1', 'resumen1', 'comentario1', 'estado1'
);

INSERT INTO areas (nombre)
VALUES ('area1');

INSERT INTO clasificacion (entidad_id, legislatura_id, numero, area_id) VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1,
 (SELECT area_id FROM areas WHERE nombre='area1')
);

INSERT INTO areas (nombre)
VALUES ('area2');


INSERT INTO usuarios (usuario, rol)
VALUES ('usuario1', 'escritor');

INSERT INTO asignacion (entidad_id, legislatura_id, numero, usuario_id) VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1,
 (SELECT usuario_id FROM usuarios WHERE usuario='usuario1')
);

INSERT INTO usuarios (usuario, rol)
VALUES ('usuario2', 'editor');

INSERT INTO usuarios (usuario, rol)
VALUES ('usuario3', 'admin');


INSERT INTO iniciativas (entidad_id, legislatura_id, numero,
cambios, tema, resumen, comentario, estado)
VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 3, 'Cambios 3', 'tema3', 'resumen3', 'comentario3', 'estado3'
);
