from colabora.util import revisa_tema

def test_revisa_tema_punto_final():
    tema = 'Salud.'
    result = revisa_tema(tema)
    assert result == ('Error', ['El tema no debe llevar punto al final'])

def test_revisa_tema_espacio():
    tema = ' Salud'
    result = revisa_tema(tema)
    assert result == ('Error', ['El tema no debe llevar espacio ni al inicio ni al final'])

def test_revisa_tema_punto_renglon():
    tema = 'Salud\nSalud'
    result = revisa_tema(tema)
    assert result == ('Error', ['El tema no debe llevar un renglón nuevo sin que vaya después de un punto'])

def test_revisa_tema_correcto():
    tema = 'Salud'
    result = revisa_tema(tema)
    assert result == ('Ok', [])
