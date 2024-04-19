from pypdf.generic._base import DictionaryObject, NumberObject, TextStringObject

def convert_to_stream_format(annotation):
    if "/DA" in annotation:
        da_value = annotation["/DA"]
        if isinstance(da_value, TextStringObject):
            stream_da = convert_da_to_stream_format(da_value)
            annotation[NameObject("/DA")] = TextStringObject(stream_da)
    
    if "/DS" in annotation:
        del annotation["/DS"]
    
    return annotation

def convert_to_current_format(annotation):
    if "/DA" in annotation:
        da_value = annotation["/DA"]
        if isinstance(da_value, TextStringObject):
            current_da = convert_stream_format_to_da(da_value)
            annotation[NameObject("/DA")] = TextStringObject(current_da)
    
    return annotation

def convert_da_to_stream_format(da_value):
    # Implement the conversion logic from the current /DA format to Stream-Format
    # This function should handle various /DA formats and convert them to Stream-Format
    # Example conversion:
    # "0.9333333333333333 0.9333333333333333 0.9333333333333333 rg"
    # to "/Helv 10.5 Tf 0 Tc 11.76 TL 0 0.470588 0.831373 rg"
    # Implement a more robust conversion logic based on the specific requirements
    stream_da = ""
    # Conversion logic goes here
    return stream_da

def convert_stream_format_to_da(stream_value):
    # Implement the conversion logic from Stream-Format to the current /DA format
    # This function should handle various Stream-Format values and convert them to the current /DA format
    # Implement a more robust conversion logic based on the specific requirements
    current_da = ""
    # Conversion logic goes here
    return current_da