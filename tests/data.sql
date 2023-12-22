INSERT INTO estado (nombre) VALUES ('estado1');
INSERT INTO legislatura (nombre) VALUES ('legislatura1');

INSERT INTO iniciativas (estado_id, legislatura_id, numero,
cambios, tema, resumen, comentario, estado)
VALUES
((SELECT estado_id FROM estado WHERE nombre='estado1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1, 'Cambios 1', 'tema1', 'resumen1', 'comentario1', 'estado1'
);

INSERT INTO areas (nombre)
VALUES ('area1');

INSERT INTO clasificacion (estado_id, legislatura_id, numero, area_id) VALUES
((SELECT estado_id FROM estado WHERE nombre='estado1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1,
 (SELECT area_id FROM areas WHERE nombre='area1')
);

INSERT INTO areas (nombre)
VALUES ('area2');


INSERT INTO usuarios (usuario, rol)
VALUES ('usuario1', 'escritor');

INSERT INTO asignacion (estado_id, legislatura_id, numero, usuario_id) VALUES
((SELECT estado_id FROM estado WHERE nombre='estado1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1,
 (SELECT usuario_id FROM usuarios WHERE usuario='usuario1')
);

INSERT INTO usuarios (usuario, rol)
VALUES ('usuario2', 'editor');

INSERT INTO usuarios (usuario, rol)
VALUES ('usuario3', 'admin');


INSERT INTO iniciativas (estado_id, legislatura_id, numero,
cambios, tema, resumen, comentario, estado)
VALUES
((SELECT estado_id FROM estado WHERE nombre='estado1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 3, 'Cambios 3', 'tema3', 'resumen3', 'comentario3', 'estado3'
);
