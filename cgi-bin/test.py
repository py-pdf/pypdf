"""
import cgi, cgitb

print "Content-type: text/html \n\n"

form = cgi.FieldStorage()
val = form.getvalue('files')
if val.file:
    print "<p>%s is a file</p>" % val
"""