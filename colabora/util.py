import re
from spellchecker import SpellChecker
def revisa_tema(tema): 
    correcciones = []
    estado = 'Ok'
    
    spell = SpellChecker(language='es')
    incorrectas = spell.unknown(re.findall(r'\b\w+\b', tema))

    if incorrectas:
        correcciones.append(f'Revisar si la(s) palabra(s) "{", ".join(incorrectas)}" están bien escritas')
    if tema[-1] == '.':
        correcciones.append('El tema no debe llevar punto al final')
    if tema[0] == ' ' or tema[-1] == ' ':
        correcciones.append('El tema no debe llevar espacio ni al inicio ni al final')
    if re.search(r"(?<!\.)\n", tema):
        correcciones.append('El tema no debe llevar un renglón nuevo sin que vaya después de un punto')

    if len(correcciones) != 0:
        estado = 'Error'
        
    return estado, correcciones