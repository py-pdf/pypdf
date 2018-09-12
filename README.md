# PyPDF4
PyPDF4 is a pure-python PDF library capable of splitting, merging together,
cropping, and transforming the pages of PDF files. It can also add custom data,
viewing options, and passwords to PDF files.  It can retrieve text and metadata
from PDFs as well as merge entire files together.

What happened to PyPDF2?  Nothing; it's still available at
https://github.com/mstamy2/PyPDF2.  For various reasons @claird will eventually
explain, I've simply decided to mark a new "business model" with a
slightly-renamed project name.
While PyPDF4 will continue to be available at no charge, I have strong plans
for better ongoing support to start in August 2018.

Homepage (available soon): http://claird.github.io/PyPDF4/.

## Examples
Please see the `samplecode` folder.

## Documentation
Documentation soon will be available, although probably not at
https://pythonhosted.org/PyPDF4/.

## FAQ
Please see http://claird.github.io/PyPDF4/FAQ.html (available in early August).

## Tests
PyPDF4 includes a modest (but growing!) test suite built on the unittest
framework. All tests are located in the `tests/` folder and are distributed
among dedicated modules. Tests can be run from the command line by:

```
python2 -m unittest discover --start-directory tests/
python3 -m unittest discover --start-directory tests/
```

## Contributing
The contribution guide lines specify a list of common rules and conventions
that volunteers and contributors alike are expected to maintain. An exhaustive
list will be soon compiled, or may never be so, but for now you should:

* Develop for Python 3 and maintain backwards-compatibility for 2.7.
* Follow the [PEP 8](http://filltherealaddress.com) style conventions, such as:
    * Never go beyond line lengths of 79 characters.
    * Maintain correct spacing between global-scoped classes (two spaces in
	between etc.).
* Provide [docstring documentation](https://www.python.org/dev/peps/pep-0257/)
for public classes and functions. 
* **Provide test cases** for individual units of development of your own.
Proper testing is highly encouraged: *Code without tests is broken by design*
\- Jacob Kaplan-Moss, Django's original development team member. [Learn how to
apply unit testing](https://docs.python.org/3/library/unittest.html) to your
code.
* Utilize `# TO-DO` or `TO-DO` markings within
[docstrings](https://www.python.org/dev/peps/pep-0257/) for indicating a
feature that is yet to be implemented or discussed. Some IDEs feature TO-DOs
detection consoles.
