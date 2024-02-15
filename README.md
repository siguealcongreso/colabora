# colabora

colabora es una aplicación web para escribir, revisar y aprobar los
resúmenes de iniciativas.

## Para contribuir a la aplicación

1. Copia este repositorio a tu cuenta (Crea un fork)

2. Clona de tu repositorio a tu computadora:

       git clone git@github.com:<tu-usuario>/colabora.git

3. Crea un entorno virtual

       cd colabora
       python3 -m venv env

4. Instala la aplicación con sus dependencias en modo de desarrollo

       env/bin/pip install -e '.[test]'

5. Corre las pruebas

       env/bin/pytest --cov=colabora

6. Inicializa la base de datos

       env/bin/flask --app colabora.main shell
       >> import colabora.db
       >> colabora.db.init_db()
       >> exit()

7. Corre la aplicación

       env/bin/flask --debug --app colabora.main run

8. Crea una rama para las modificaciones

       git checkout -b agregar-mejora

9. Haz modificaciones

10. Empuja tus modificaciones a tu repositorio

11. Solicita que se incluyan tus cambios (Crea un Pull Request)

## Para generar la documentación

1. Instala la dependencia para la documentación

       env/bin/pip install -e '.[doc]'

2. Activa el entorno virtual

       . env/bin/activate

3. Genera la documentación

       cd docs
       make html

4. Navega a build/html/index.html