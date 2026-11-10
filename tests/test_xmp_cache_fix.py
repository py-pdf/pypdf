import time
from pypdf.generic import StreamObject
from pypdf.xmp import XmpInformation

def test_xmp_missing_properties_cache():
    """
    Test that querying missing properties in XMP metadata uses the cache 
    and does not repeatedly traverse the XML tree (which caused O(N^2) DoS).
    """
    num_nodes = 1000
    evil_xml = ['<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>']
    evil_xml.append('<x:xmpmeta xmlns:x="adobe:ns:meta/">')
    evil_xml.append('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">')
    
    for _ in range(num_nodes):
        evil_xml.append('<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:dummy>test</dc:dummy></rdf:Description>')
        
    evil_xml.append('</rdf:RDF>')
    evil_xml.append('</x:xmpmeta>')
    evil_xml.append('<?xpacket end="r"?>')

    xmp_data = "\n".join(evil_xml).encode("utf-8")
    stream = StreamObject()
    stream.set_data(xmp_data)
    xmp = XmpInformation(stream)

    start_time = time.time()
    for _ in range(10):
        assert xmp.dc_title is None
        assert xmp.dc_creator is None
        assert xmp.pdf_keywords is None
        
    elapsed_time = time.time() - start_time
    assert elapsed_time < 1.0, f"Test took too long ({elapsed_time}s), cache is likely broken!"
