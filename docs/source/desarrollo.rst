==========
Desarrollo
==========

El desarrollo de Colabora es mediante la metodología `Test-driven
development <https://en.wikipedia.org/wiki/Test-driven_development>`_
o TDD.

Herramientas
------------

Se utiliza el framework de pruebas `pytest
<https://docs.pytest.org/en/stable/>`_ como se sugiere en la
documentación de Flask.  El módulo `coverage
<https://coverage.readthedocs.io/>`_ se usa desde pytest para mostrar
el porcentaje de las líneas del código que están ejercitadas por las
pruebas, que debe ser el 100%.

Organización
------------

La carpeta `tests` tiene los archivos `test_*.py` de pruebas. El
archivo `conftest.py` tiene algunos *fixtures* y *mocks*.

Las funciones para crear y verificar el hash de la contraseña de
usuario son remplazadas por sendos `mock` durante las pruebas.  Esto
permite escribir los hash de contraseña en los datos de prueba
como *contraseña:hashed*.

Datos de prueba
---------------

La base de datos durante las pruebas se construye usando las tablas en
`schema.sql` y se agregan los datos de pruebas en `data.sql`. Estos
datos incluyen:

#. Generales

   - entidad `entidad1`, legislatura `legislatura1`
   - estado `estado1`
   - area `area1` y `area2`

#. Usuarios

   - `usuario1` escritor
   - `usuario2` editor
   - `usuario3` admin
   - `usuario4` escritor

#. Iniciativas

   - `entidad1` `legislatura1` 1
   - `entidad1` `legislatura1` 3

#. Asociaciones

   - asignación: `iniciativa 1` - `usuario1`
   - clasificación: `iniciativa 3` - `area1` y `area2`


Cambios a la base de datos
--------------------------

En algún momento pueden hacer falta uno o más cambios en la base de
datos, como agregar una columna, remover un límite en una columna,
agregar una tabla, etc.

Los pasos a seguir son:

#. Hacer los cambios en `schema.sql` y `data.sql`

#. Ejecutar ambos archivos manualmente y probar los resultados
   realizando algunas consultas

#. Correr las pruebas

#. Actualizar las funciones que lo requieran en el módulo `db`

#. Agregar funciones que hagan falta al módulo `db`

#. Preparar un guión de migración que haga los cambios del punto 1.

#. Aplicar el guión de migración a la base de datos para pruebas (Ver
   la siguiente sección).

#. Ejecutar la aplicación localmente con la base de datos migrada y
   validar los resultados.

Base de datos para pruebas
--------------------------

Para usar en el entorno de desarrollo una base de datos con los datos
actuales, se puede tomar una copia de la base actual y se asigna una
contraseña de prueba a todos los usuarios. El comando a usar es::

  HASH=$(python3 -c "import werkzeug.security; print(werkzeug.security.generate_password_hash('test'))")
  sqlite3 colabora.sqlite "UPDATE usuarios SET contrasena=$HASH;"


Despliegue al servidor
----------------------

Cuando se tiene ya probada una versión de la aplicación, se siguen
estos pasos para instalarla en el servidor:

#. Actualizar la versión en `colabora/__init__.py`

#. Crear un tag

#. Crear un wheel para instalar::

     flit build

#. Copiar `colabora-0.XX-py2.py3-none-any.whl` al servidor

#. Desempacar

#. Crear el entorno virtual e instalar el proyecto en modo de
   desarrollo.

#. Aplicar el guión de migración a la base de datos de producción.

#. Actualizar la configuración del servidor de HTTP.
