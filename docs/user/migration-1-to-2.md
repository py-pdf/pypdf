# Migration Guide: 1.x to 2.x

`PyPDF2<2.0.0` ([docs](https://pypdf2.readthedocs.io/en/1.27.12/meta/history.html))
is very different from `PyPDF2>=2.0.0` ([docs](../meta/history.md)).

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
instead of files. Also, the `strict` parameter changed the default value from
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

* `readObject` ➔ `read_object`
* `convertToInt` ➔ `convert_to_int`
* `DocumentInformation.getText` ➔ `DocumentInformation._get_text` : This method should typically not be used; please let me know if you need it.
* `readHexStringFromStream` ➔ `read_hex_string_from_stream`
* `initializeFromDictionary` ➔ `initialize_from_dictionary`
* `createStringObject` ➔ `create_string_object`
* `TreeObject.hasChildren` ➔ `TreeObject.has_children`
* `TreeObject.emptyTree` ➔ `TreeObject.empty_tree`

In many places:
  - `getObject` ➔ `get_object`
  - `writeToStream` ➔ `write_to_stream`
  - `readFromStream` ➔ `read_from_stream`


PdfReader class:
  - `reader.getPage(pageNumber)` ➔ `reader.pages[page_number]`
  - `reader.getNumPages()` / `reader.numPages` ➔ `len(reader.pages)`
  - `getDocumentInfo` ➔ `metadata`
  - `flattenedPages` attribute ➔ `flattened_pages`
  - `resolvedObjects` attribute ➔ `resolved_objects`
  - `xrefIndex` attribute ➔ `xref_index`
  - `getNamedDestinations` / `namedDestinations` attribute ➔ `named_destinations`
  - `getPageLayout` / `pageLayout` ➔ `page_layout` attribute
  - `getPageMode` / `pageMode` ➔ `page_mode` attribute
  - `getIsEncrypted` / `isEncrypted` ➔ `is_encrypted` attribute
  - `getOutlines` ➔ `get_outlines`
  - `readObjectHeader` ➔ `read_object_header`
  - `cacheGetIndirectObject` ➔ `cache_get_indirect_object`
  - `cacheIndirectObject` ➔ `cache_indirect_object`
  - `getDestinationPageNumber` ➔ `get_destination_page_number`
  - `readNextEndLine` ➔ `read_next_end_line`
  - `_zeroXref` ➔ `_zero_xref`
  - `_authenticateUserPassword` ➔ `_authenticate_user_password`
  - `_pageId2Num` attribute ➔ `_page_id2num`
  - `_buildDestination` ➔ `_build_destination`
  - `_buildOutline` ➔ `_build_outline`
  - `_getPageNumberByIndirect(indirectRef)` ➔ `_get_page_number_by_indirect(indirect_ref)`
  - `_getObjectFromStream` ➔ `_get_object_from_stream`
  - `_decryptObject` ➔ `_decrypt_object`
  - `_flatten(..., indirectRef)` ➔ `_flatten(..., indirect_ref)`
  - `_buildField` ➔ `_build_field`
  - `_checkKids` ➔ `_check_kids`
  - `_writeField` ➔ `_write_field`
  - `_write_field(..., fieldAttributes)` ➔ `_write_field(..., field_attributes)`
  - `_read_xref_subsections(..., getEntry, ...)` ➔ `_read_xref_subsections(..., get_entry, ...)`

PdfWriter class:
  - `writer.getPage(pageNumber)` ➔ `writer.pages[page_number]`
  - `writer.getNumPages()` ➔ `len(writer.pages)`
  - `addMetadata` ➔ `add_metadata`
  - `addPage` ➔ `add_page`
  - `addBlankPage` ➔ `add_blank_page`
  - `addAttachment(fname, fdata)` ➔ `add_attachment(filename, data)`
  - `insertPage` ➔ `insert_page`
  - `insertBlankPage` ➔ `insert_blank_page`
  - `appendPagesFromReader` ➔ `append_pages_from_reader`
  - `updatePageFormFieldValues` ➔ `update_page_form_field_values`
  - `cloneReaderDocumentRoot` ➔ `clone_reader_document_root`
  - `cloneDocumentFromReader` ➔ `clone_document_from_reader`
  - `getReference` ➔ `get_reference`
  - `getOutlineRoot` ➔ `get_outline_root`
  - `getNamedDestRoot` ➔ `get_named_dest_root`
  - `addBookmarkDestination` ➔ `add_bookmark_destination`
  - `addBookmarkDict` ➔ `add_bookmark_dict`
  - `addBookmark` ➔ `add_bookmark`
  - `addNamedDestinationObject` ➔ `add_named_destination_object`
  - `addNamedDestination` ➔ `add_named_destination`
  - `removeLinks` ➔ `remove_links`
  - `removeImages(ignoreByteStringObject)` ➔ `remove_images(ignore_byte_string_object)`
  - `removeText(ignoreByteStringObject)` ➔ `remove_text(ignore_byte_string_object)`
  - `addURI` ➔ `add_uri`
  - `addLink` ➔ `add_link`
  - `getPage(pageNumber)` ➔ `get_page(page_number)`
  - `getPageLayout / setPageLayout / pageLayout` ➔ `page_layout attribute`
  - `getPageMode / setPageMode / pageMode` ➔ `page_mode attribute`
  - `_addObject` ➔ `_add_object`
  - `_addPage` ➔ `_add_page`
  - `_sweepIndirectReferences` ➔ `_sweep_indirect_references`

PdfMerger class
  - `__init__` parameter: `strict=True` ➔ `strict=False` (the `PdfFileMerger` still has the old default)
  - `addMetadata` ➔ `add_metadata`
  - `addNamedDestination` ➔ `add_named_destination`
  - `setPageLayout` ➔ `set_page_layout`
  - `setPageMode` ➔ `set_page_mode`

Page class:
  - `artBox` / `bleedBox` / `cropBox` / `mediaBox` / `trimBox` ➔ `artbox` / `bleedbox` / `cropbox` / `mediabox` / `trimbox`
    - `getWidth`, `getHeight ` ➔ `width` / `height`
    - `getLowerLeft_x` / `getUpperLeft_x` ➔ `left`
    - `getUpperRight_x` / `getLowerRight_x` ➔ `right`
    - `getLowerLeft_y` / `getLowerRight_y` ➔ `bottom`
    - `getUpperRight_y` / `getUpperLeft_y` ➔ `top`
    - `getLowerLeft` / `setLowerLeft` ➔ `lower_left` property
    - `upperRight` ➔ `upper_right`
  - `mergePage` ➔ `merge_page`
  - `rotateClockwise` / `rotateCounterClockwise` ➔ `rotate_clockwise`
  - `_mergeResources` ➔ `_merge_resources`
  - `_contentStreamRename` ➔ `_content_stream_rename`
  - `_pushPopGS` ➔ `_push_pop_gs`
  - `_addTransformationMatrix` ➔ `_add_transformation_matrix`
  - `_mergePage` ➔ `_merge_page`

XmpInformation class:
  - `getElement(..., aboutUri, ...)` ➔ `get_element(..., about_uri, ...)`
  - `getNodesInNamespace(..., aboutUri, ...)` ➔ `get_nodes_in_namespace(..., aboutUri, ...)`
  - `_getText` ➔ `_get_text`

utils.py:
  - `matrixMultiply` ➔ `matrix_multiply
  - `RC4_encrypt` is moved to the security module

## Parameter Names

* `PdfWriter.get_page`: `pageNumber` ➔ `page_number`
* `PyPDF2.filters` (all classes): `decodeParms` ➔ `decode_parms`
* `PyPDF2.filters` (all classes): `decodeStreamData` ➔ `decode_stream_data`
* `pagenum` ➔ `page_number`
* `PdfMerger.merge`: `position` ➔ `page_number`
* `PdfWriter.add_outline_item_destination`: `dest` ➔ `page_destination`
* `PdfWriter.add_named_destination_object`: `dest` ➔ `page_destination`
* `PdfWriter.encrypt`: `user_pwd` ➔ `user_password`
* `PdfWriter.encrypt`: `owner_pwd` ➔ `owner_password`

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
