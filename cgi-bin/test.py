import cgi, cgitb

print "Content-type: text/html"
print
print "<title>PyPDF2 testing</title>"

form = cgi.FieldStorage()
val = form["files"].value
if val.file:
    print "<p>%s is a file</p>" % val
else:
    print "<p>%s</p>" % val
