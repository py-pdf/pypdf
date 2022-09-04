# Migration Guide: 1.x to 2.x

`PyPDF2<2.0.0` ([docs](https://pypdf2.readthedocs.io/en/1.27.12/meta/history.html))
is very different from `PyPDF2>=2.0.0` ([docs](https://pypdf2.readthedocs.io/en/latest/meta/history.html)).

Luckily, most changes are simple naming adjustments. This guide helps you to
make the step from `PyPDF2 1.x` (or even the original PyPpdf) to `PyPDF2>=2.0.0`.

You can execute your code with the updated version and show deprecation warnings
by running `python -W all your_code.py`.

# Imports and Modules

* `PyPDF2.utils` no longer exists
* `PyPDF2.pdf` no longer exists. You can import from `PyPDF2` directly or from
  `PyPDF2.generic`

# Naming Adjustments

## Classes

The base classes were renamed as they also allow to operate with ByteIO streams
instead of files. Also, the `strict` paramter changed the default value from
`strict=True` to `strict=False`.

* `PdfFileReader` ➔ `PdfReader`
* `PdfFileWriter` ➔ `PdfWriter`
* `PdfFileMerger` ➔ `PdfMerger`

PdfFileReader and PdfFileMerger no longer have the `overwriteWarnings`
parameter. The new behavior is `overwriteWarnings=False`.

## Function, Method, and Property Names

In `PyPDF2.xmp.XmpInformation`:

* `rdfRoot` ➔ `rdf_root`
* `xmp_createDate` ➔ `xmp_create_date`
* `xmp_creatorTool` ➔ `xmp_creator_tool`
* `xmp_metadataDate` ➔ `xmp_metadata_date`
* `xmp_modifyDate` ➔ `xmp_modify_date`
* `xmpMetadata` ➔ `xmp_metadata`
* `xmpmm_documentId` ➔ `xmpmm_document_id`
* `xmpmm_instanceId` ➔ `xmpmm_instance_id`

In `PyPDF2.generic`:

* `readHexStringFromStream` ➔ `read_hex_string_from_stream`
* `initializeFromDictionary` ➔ `initialize_from_dictionary`
* `createStringObject` ➔ `create_string_object`
* `TreeObject.hasChildren` ➔ `TreeObject.has_children`
* `TreeObject.emptyTree` ➔ `TreeObject.empty_tree`

## Parameter Names

* `PdfWriter.get_page`: `pageNumber` ➔ `page_number`
* `PyPDF2.filters` (all classes): `decodeParms` ➔ `decode_parms`
* `PyPDF2.filters` (all classes): `decodeStreamData` ➔ `decode_stream_data`

## Deprecations

A few classes / functions were deprecated without replacement:

* `PyPDF2.utils.ConvertFunctionsToVirtualList`
* `PyPDF2.utils.formatWarning`
* `PyPDF2.isInt(obj)`: Use `instance(obj, int)` instead
* `PyPDF2.u_(s)`: Use `s` directly
* `PyPDF2.chr_(c)`: Use `chr(c)` instead
* `PyPDF2.barray(b)`: Use `bytearray(b)` instead
* `PyPDF2.isBytes(b)`: Use `instance(b, type(bytes()))` instead
* `PyPDF2.xrange_fn`: Use `range` instead
* `PyPDF2.string_type`: Use `str` instead
* `PyPDF2.isString(s)`: Use `instance(s, str)` instead
* `PyPDF2._basestring`: Use `str` instead
* `b_(...)` was removed. You should typically be able use the bytes object directly, otherwise you can [copy this](https://github.com/py-pdf/PyPDF2/pull/986#issuecomment-1230698069)
