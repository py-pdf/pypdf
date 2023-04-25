# Installation

There are several ways to install pypdf. The most common option is to use pip.

## pip

pypdf requires Python 3.6+ to run.

Typically Python comes with `pip`, a package installer. Using it you can
install pypdf:

```bash
pip install pypdf
```

If you are not a super-user (a system administrator / root), you can also just
install pypdf for your current user:

```bash
pip install --user pypdf
```

### Optional dependencies

pypdf tries to be as self-contained as possible, but for some tasks the amount
of work to properly maintain the code would be too high. This is especially the
case for cryptography and image formats.

If you simply want to install all optional dependencies, run:

```
pip install pypdf[full]
```

Alternatively, you can install just some:

If you plan to use pypdf for encrypting or decrypting PDFs that use AES, you
will need to install some extra dependencies. Encryption using RC4 is supported
using the regular installation.

```
pip install pypdf[crypto]
```

If you plan to use image extraction, you need Pillow:

```
pip install pypdf[image]
```

## Python Version Support

| Python                 | 3.11 | 3.10 | 3.9 | 3.8 | 3.7 | 3.6 | 2.7 |
| ---------------------- | ---- | ---- | --- | --- | --- | --- | --- |
| pypdf>=3.0             | YES  | YES  | YES | YES | YES | YES |     |
| PyPDF2>=2.0            | YES  | YES  | YES | YES | YES | YES |     |
| PyPDF2 1.20.0 - 1.28.4 |      | YES  | YES | YES | YES | YES | YES |
| PyPDF2 1.15.0 - 1.20.0 |      |      |     |     |     |     | YES |


## Anaconda

Anaconda users can [install pypdf via conda-forge](https://anaconda.org/conda-forge/pypdf).


## Development Version

In case you want to use the current version under development:

```bash
pip install git+https://github.com/py-pdf/pypdf.git
```
