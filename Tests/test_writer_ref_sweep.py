"""
Unit tests for _sweepIndirectReference() of the PdfFileWriter object.
"""

import collections
import io
import unittest
import PyPDF2


class SweepLogger(PyPDF2.PdfFileWriter):
    """Subclass adding test instrumentation to sweep method calls."""
    def __init__(self):
        super(SweepLogger, self).__init__()
        self.depth = 0
        self.max_depth = 0
        self.visited_items = []
        self.sweepQ = collections.deque()

    def _sweepIndirectReferences(self, externMap, data, iterItems=False):
        """
        Wrapper of the original method call, recording recursion depth
        and which data items have been swept.
        """
        self.depth += 1
        if self.depth > self.max_depth:
            self.max_depth = self.depth
        self.visited_items.append(data)

        ret = super(SweepLogger, self)._sweepIndirectReferences(externMap,
                                                                data, iterItems)

        self.depth -= 1
        return ret


class WriterFixture(object):
    """Superclass creating a dummy writer object."""
    def setUp(self):
        self.writer = SweepLogger()
        self.buffer = io.BytesIO()


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
        self.writer._sweepIndirectReferences({}, ar, True)
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
        self.writer._sweepIndirectReferences({}, obj, True)
        for key in d:
            self.assertIs(d[key], obj[key])
        self.assertEqual(d, obj)


class StreamInContainerReplacement(WriterFixture, unittest.TestCase):
    """Ensure streams in containers are replaced with indirect objects."""
    def test_array(self):
        """Confirm a stream in an array is replaced with an indirect object."""
        stream = PyPDF2.generic.StreamObject()
        ar = PyPDF2.generic.ArrayObject([stream])
        self.writer._sweepIndirectReferences({}, ar, True)
        self.assert_replacement(stream, ar[0])

    def test_dictionary(self):
        """Confirm a stream in a dictionary is replaced with an indirect object."""
        stream = PyPDF2.generic.StreamObject()
        key = PyPDF2.generic.NameObject('/foo')
        d = PyPDF2.generic.DictionaryObject({key:stream})
        self.writer._sweepIndirectReferences({}, d, True)
        repl = d.raw_get(key) # Bypass indirect object resolution.
        self.assert_replacement(stream, repl)

    def assert_replacement(self, orig, repl):
        """
        Verifies the original object was added to the PDF's object list,
        and the replacement is indeed an indirect object.
        """
        self.assertIs(orig, self.writer._objects[-1])
        self.assertIsInstance(repl, PyPDF2.generic.IndirectObject)


class InternalIndirectObjects(WriterFixture, unittest.TestCase):
    """Tests for indirect objects originating within the output document."""
    def test_visit_target(self):
        """Confirm the target of an indirect object is swept."""
        target = PyPDF2.generic.NullObject()
        ido = self.writer._addObject(target)
        self.writer._root_object[PyPDF2.generic.NameObject('/foo')] = ido
        self.writer.write(self.buffer)
        self.assertIn(target, self.writer.visited_items)

    def test_visit_target_once(self):
        """Confirm the target of an indirect object is swept only once."""
        target = PyPDF2.generic.NullObject()
        ido = self.writer._addObject(target)
        self.writer._root_object[PyPDF2.generic.NameObject('/first')] = ido
        self.writer._root_object[PyPDF2.generic.NameObject('/second')] = ido
        self.writer.write(self.buffer)
        hits = [obj for obj in self.writer.visited_items if obj is target]
        self.assertEqual(len(hits), 1)


class ExternalIndirectObjects(WriterFixture, unittest.TestCase):
    """Tests for sweeping indirect objects from a separate document."""
    def test_replacement(self):
        """Ensure a new indirect object is created to replace an external one."""
        ext_ido = self._create_external_indirect_objects()[0]
        new_ido = self.writer._sweepIndirectReferences({}, ext_ido)
        self.assertIsInstance(new_ido, PyPDF2.generic.IndirectObject)
        self.assertIs(new_ido.pdf, self.writer)

    def test_target_inclusion(self):
        """Ensure the target of the replacement indirect object is correctly added to the internal object list."""
        ext_ido = self._create_external_indirect_objects()[0]
        new_ido = self.writer._sweepIndirectReferences({}, ext_ido)
        new_obj = new_ido.getObject()
        self.assertIs(self.writer._objects[new_ido.idnum - 1], new_obj)

    def test_target_swept(self):
        """Ensure the target of the replacement indirect object is swept."""
        ext_ido = self._create_external_indirect_objects()[0]
        target = ext_ido.getObject()
        key = PyPDF2.generic.NameObject('/foo')
        self.writer._root_object[key] = ext_ido
        self.writer.write(self.buffer)
        self.assertIn(target, self.writer.visited_items)

    def test_single_inclusion(self):
        """Ensure a direct object targeted by multiple indirect objects is added to the internal object list once."""
        num = 3
        ext_idos = self._create_external_indirect_objects(num)
        target = ext_idos[0].getObject()

        # Add the indirect entries to the root dictionary.
        keys = [PyPDF2.generic.NameObject("/ido{0}".format(x))
                for x in range(num)]
        pairs = [(keys[x], ext_idos[x]) for x in range(num)]
        self.writer._root_object.update(pairs)

        self.writer.write(self.buffer)
        hits = [obj for obj in self.writer._objects if obj is target]
        self.assertEqual(len(hits), 1)

    def _create_external_indirect_objects(self, num=1):
        """Generates indirect objects originating from a separate PDF.

        To simulate objects from a different document a dummy PDF is
        created with mock indirect objects inserted into its root dictionary.
        The document is written to a buffer then read back into a
        PdfFileReader instance. The original indirect objects from the
        reader's root dictionary are then returned to the caller, which
        can now be treated as if they are external.
        """
        keys = [PyPDF2.generic.NameObject("/ido{0}".format(x))
                for x in range(num)]

        # Generate the dummy document with a direct object and a single
        # indirect object pointing to it.
        doc = PyPDF2.PdfFileWriter()
        obj = PyPDF2.generic.NullObject()
        ido = doc._addObject(obj)

        # Create the requested number of entries in the root dictionary.
        pairs = [(k, ido) for k in keys]
        doc._root_object.update(pairs)

        # Dump the dummy document out to a buffer and bring it back into
        # a PdfFileReader.
        buf = io.BytesIO()
        doc.write(buf)
        reader = PyPDF2.PdfFileReader(buf)

        root = reader.trailer[PyPDF2.generic.NameObject('/Root')]
        return [root.raw_get(k) for k in keys]


class Recursion(WriterFixture, unittest.TestCase):
    """Tests for recursive calls into nested data structures."""
    def test_depth_limit(self):
        """Ensure recursion depth is limited when sweeping nested data.

        Recursion should never exceed 3 per the following series of data items:
        1. Top-level call with a container(array/dictionary) as the data.
        2. Indirect object within in the top-level container.
        3. Indirect object target.
        """
        self._make_nested_data()
        self.writer.write(self.buffer)
        self.assertEqual(self.writer.max_depth, 3)

    def test_visit(self):
        """Ensure all items within nested data structures are swept."""
        self._make_nested_data()
        self.writer.write(self.buffer)

        visited = set()
        for o in self.writer.visited_items:
            try:
                visited.add(o)
            except TypeError:
                pass
        self.assertTrue(self.nested_objects.issubset(visited))

    def _make_nested_data(self):
        """
        Creates a dummy nested data structure under the root dictionary.
        Each level consists of a dictionary with an object key associated with
        a direct object, and a nest key storing the next nested dictionary.
        """
        # This set stores the direct objects from the nested dictionaries
        # at all levels.
        self.nested_objects = set()

        self.obj_key = PyPDF2.generic.NameObject('/obj')
        self.nest_key = PyPDF2.generic.NameObject('/nest')

        # Create a top-level container in the root dictionary.
        d = PyPDF2.generic.DictionaryObject()
        self.writer._root_object[self.nest_key] = d

        # Add a nested set of dictionaries under the top-level item.
        for _i in range(10):
            obj = PyPDF2.generic.NullObject()
            d[self.obj_key] = obj
            self.nested_objects.add(obj)

            nest = PyPDF2.generic.DictionaryObject()
            d[self.nest_key] = nest
            d = nest
