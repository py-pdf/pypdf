# Security

We strive to provide a library with secure defaults.

## Configuration

### Filters

*pypdf* currently employs output size limits for some filters which are known to possibly have large compression ratios
and other related issues.

The usual limit is at 75 MB of uncompressed data during decompression. If this is too low for your use case, and you are
aware of the possible side effects, you can modify the following constants:

* `pypdf.filters.JBIG2_MAX_OUTPUT_LENGTH` for the *JBIG2Decode* filter (JBIG2 images)
* `pypdf.filters.LZW_MAX_OUTPUT_LENGTH` for the maximum output length of the *LZWDecode* filter (LZW compression)
* `pypdf.filters.RUN_LENGTH_MAX_OUTPUT_LENGTH` for the maximum output length of the *RunLengthDecode* filter (run-length compression)
* `pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH` for the maximum output length of the *FlateDecode* filter (zlib compression)
* `pypdf.filters.ZLIB_MAX_RECOVERY_INPUT_LENGTH` for the number of bytes to attempt the recovery with for the *FlateDecode* filter.
  It defaults to 5 MB due to the much more complex recovery approach.

The following general stream length limits apply, defaulting to 75 MB as well:

* `pypdf.filters.MAX_DECLARED_STREAM_LENGTH` for the `/Length` field of streams.
* `pypdf.filters.MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH` for the maximum allowed output length of array-based streams.

For the *JBIG2Decode* filter, calling the external *jbig2dec* tool can be disabled by setting `pypdf.filters.JBIG2DEC_BINARY = None`.

For the *FlateDecode* filter, the following additional limits apply:

* `pypdf.filters.FLATE_MAX_BUFFER_SIZE` for the maximum buffer size to allocate for images, defaulting to 75 MB
* `pypdf.filters.FLATE_MAX_COLUMNS` for the maximum number of columns, defaulting to 250 000
* `pypdf.filters.FLATE_MAX_ROW_LENGTH` for the maximum row length, defaulting to 4 MB

### Reading

*pypdf* currently employs the following reading limits on *PdfReader* instances:

* `root_object_recovery_limit` limits the number of objects to read before stopping with Root object recovery in
  non-strict mode. It defaults to 10 000. Setting it to `None` will fully disable this limit.

If you want to employ custom limits for the *PdfWriter* as well, the currently preferred way
is to initialize it from the reader, id est something like
`PdfWriter(clone_from=PdfReader("file.pdf", root_object_recovery_limit=42))`.

For *PdfWriter* instances, the following limits are employed for incremental reading:

* `incremental_clone_object_count_limit` limits the number of objects to read during cloning. It defaults to
  500 000. Setting it to `None` will fully disable this limit.
* `incremental_clone_object_id_limit` limits the maximum object ID to read during cloning. It defaults to
  1 000 000. Setting it to `None` will fully disable this limit.

## Reporting possible vulnerabilities

Please refer to our [security policy](https://github.com/py-pdf/pypdf/security/policy).

## Invalid reports

### Exceptions

Most exceptions raised by our code are considered bugs or robustness issues and can be reported publicly.
We consider it the task of the library user to catch exceptions which could cause their service to crash, although we try to
only raise a known set of exception types.

### Cryptographic functions

We receive reports about possibly insecure cryptography from time to time. This includes the following aspects:

* Using the ARC4 cipher
* Using the AES cipher in ECB mode
* Using MD5 for hashing

These are requirements of the PDF standard, which we need to achieve the greatest compatibility with.
Although some of them might be deprecated in PDF 2.0, the PDF 2.0 adoption rate is very low and legacy documents need to be supported.

### XML parsing

We use `xml.minidom` for parsing XMP information. Given recent Python versions built against recent Expat versions, the usual attacks
(exponential entity expansion and external entity expansion) should not be possible. We have corresponding tests in place to ensure
this for the platforms our tests run against.

For some details, see [the official documentation](https://docs.python.org/3/library/xml.html#xml-security) and the
[README for defusedxml](https://github.com/tiran/defusedxml/blob/main/README.md#python-xml-libraries).

Please note that automated scanners tend to still flag any direct imports of XML modules from the Python standard library as unsafe.
There have been discussions about this being outdated already, but they are still being flagged.
