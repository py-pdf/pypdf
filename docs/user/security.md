# Security

We strive to provide a library with secure defaults.

## Configuration

*pypdf* currently employs output size limits for some filters which are known to possibly have large compression ratios.

The usual limit is at 75 MB of uncompressed data during decompression. If this is too low for your use case, and you are
aware of the possible side effects, you can modify the following constants which define the desired maximal output size in bytes:

* `pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH` for the *FlateDecode* filter (zlib compression)
* `pypdf.filters.LZW_MAX_OUTPUT_LENGTH` for the *LZWDecode* filter (LZW compression)

## Reporting possible vulnerabilities

Please refer to our [security policy](https://github.com/py-pdf/pypdf/security/policy).

## Invalid reports

We receive reports about possibly insecure cryptography from time to time. This includes the following aspects:

* Using the ARC4 cipher
* Using the AES cipher in ECB mode
* Using MD5 for hashing

These are requirements of the PDF standard, which we need to achieve the greatest compatibility with.
Although some of them might be deprecated in PDF 2.0, the PDF 2.0 adoption rate is very low and legacy documents need to be supported.
