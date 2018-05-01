'''
    Helper module for permissions


TABLE 3.15 User access permissions

BIT POSITION                    MEANING
1-2                             Reserved; must be 0.
3	                            (Revision 2) Print the document.
                                (Revision 3) Print the document (possibly not at the highest quality
                                level, depending on whether bit 12 is also set).
4	                            Modify the contents of the document by operations other than those controlled 
                                by bits 6, 9, and 11.
5	                            (Revision 2) Copy or otherwise extract text and graphics from the document, 
                                including extracting text and graphics (in support of accessibility to 
                                disabled users or for other purposes).
                                (Revision 3) Copy or otherwise extract text and graphics from the document 
                                by operations other than that controlled by bit 10.
6	                            Add or modify text annotations, fill in interactive form fields, and, 
                                if bit 4 is also set, create or modify interactive form fields 
                                (including signature fields).
7-8	                            Reserved; must be 1.
9	                            (Revision 3 only) Fill in existing interactive form fields (including 
                                signature fields), even if bit 6 is clear.
10	                            (Revision 3 only) Extract text and graphics (in support of accessibility 
                                to disabled users or for other purposes).
11	                            (Revision 3 only) Assemble the document (insert, rotate, or delete pages 
                                and create bookmarks or thumbnail images), even if bit 4 is clear.
12	                            (Revision 3 only) Print the document to a representation from which a 
                                faithful digital copy of the PDF content could be generated. 
                                When this bit is clear (and bit 3 is set), printing is limited to a 
                                low level representation of the appearance, possibly of degraded quality. 
                                (See implementation note 16 in Appendix H.)
13-32	                        (Revision 3 only) Reserved; must be 1.

Source: http://www.verypdf.com/encryptpdf/permissions.htm
'''

__BIT_POSITION_PRINT = 3
__BIT_POSITION_MODIFY = 4
__BIT_POSITION_COPY = 5
__BIT_POSITION_ANNOTATIONS = 6
__BIT_POSITION_FILL_FIELDS = 9
__BIT_POSITION_EXTRACT = 10
__BIT_POSITION_ASSEMBLE = 11
__BIT_POSITION_PRINT_HQ = 12

def __get_bit_value_as_int(bit):
    '''
        Returns the in value of a bit
    '''
    return 2 ** (bit - 1)

PERM_NONE = 0
PERM_PRINT = __get_bit_value_as_int(__BIT_POSITION_PRINT) | __get_bit_value_as_int(__BIT_POSITION_PRINT_HQ)
PERM_MODIFY = __get_bit_value_as_int(__BIT_POSITION_MODIFY)
PERM_MODIFY_TEXT = __get_bit_value_as_int(__BIT_POSITION_ANNOTATIONS)
PERM_FILL_FIELDS = __get_bit_value_as_int(__BIT_POSITION_FILL_FIELDS)
PERM_ASSEMBLE = __get_bit_value_as_int(__BIT_POSITION_ASSEMBLE)
PERM_COPY = __get_bit_value_as_int(__BIT_POSITION_COPY) | __get_bit_value_as_int(__BIT_POSITION_EXTRACT)
PERM_ALL = PERM_PRINT | PERM_MODIFY | PERM_MODIFY_TEXT | PERM_FILL_FIELDS | PERM_ASSEMBLE | PERM_COPY

def __twos_complement(val):
    bits = 32
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def get_perm_value_as_int(perms):
    '''
        Returns the twos complement representation of the permission
    '''
    # Mask is 11111111111111111111000011000000
    # Bits 13-32 are 1 and bits 7-8 are 1
    mask = 0xFFFFF0C0
    perms = perms | mask
    return __twos_complement(perms)
