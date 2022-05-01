# Frequently-Asked Questions

## How is PyPDF2 related to pyPdf?

PyPDF2 is a fork from the no-longer-maintained pyPdf approved by the
latter's founder.

## Which Python versions are supported?

As [Matthew] writes, "... the intention is for PyPDF2 to work with
Python 2 as well as Python 3." ([source])

In January 2014, the main branch works with 2.6-2.7 and 3.1-3.3 \[and
maybe 2.5?\]. Notice that 1.19--the latest in PyPI as of this
writing--(mostly) did not work with 3.x.

I often merge \[concatenate\] various PDF instances, and my application
'craters' with certain files produced by {AutoCAD, my departmental
scanner, ...}, even though the original files display OK. What do I do
now? Crucial ideas we want you to know:

-   All of us contend with [this sort of thing]. Vendors often produce
    PDF with questionable syntax, or at least syntax that isn't what
    PyPDF2 expects.
-   We're committed to resolving all these problems, so that your
    applications (and ours) can handle any PDF instances that come their
    way. Write whenever you have a problem a [GitHub issue].
-   In the meantime, while you're waiting on us, you have at least a
    couple of choices: you can debug PyPDF2 yourself; or use Acrobat or
    Preview or a similar consumer-grade PDF tool to 'mollify'
    \[explain\] your PDF instances so you get the results you are after.

  [Matthew]: https://github.com/mstamy2
  [source]: https://github.com/py-pdf/PyPDF2/commit/24b270d876518d15773224b5d0d6c2206db29f64#commitcomment-5038317
  [this sort of thing]: https://github.com/py-pdf/PyPDF2/issues/24
  [GitHub issue]: https://github.com/py-pdf/PyPDF2/issues
