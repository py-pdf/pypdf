q_and_as = [('license', 'How is PyPDF2 licensed?',
            """<p>Short answer:  BSD-style.  Do with PyPDF2 as you like, and 
   don't bring others down.

<p>Longer version:  ..."""),
           ('why', "Why PyPDF2?  Why doesn't everyone everywhere just use libraries coded in Java or C?", """
<p>Why does PyPDF2 interest <i>you</i>?  The same or a similar reason
likely applies to other PyPDF2 users.  
<a href = 'mailto:PyPDF2@phaseit.net'>E-mail us</a> with a few words
about how <i>you</i> use PyPDF2.
           """),
            ('relation-to-pyPdf', "How is PyPDF2 related to pyPdf?", """
<p>As the <a href = 'http://mstamy2.github.io/PyPDF2/index.html#origin'>PyPDF2
   home page</a> explains, PyPDF2 is a fork from the no-longer-maintained pyPdf
   approved by the latter's founder.
          """),
           ('migration-from-pyPdf', """I'm a long-time pyPdf user.
How hard is migration to PyPDF2?""", """
<p>Migration to PyPDF2 from pyPdf should be utterly transparent.
   If <i>anything</i> gets in your way, we want to know.  Your
   Python code needn't change <i>at all</i>, unless you choose
   to program in a customized location for the PyPDF2 module.
   In particular, ...
          """),
            ('more', 'Where do I learn more about PyPDF2?',
              """<p>The <a href = 'index.html'>PyPDF2 home page</a>
            is a good place to look for more information."""),
            ('mailing', 'Is there a mailing list?', """
             """),
            ('now', 'What development is underway now?', """
             """),
            ('versions', 'With what versions of Python does PyPDF2 work?', """
<p>The main branch [provide hyperlink] [what PyPI provides] as of
year-end 2013 works with 2.6-2.7
[and maybe 2.5?].  The 2-3 branch [] seems to do fine with 3.1-3.3 [?].
we're working to consolidate these, of course [although likely (?) at the
expense of 2.5?].
                """),
            ('characteristic-problems', '''
I often merge [concatenate] various PDF instances, and my
application 'craters' with certain files produced by
{AutoCAD, my departmental scanner, ...}, even though the
original files display OK.  What do I do now?
      ''',  """
<p>Crucial ideas we want you to know:  <ul>
    <li><i>All</i> of us contend with 
    <a href = 'https://github.com/mstamy2/PyPDF2/issues/24'>this
    sort of thing</a>.  Vendors often produce PDF with questionable
    syntax, or at least syntax that isn't what PyPDF2 expects.
    <li>We're committed to resolving all these problems, so 
     that your applications (and ours) can handle any PDF 
     instances that come their way.  
     <a href = "mailto:PyPDF2@Phaseit.net">Write us</a> whenever you
     have a problem [describe the not-yet-working on-line
     submission system].
    <li>In the meantime, while you're waiting on us, you have 
        at least a couple of choices:  you can
        <ul>
        <li>debug PyPDF2 yourself; or
        <li>use Acrobat or Preview or a similar 
            consumer-grade PDF tool to 'mollify' [explain] your
            PDF instances so you get the results you
            are after.
        </ul>
    </ul>
              """),
]

"""
ALSO, document that it works with Py2.5 (?) (not 2.4?).

Explain two forks; #plans; link to tutorial.

Promote PyPDF2 at SO

Tweet about PyPDF2 dominance of pdftk.

PyPDF2 line-up.
"""



title = "'Frequently-Asked Questions' for the PyPDF2 project"


print """<!DOCTYPE html>
<html>
<head>
<title>%s</title>
</head>
<body>
<h1>%s</h1>""" % (title, title)

print "<h2>Table of Contents</h2><ul>"

for (id, q, a) in q_and_as:
    print "<li><a href = '#%s'>%s</a></li>" % (id, q)
print "</ul>"

for (id, q, a) in q_and_as:
    print "<h2><a id = '%s'>%s</a></h2>" % (id, q)
    print a

print "</body></html>"
