INSERT INTO entidad (nombre) VALUES ('entidad1');
INSERT INTO legislatura (nombre) VALUES ('legislatura1');
INSERT INTO estado (estado) VALUES ('estado1');

INSERT INTO iniciativas (entidad_id, legislatura_id, numero,
cambios, tema, resumen, comentario)
VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1, 'Cambios 1', 'tema1', 'resumen1', 'comentario1'
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


INSERT INTO usuarios (usuario, rol, contrasena)
VALUES ('usuario1', 'escritor', 'pbkdf2:sha256:260000$tO9sZi75hb37KUJx$31b698118aeaa310216e3817187df664592d953a7e509ef1b143e61d6e1a3ee6');

INSERT INTO asignacion (entidad_id, legislatura_id, numero, usuario_id) VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 1,
 (SELECT usuario_id FROM usuarios WHERE usuario='usuario1')
);

INSERT INTO usuarios (usuario, rol, contrasena)
VALUES ('usuario2', 'editor', 'pbkdf2:sha256:260000$kcXIu3KRdxMBnn7e$1f8b1e0734bde500c5db3401bda54177af962764086b9df337df77848438aa92');

INSERT INTO usuarios (usuario, rol, contrasena)
VALUES ('usuario3', 'admin', 'pbkdf2:sha256:260000$wwFM6rPwlrseIYi9$3fd438a00a0c40b250e1e8e82454f9b7fc6987d7d588bca40e8d2467894f9a81');


INSERT INTO iniciativas (entidad_id, legislatura_id, numero,
cambios, tema, resumen, comentario)
VALUES
((SELECT entidad_id FROM entidad WHERE nombre='entidad1'),
 (SELECT legislatura_id FROM legislatura WHERE nombre='legislatura1'),
 3, 'Cambios 3', 'tema3', 'resumen3', 'comentario3'
);
