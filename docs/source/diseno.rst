Diseño
======

General
-------

La aplicación está organizada en un paquete importable los siguientes
módulos:

- app.py
- db.py
- views.py
- main.py

La configuración es en el archivo `defaults.py`

Puede ser ejecutada en producción por Apache con `mod_wsgi` usando el
archivo `colabora.wsgi`.  Para desarrollo se puede usar `waitress`,
montando la aplicación en un punto idéntico como en producción.

El empaquetado se hace con `flit`.

Modelos
-------

La base de datos tiene las siguientes tablas:

.. table::
   :width: 100%
   :widths: 20,30,50

   +-----------------+-----------------------+-----------------------------------+
   | Tabla           |  Llave primaria       | Columnas                          |
   +=================+=======================+===================================+
   | iniciativas     |  entidad_id           | cambios                           |
   |                 |                       |                                   |
   |                 |  legislatura_id       | tema                              |
   |                 |                       |                                   |
   |                 |  numero               | resumen                           |
   |                 |                       |                                   |
   |                 |                       | comentario                        |
   |                 |                       |                                   |
   |                 |                       | estado                            |
   +-----------------+-----------------------+-----------------------------------+
   | entidad         |  entidad_id           | nombre UNIQUE                     |
   |                 |                       |                                   |
   |                 |                       |                                   |
   +-----------------+-----------------------+-----------------------------------+
   | legislatura     |  legislatura_id       | nombre UNIQUE                     |
   |                 |                       |                                   |
   |                 |                       |                                   |
   |                 |                       |                                   |
   |                 |                       |                                   |
   |                 |                       |                                   |
   |                 |                       |                                   |
   +-----------------+-----------------------+-----------------------------------+
   | usuarios        |  usuario_id           | usuario UNIQUE                    |
   |                 |                       |                                   |
   |                 |                       | rol                               |
   |                 |                       |                                   |
   |                 |                       | contrasena                        |
   |                 |                       |                                   |
   |                 |                       | activo                            |
   +-----------------+-----------------------+-----------------------------------+
   | areas           |  area_id              | nombre UNIQUE                     |
   |                 |                       |                                   |
   |                 |                       |                                   |
   |                 |                       |                                   |
   +-----------------+-----------------------+-----------------------------------+
   | asignacion      |  entidad_id           |                                   |
   |                 |                       |                                   |
   |                 |  legislatura_id       |                                   |
   |                 |                       |                                   |
   |                 |  numero               |                                   |
   |                 |                       |                                   |
   |                 |  usuario_id           |                                   |
   +-----------------+-----------------------+-----------------------------------+
   | clasificacion   |  entidad_id           |                                   |
   |                 |                       |                                   |
   |                 |  legislatura_id       |                                   |
   |                 |                       |                                   |
   |                 |  numero               |                                   |
   |                 |                       |                                   |
   |                 |  area_id              |                                   |
   +-----------------+-----------------------+-----------------------------------+

Una iniciativa se selecciona con la tríada ``entidad``, ``legislatura`` y ``numero``.
Por ejemplo *Jalisco, LXIII, 2561*.


Flujo
------

Se muestra la secuencia de utilización por usuario desde que llega al sitio,
ingresa con su cuenta, y realiza diversas operaciones.

.. table::
   :width: 100%
   :widths: 30,20,50

   +---------------------------+-------------+-----------------------------------+
   | Ruta                      |  Vista      |  Acción                           |
   +===========================+=============+===================================+
   | /                         |  lista      |Mostrar enlace a /login y          |
   |                           |             |la lista de todas las              |
   |                           |             |iniciativas.                       |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+
   | /login                    |  login      |GET: Mostrar formulario            |
   |                           |             |                                   |
   |                           |             |POST: validar                      |
   |                           |             |credenciales del usuario,          |
   |                           |             |iniciar sesión y reenviar          |
   |                           |             |a la página original.              |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+
   | /                         |  lista      |Mostrar:                           |
   |                           |             |                                   |
   | /iniciativas              |             |- Usuario                          |
   |                           |             |                                   |
   |                           |             |- Un botón "terminar               |
   |                           |             |  sesión" que envía a              |
   |                           |             |  /logout                          |
   |                           |             |                                   |
   |                           |             |- Un botón "mis                    |
   |                           |             |  iniciativas" que envía           |
   |                           |             |  a /iniciativas, o un botón "todas|
   |                           |             |  las iniciativas que envía a /.   |
   |                           |             |                                   |
   |                           |             |- Un botón                         |
   |                           |             |  "editar" para editores           |
   |                           |             |  y admin.                         |
   |                           |             |                                   |
   |                           |             |y la lista de todas las            |
   |                           |             |iniciativas. Cada ficha            |
   |                           |             |tiene:                             |
   |                           |             |                                   |
   |                           |             |- Un botón "editar" junto          |
   |                           |             |  a Tema que envía a               |
   |                           |             |  /edita/{numero}                  |
   |                           |             |                                   |
   |                           |             |- Un botón "editar" junto          |
   |                           |             |  a Comentario que envía           |
   |                           |             |  a /comenta{numero}               |
   +---------------------------+-------------+-----------------------------------+
   | /iniciativas/             | crea        |POST:                              |
   |                           |             |                                   |
   |                           |             |Recibe cambios.                    |
   |                           |             |                                   |
   |                           |             |Insert registro en iniciativas.    |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+
   | /asigna                   | asigna      |GET: Mostrar                       |
   |                           |             |                                   |
   |                           |             |- Una lista de selección           |
   |                           |             |  con los usuarios.                |
   |                           |             |                                   |
   |                           |             |- Un botón "asignar" que           |
   |                           |             |  envía el formulario.             |
   |                           |             |                                   |
   |                           |             |- Un botón "mostrar                |
   |                           |             |  asignadas" que envía el          |
   |                           |             |  formulario.                      |
   |                           |             |                                   |
   |                           |             |- La lista de iniciativas          |
   |                           |             |  no asignadas.                    |
   |                           |             |                                   |
   |                           |             |- Cada ficha dice                  |
   |                           |             |  "Asignar" seguida de             |
   |                           |             |  una caja para marcar.            |
   |                           |             |                                   |
   |                           |             |POST: Si se oprimió "asignar", toma|
   |                           |             |el usuario y la lista de números,  |
   |                           |             |actualiza la base de datos, y envía|
   |                           |             |a /asigna.  Ya no se muestran las  |
   |                           |             |recién asignadas.                  |
   |                           |             |                                   |
   |                           |             |Si se oprimió "mostrar asignadas"  |
   |                           |             |con un usuario, enviar a /asigna   |
   |                           |             |solamente con los iniciativas de   |
   |                           |             |ese usuario.                       |
   +---------------------------+-------------+-----------------------------------+
   | /logout                   | logout      |Cerrar la sesión del               |
   |                           |             |usuario y reenvíar a la            |
   |                           |             |página original.                   |
   +---------------------------+-------------+-----------------------------------+
   | /crea/{numero}            | crea        |POST:                              |
   |                           |             |                                   |
   |                           |             |Recibe cambios.                    |
   |                           |             |                                   |
   |                           |             |Insert registro en iniciativas.    |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+
   | /edita/{numero}           | edita       |Mostrar:                           |
   |                           |             |                                   |
   |                           |             |Un botón "enviar" que              |
   |                           |             |envía el formulario.               |
   |                           |             |                                   |
   |                           |             |Un botón "Cancelar" que            |
   |                           |             |envía a /iniciativas o a           |
   |                           |             |/lista.                            |
   |                           |             |                                   |
   |                           |             |La iniciativa con Tema, Resumen y  |
   |                           |             |Área editables.                    |
   |                           |             |                                   |
   |                           |             |Si es editor, Comentario           |
   |                           |             |es editable.                       |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+
   | /comenta/{numero}         | comenta     | Mostrar iniciativa con            |
   |                           |             | formulario                        |
   +---------------------------+-------------+-----------------------------------+
   | /aprueba/{numero}         | aprueba     |                                   |
   |                           |             |                                   |
   |                           |             |                                   |
   +---------------------------+-------------+-----------------------------------+



Seguridad
---------

Hay los siguientes roles:

``escritor``

  Puede escribir en tema, resumen y área de las iniciativas que tienen asignadas.  No
  puede escribir si la iniciativa ya fue aprobada por un editor.

``editor``

  Puede escribir en comentarios de cualquier iniciativa. Puede
  escribir en tema, resumen y área de cualquier iniciativa.  Puede aprobar cualquier
  iniciativa.

``admin``

  Puede escribir en asignada de cualquier iniciativa, además de los permisos de
  ``editor``.

