q_and_as = [('license', 'How is PyPDF2 licensed?',
            """<p>Short answer:  BSD-style.  Do with PyPDF2 as you like, and 
   don't bring others down.

<p>Longer version:  ..."""),
           ('why', "Why PyPDF2?  Why doesn't everyone everywhere just use libraries coded in Java or C?", """
               ...
           """),
            ('relation-to-PyPdf', "How is PyPDF2 related to PyPdf?", """
[refer to home page]
          """)]


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
