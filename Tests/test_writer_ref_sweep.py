"""
Unit tests for _sweepIndirectReference() of the PdfFileWriter object.
"""

import unittest
import PyPDF2


class SweepLogger(PyPDF2.PdfFileWriter):
    """Subclass adding test instrumentation to sweep method calls."""
    def __init__(self):
        super(SweepLogger, self).__init__()
        self.depth = 0
        self.max_depth = 0
        self.visited_items = []

    def _sweepIndirectReferences(self, externMap, data):
        """
        Wrapper of the original method call, recording recursion depth
        and which data items have been swept.
        """
        self.depth += 1
        if self.depth > self.max_depth:
            self.max_depth = self.depth
        self.visited_items.append(data)

        ret = super(SweepLogger, self)._sweepIndirectReferences(externMap, data)

        self.depth -= 1
        return ret


class WriterFixture(object):
    """Superclass creating a dummy writer object."""
    def setUp(self):
        self.writer = SweepLogger()


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


class ContainerDirectContentEquality(WriterFixture, unittest.TestCase):
    """Tests to confirm direct objects within containers are unmodified."""
    def test_array(self):
        """Confirm direct objects within an array are retained."""
        l = [
            PyPDF2.generic.NullObject(),
            PyPDF2.generic.BooleanObject(True)
            ]
        ar = PyPDF2.generic.ArrayObject(l)
        self.writer._sweepIndirectReferences({}, ar)
        for i in range(len(l)):
            self.assertIs(l[i], ar[i])
        self.assertEqual(l, ar)

    def test_dictionary(self):
        """Confirm direct objects within a dictionary are retained."""
        d = {
            PyPDF2.generic.NameObject('/spam'):PyPDF2.generic.NullObject(),
            PyPDF2.generic.NameObject('/eggs'):PyPDF2.generic.NumberObject('0')
            }
        obj = PyPDF2.generic.DictionaryObject(d)
        self.writer._sweepIndirectReferences({}, obj)
        for key in d:
            self.assertIs(d[key], obj[key])
        self.assertEqual(d, obj)


class StreamInContainerReplacement(WriterFixture, unittest.TestCase):
    """Ensure streams in containers are replaced with indirect objects."""
    def test_array(self):
        """Confirm a stream in an array is replaced with an indirect object."""
        stream = PyPDF2.generic.StreamObject()
        ar = PyPDF2.generic.ArrayObject([stream])
        self.writer._sweepIndirectReferences({}, ar)
        self.assert_replacement(stream, ar[0])

    def test_dictionary(self):
        """Confirm a stream in a dictionary is replaced with an indirect object."""
        stream = PyPDF2.generic.StreamObject()
        key = PyPDF2.generic.NameObject('/foo')
        d = PyPDF2.generic.DictionaryObject({key:stream})
        self.writer._sweepIndirectReferences({}, d)
        repl = d.raw_get(key) # Bypass indirect object resolution.
        self.assert_replacement(stream, repl)

    def assert_replacement(self, orig, repl):
        """
        Verifies the original object was added to the PDF's object list,
        and the replacement is indeed an indirect object.
        """
        self.assertIs(orig, self.writer._objects[-1])
        self.assertIsInstance(repl, PyPDF2.generic.IndirectObject)
