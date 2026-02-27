# Security

We strive to provide a library with secure defaults.

## Configuration

### Filters

*pypdf* currently employs output size limits for some filters which are known to possibly have large compression ratios.

The usual limit is at 75 MB of uncompressed data during decompression. If this is too low for your use case, and you are
aware of the possible side effects, you can modify the following constants which define the desired maximal output size in bytes:

* `pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH` for the *FlateDecode* filter (zlib compression)
* `pypdf.filters.LZW_MAX_OUTPUT_LENGTH` for the *LZWDecode* filter (LZW compression)
* `pypdf.filters.RUN_LENGTH_MAX_OUTPUT_LENGTH` for the *RunLengthDecode* filter (run-length compression)

For JBIG2 images, there is a similar parameter to limit the memory usage during decoding: `pypdf.filters.JBIG2_MAX_OUTPUT_LENGTH`
It defaults to 75 MB as well.

For the *FlateDecode* filter, the number of bytes to attempt recovery with can be set by `pypdf.filters.ZLIB_MAX_RECOVERY_INPUT_LENGTH`.
It defaults to 5 MB due to the much more complex recovery approach.

### Reading

*pypdf* currently employs the following reading limits on *PdfReader* instances:

* `root_object_recovery_limit` limits the number of objects to read before stopping with Root object recovery in
  non-strict mode. It defaults to 10 000. Setting it to `None` will fully disable this limit.

If you want to employ custom limits for the *PdfWriter* as well, the currently preferred way
is to initialize it from the reader, id est something like
`PdfWriter(clone_from=PdfReader("file.pdf", root_object_recovery_limit=42))`.

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
