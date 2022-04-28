# PDF Version Support

PDF comes in the following versions:

* 1993: 1.0
* 1994: 1.1
* 1996: 1.2
* 1999: 1.3
* 2001: 1.4
* 2003: 1.5
* 2004: 1.6
* 2006 - 2012: 1.7, ISO 32000-1:2008
* 2017: 2.0

The general format didn't change, but new features got added. It can be that
PyPDF2 can do the operations you want on PDF 2.0 files without fully supporting
all features of PDF 2.0.

## PDF Feature Support by PyPDF2

| Feature                                 | PDF-Version | PyPDF2 Support |
| --------------------------------------- | ----------- | -------------- |
| Transparent Graphics                    | 1.4         | ?              |
| CMaps                                   | 1.4         | ❌ [#201](https://github.com/py-pdf/PyPDF2/pull/201), [#464](https://github.com/py-pdf/PyPDF2/pull/464), [#805](https://github.com/py-pdf/PyPDF2/pull/805)   |
| Object Streams                          | 1.5         | ?              |
| Cross-reference Streams                 | 1.5         | ?              |
| Optional Content Groups (OCGs) - Layers | 1.5         | ?              |
| Content Stream Compression              | 1.5         | ?              |
| AES Encryption                          | 1.6         | ❌ [#749](https://github.com/py-pdf/PyPDF2/pull/749)  |

See [History of PDF](https://en.wikipedia.org/wiki/History_of_PDF) for more
features.
