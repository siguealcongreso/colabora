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

7. Corre las pruebas y mide la cobertura

       pytest --cov
       pytest --cov --cov-report=term-missing

8. Revisa que tus modificaciones cumplen con los *Requerimientos para
los commits* que se describen en la siguiente sección.

9. Realiza uno o más commits en tu computadora

10. Empuja la rama con tus modificaciones a tu repositorio en GitHub

11. Solicita que se incluyan tus cambios (Crea un Pull Request)

12. Una vez que se aprobó el Pull Request, borra la rama del issue:

       git branch -d issue-48
       git push -d origin issue-48


## Requerimientos para los commits

1. Revisa que `git diff --check` no reporte renglones con espacios al
final en los archivos que modificas.

2. Modifica solamente los renglones necesarios para resolver el issue
en cuestión. No hagas cambios cosméticos en otros renglones del código
que no tienen que ver con lo que estás mejorando.

3. Si estás agregando texto, revisa que cumple con la Ortografía y
Gramática.

## Para revisar un Pull Request

1. Consulta el Issue indicado en `Development` del Pull Request para
conocer la descripción y el resultado esperado.

2. Actualiza la rama `main` de tu repositorio local con los cambios más
recientes del repositorio original:

       git checkout main
       git pull upstream

3. Activa el entorno virtual

       . env/bin/activate

4. Corre la aplicación

       flask --debug --app colabora.main run

5. Observa que se reproduce la situación actual en la descripción del
Issue.

6. Si aún no tienes una referencia remota al repositorio de donde vienen
los cambios del Pull Request, crea una y descarga sus ramas:

       git remote add <nombre> <repositorio>
       git fetch <nombre>

7. Cambia a la rama origen del Pull Request en ese repositorio:

       git checkout `nombre:rama`

8. Observa si se obtiene el resultado esperado del Issue.

9. Revisa la descripción, los cambios realizados y la razón de la
modificación en el Pull Request.

10. Revisa los cambios realizados por el Pull Request:

       git log -p main..`nombr`:rama`

11. Revisa que la cobertura del código y de las pruebas está completa:

       pytest --cov --cov-report=term-missing --cov-branch

12. Una vez que termines los pasos anteriores, haz clic en `Files
changed` del Pull Request y después en el botón verde `Review
changes`.

13. Si todo está bien, escribe `Revisado`.

14. Si encontraste algún problema o tienes alguna duda, describe el
problema o pregunta la información que sea necesaria.

15. Haz clic en `Submit review`.

## Para generar la documentación

1. Activa el entorno virtual

       . env/bin/activate

2. Instala la dependencia para la documentación

       pip install -e '.[doc]'

3. Genera la documentación

       cd docs
       make html

4. Navega a `build/html/index.html`