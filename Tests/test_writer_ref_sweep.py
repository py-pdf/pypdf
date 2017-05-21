"""
Unit tests for _sweepIndirectReference() of the PdfFileWriter object.
"""

import unittest
import PyPDF2


class WriterFixture(object):
    """Superclass creating a dummy writer object."""
    def setUp(self):
        self.writer = PyPDF2.PdfFileWriter()


class DirectIdentity(WriterFixture, unittest.TestCase):
    """Tests to confirm original direct objects are returned.

    For all non-indirect types, the returned object should be identical
    as the given data parameter.
    """
    def test_boolean(self):
        """Confirm original boolean objects are returned."""
        obj = PyPDF2.generic.BooleanObject(False)
        self.assert_identity(obj)

    def test_float(self):
        """Confirm original float objects are returned."""
        obj = PyPDF2.generic.FloatObject('42.01')
        self.assert_identity(obj)

    def test_integer(self):
        """Confirm original integer objects are returned."""
        obj = PyPDF2.generic.NumberObject('42')
        self.assert_identity(obj)

    def test_string(self):
        """Confirm original string objects are returned."""
        obj = PyPDF2.generic.createStringObject('spam')
        self.assert_identity(obj)

    def test_name(self):
        """Confirm original name objects are returned."""
        obj = PyPDF2.generic.NameObject('/spam')
        self.assert_identity(obj)

    def test_array(self):
        """Confirm original array objects are returned."""
        obj = PyPDF2.generic.ArrayObject()
        self.assert_identity(obj)

    def test_dictionary(self):
        """Confirm original dictionary objects are returned."""
        obj = PyPDF2.generic.DictionaryObject()
        self.assert_identity(obj)

    def test_stream(self):
        """Confirm original stream objects are returned."""
        obj = PyPDF2.generic.StreamObject()
        self.assert_identity(obj)

    def test_null(self):
        """Confirm original null objects are returned."""
        obj = PyPDF2.generic.NullObject()
        self.assert_identity(obj)

    def assert_identity(self, obj):
        """Asserts the returned object is the same as the original."""
        ret = self.writer._sweepIndirectReferences({}, obj)
        self.assertIs(ret, obj)
