#!/usr/bin/env vpython3
import os
import time
import hashlib
import random
import struct
from pypdf import PdfWriter, PageObject
from pypdf._page import PageObject
from pypdf.generic import (
    ArrayObject,
    ByteStringObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NumberObject,
    StreamObject
)

class PdfWriterIncremental(PdfWriter):
    def __init__(self, reader):
        super().__init__()

        xsize = reader.trailer["/Size"]
        self._objects = []
        while len(self._objects) < xsize - 1:
            self._objects.append(None)

        self.x_reader = reader
        self.x_info = self.x_reader.trailer.get("/Info")
        x_prev_root = self.x_reader.trailer.raw_get("/Root")
        self._root_object = x_prev_root.get_object()
        self.x_root = IndirectObject(x_prev_root.idnum, 0, self)
        self.x_prev_root = x_prev_root.copy()

        where = self.x_reader.stream.tell()
        self.x_reader.stream.seek(0, os.SEEK_END)
        self.x_startdata = self.x_reader.stream.tell()
        self.x_reader.stream.seek(where, os.SEEK_SET)

    def get_page(self, page_number: int) -> PageObject:
        indpage = self.x_reader._get_page(page_number).indirect_reference
        page = self._objects[indpage.idnum - 1]
        if page is None:
            page = PageObject(self, IndirectObject(indpage.idnum, 0, self))
            page.update(indpage.get_object())
            self._objects[indpage.idnum - 1] = page
        return page

    def write(self, stream):
        if self._root_object != self.x_prev_root:
            self._objects[self._root_object.indirect_reference.idnum - 1] = self._root_object
        stream.write(b"\n")
        positions = {}
        for i in range(len(self._objects)):
            idnum = i + 1
            obj = self._objects[i]
            if obj is None:
                positions[idnum] = 0
                continue
            #print(i, idnum, obj)
            positions[idnum] = self.x_startdata + stream.tell()
            stream.write(f"{idnum} 0 obj\n".encode())
            obj.write_to_stream(stream, None)
            stream.write(b"\nendobj\n")

        ID = self.x_reader.trailer.get("/ID", None)
        if ID is None:
            ID = hashlib.md5(repr(time.time()).encode()).digest()
        else:
            ID = ID.get_object()[0].original_bytes
        newID = repr(random.random())
        self._ID = ArrayObject(
            [
                ByteStringObject(ID),
                ByteStringObject(hashlib.md5(newID.encode()).digest()),
            ]
        )

        xref_location = self.x_startdata + stream.tell()
        trailer = DictionaryObject()
        #reader.startxref = 0
        #reader.xrefstream = False
        # xref table
        trailer.update(
            {
                NameObject("/Size"): NumberObject(len(self._objects) + 1),
                NameObject("/Root"): self.x_root,
                NameObject("/Prev"): NumberObject(self.x_reader.startxref),
                NameObject("/ID"): self._ID,
            }
        )

        if self.x_info:
            trailer[NameObject("/Info")] = self.x_info

        #print('xas xref?', reader.xrefstream)
        if not self.x_reader.xrefstream:
            stream.write(b"xref\n")
            positions[0] = 1
            keys = sorted(positions.keys())
            i = 0
            while i < len(keys):
                start = i
                while i < len(keys) and positions[keys[i]] != 0:
                    i += 1
                stream.write(b"%d %d \n" % (keys[start], i - start))
                i = start
                while i < len(keys) and positions[keys[i]] != 0:
                    if i == 0:
                        stream.write(b"0000000000 65535 f \n")
                    else:
                        stream.write(
                            b"%010d %05d n \n" % (positions[keys[i]], 0)
                        )
                    i += 1
                while i < len(keys) and positions[keys[i]] == 0:
                    i += 1

            # trailer
            stream.write(b"trailer\n")
            trailer.write_to_stream(stream, None)
        else:

            def pack(offset):
                return struct.pack(">q", offset)

            dataindex = [NumberObject(0), NumberObject(1)]
            dataxref = [b"\x00" + pack(0)]
            keys = sorted(positions.keys())
            i = 0
            while i < len(keys):
                off = positions[keys[i]]
                if off != 0:
                    start = i
                    while i < len(keys) and positions[keys[i]] != 0:
                        dataxref.append(b"\x01" + pack(positions[keys[i]]))
                        i += 1
                    dataindex.extend([NumberObject(keys[start]), NumberObject(i - start)])
                else:
                    i += 1

            dataindex = [NumberObject(0), NumberObject(len(self._objects))]
            dataxref = b"".join(dataxref)
            trailer[NameObject("/Size")] = NumberObject(len(self._objects) + 2)
            trailer[NameObject("/Type")] = NameObject("/XRef")
            trailer[NameObject("/W")] = ArrayObject([
                NameObject(1),
                NameObject(8),
                NameObject(0)
            ])
            trailer[NameObject("/Index")] = ArrayObject(dataindex)

            trailer[NameObject("/Length")] = NumberObject(len(dataxref))
            trailer[NameObject("__streamdata__")] = ByteStringObject(dataxref)
            trailer = StreamObject.initialize_from_dictionary(trailer)
            retval = trailer.flate_encode()
            trailer.update(retval)
            trailer._data = retval._data
            stream.write(b"%d 0 obj\n" % (len(self._objects)+1))
            trailer.write_to_stream(stream, None)
            stream.write(b"\nendobj")

        # eof
        stream.write(b"\nstartxref\n%d" % xref_location)
        stream.write(b"\n%%%%EOF\n")
