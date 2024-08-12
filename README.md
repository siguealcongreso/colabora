# colabora

colabora es una aplicación web para escribir, revisar y aprobar los
resúmenes de iniciativas.

## Para contribuir a la aplicación

### Preparación

1. Copia este repositorio a tu cuenta en GitHub (Crea un fork)

2. Clona de tu repositorio a tu computadora, se crea el remote `origin`:

       git clone git@github.com:<tu-usuario>/colabora.git

3. Agrega un remote `upstream`:

       git remote add upstream https://github.com/siguealcongreso/colabora.git

4. Configura git para hacer pull de `main` en `upstream` y siempre hacer push
a `origin`:

       git config --local branch.main.remote upstream
       git remote set-url --push upstream git@github.com:<tu-usuario>/colabora.git

5. Crea un entorno virtual

       python3 -m venv env

6. Activa el entorno virtual

       . env/bin/activate

7. Instala la aplicación con sus dependencias en modo de desarrollo

       pip install -e '.[test]'

8. Corre las pruebas

       pytest --cov=colabora

9. Inicializa la base de datos

       flask --app colabora.main shell
       >> from colabora.db import init_db
       >> init_db()
       >> exit()

10. Corre la aplicación

       flask --debug --app colabora.main run

11. Visita http://localhost:5000

### Trabajo en un Issue

1. Actualiza la rama `main` de tu repositorio local con los cambios más
recientes del repositorio original:

       git checkout main
       git pull upstream

2. Crea una nueva rama en donde van a ir los cambios en los que trabajes.

       git checkout -b issue-48 main

3. Haz modificaciones


4. Activa el entorno virtual

       . env/bin/activate

5. Corre la aplicación

       flask --debug --app colabora.main run

6. Visita http://localhost:5000 para revisar las modficaciones

7. Corre las pruebas

       pytest --cov=colabora

8. Realiza uno o más commits en tu computadora

9. Empuja la rama con tus modificaciones a tu repositorio en GitHub

10. Solicita que se incluyan tus cambios (Crea un Pull Request)

11. Una vez que se aprobó el Pull Request, borra la rama del issue:

       git branch -d issue-48
       git push -d origin issue-48

## Para generar la documentación

1. Instala la dependencia para la documentación

       env/bin/pip install -e '.[doc]'

2. Activa el entorno virtual

       . env/bin/activate

3. Genera la documentación

       cd docs
       make html

4. Navega a build/html/index.html