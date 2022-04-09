import io

from PyPDF2.generic import NameObject


def test_nameobject_decoding():
    czech_diacritics_pangram = "Vyciď křišťálový nůž ó učiň úděsné líbivým"
    name_string = "/" + czech_diacritics_pangram.replace(" ", "")
    utf8 = name_string.encode("utf-8")
    latin1 = name_string.encode("latin-1", errors="ignore")
    latin2 = name_string.encode("iso-8859-2")
    assert NameObject.readFromStream(io.BytesIO(utf8), None) == name_string
    assert NameObject.readFromStream(io.BytesIO(latin1), None) == latin1.decode("latin-1")
    assert NameObject.readFromStream(io.BytesIO(latin1), None) != name_string
    assert NameObject.readFromStream(io.BytesIO(latin2), None) == latin2.decode("latin-1")
    assert NameObject.readFromStream(io.BytesIO(latin2), None) != name_string
