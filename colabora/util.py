import re

def revisa_tema(tema): 
    correcciones = []
    estado = 'Ok'
    if tema[-1] == '.':
        correcciones.append('El tema no debe llevar punto al final')
    if tema[0] or tema[-1] == ' ':
        correcciones.append('El tema no debe llevar espacio ni al inicio ni al final')
    if re.search(r"(?<!\.)\n", tema):
        correcciones.append('El tema no debe llevar un renglón nuevo sin que vaya después de un punto')
    # TO-DO: Agregar spell checker en español

    if len(correcciones) != 0:
        estado = 'Error'
        
    return estado, correcciones