# PDF Version Support

PDF comes in the following versions:

* 1993: 1.0
* 1994: 1.1
* 1996: 1.2
* 1999: 1.3
* 2001: 1.4
* 2003: 1.5
* 2004: 1.6
* 2008: 1.7, ISO 32000-1:2008
* 2017: 2.0, ISO 32000-2:2017

The general format didn't change, but new features got added. It can be that
pypdf can do the operations you want on PDF 2.0 files without fully supporting
all features of PDF 2.0.

## PDF Feature Support by pypdf

| Feature                                 | PDF-Version | pypdf Support |
| --------------------------------------- | ----------- | -------------- |
| Transparent Graphics                    | 1.4         | ?              |
| CMaps                                   | 1.4         | ✅             |
| Object Streams                          | 1.5         | ?              |
| Cross-reference Streams                 | 1.5         | ?              |
| Optional Content Groups (OCGs) - Layers | 1.5         | ?              |
| Content Stream Compression              | 1.5         | ?              |
| AES Encryption                          | 1.6         | ✅             |

See [History of PDF](https://en.wikipedia.org/wiki/History_of_PDF) for more
features.

Some PDF features are not supported by pypdf, but other libraries can be used
for them:

* [pyHanko](https://pyhanko.readthedocs.io/en/latest/index.html): Cryptographically sign a PDF ([#302](https://github.com/py-pdf/pypdf/issues/302))
* [camelot-py](https://pypi.org/project/camelot-py/): Table Extraction ([#231](https://github.com/py-pdf/pypdf/issues/231))
