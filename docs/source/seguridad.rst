Seguridad
=========

Introducción
------------

Para acceder al contenido de Colabora, se utiliza un sistema de acceso por usuario, contraseña 
y rol_: característica que determina el contenido a renderizar en las vistas y las tareas por cumplir.

Un nuevo visitante puede crear una cuenta por sí solo, recibiendo el rol de escritor_ al registrarse.
Para asegurarnos que elijan una contraseña segura, Colabora importa el modulo zxcvbn_ que califica su fortaleza.

Para autorizar las operaciones CRUD de la API, se obtiene una llave al hacer log in con un usuario y contraseña.

.. _zxcvbn: https://zxcvbn-ts.github.io/zxcvbn/

Elementos
---------

Acceso
------

.. _rol:

Hay los siguientes roles:

.. _escritor:

``escritor``

  Puede escribir en tema, resumen y área de las iniciativas que tienen asignadas.  No
  puede escribir si la iniciativa ya fue aprobada por un editor.

``editor``

  Puede escribir en comentarios de cualquier iniciativa. Puede
  escribir en tema, resumen y área de cualquier iniciativa.  Puede aprobar cualquier
  iniciativa.

.. _administrador:

``admin``

  Puede escribir en asignada de cualquier iniciativa, además de los permisos de editor.
  ``editor``.