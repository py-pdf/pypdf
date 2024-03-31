# Installation

There are several ways to install PyPDF2. The most common option is to use pip.

## pip

PyPDF2 requires Python 3.6+ to run.

Typically Python comes with `pip`, a package installer. Using it you can
install PyPDF2:

```bash
pip install PyPDF2
```

If you are not a super-user (a system administrator / root), you can also just
install PyPDF2 for your current user:

```bash
pip install --user PyPDF2
```

### Optional dependencies

PyPDF2 tries to be as self-contained as possible, but for some tasks the amount
of work to properly maintain the code would be too high. This is especially the
case for cryptography and image formats.

If you simply want to install all optional dependencies, run:

```
pip install PyPDF2[full]
```

Alternatively, you can install just some:

If you plan to use PyPDF2 for encrypting or decrypting PDFs that use AES, you
will need to install some extra dependencies. Encryption using RC4 is supported
using the regular installation.

```
pip install PyPDF2[crypto]
```

If you plan to use image extraction, you need Pillow:

```
pip install PyPDF2[image]
```

## Python Version Support

| Python                 | 3.10 | 3.9 | 3.8 | 3.7 | 3.6 | 2.7 |
| ---------------------- | ---- | --- | --- | --- | --- | --- |
| PyPDF2>=2.0            | YES  | YES | YES | YES | YES |     |
| PyPDF2 1.20.0 - 1.28.4 | YES  | YES | YES | YES | YES | YES |
| PyPDF2 1.15.0 - 1.20.0 |      |     |     |     |     | YES |


## Anaconda

Anaconda users can [install PyPDF2 via conda-forge](https://anaconda.org/conda-forge/pypdf2).


## Development Version

In case you want to use the current version under development:

```bash
pip install git+https://github.com/py-pdf/PyPDF2.git
```
