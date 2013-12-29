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
            ('more', 'Where do I learn more about PyPDF2?',
              """<p>The <a href = 'index.html'>PyPDF2 home page</a>
            is a good place to look for more information."""),
            ('mailing', 'Is there a mailing list?', """
             """),
            ('now', 'What development is underway now?', """
             """),
            ('versions', 'With what versions of Python does PyPDF2 work?', """
                """),
]


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
