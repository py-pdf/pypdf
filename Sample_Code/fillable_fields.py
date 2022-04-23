"""
Sample code that copies a PDF, changing field values along the way (i.e. using a PDF with fillable fields as a template).
"""
import sys
from PyPDF2 import PdfFileWriter, PdfFileReader

root_folder = "Sample_Code/"
template_name = "fillable_form.pdf"


def discover_fields(template_pdf, just_text=True):
    if just_text:
        available_fields = template_pdf.getFormTextFields()
    else:
        available_fields = template_pdf.getFields()
    if available_fields:
        for fieldname in available_fields:
            print(fieldname)
    else:
        print("ERROR: '" + template_name + "' has no text fields.")
        sys.exit(1)

def fill_in_pdf(template_pdf, field_values, filename):
    output = PdfFileWriter()
    output.have_viewer_render_fields()
    for page_no in range(template_pdf.getNumPages()):
        template_page = template_pdf.getPage(0)
        output.addPage(template_page)
        page = output.getPage(page_no)
        output.updatePageFormFieldValues(page, field_values, read_only=True)
    output_stream = open(filename, "wb")
    output.write(output_stream)
    output_stream.close()

template_pdf = PdfFileReader(open(root_folder + template_name, "rb"), strict=False)

employee_john = {
    "employee_name": "John Hardworker",
    "employee_id": "0123",
    "department": "Human Resources",
    "manager_name": "Doris Stickler",
    "manager_id": "0072"
}
employee_cyndi = {
    "employee_name": "Cyndi Smartworker",
    "employee_id": "0199",
    "department": "Engineering",
    "manager_name": "Steven Wright",
    "manager_id": "0051"
}


discover_fields(template_pdf)

fill_in_pdf(template_pdf, employee_john, root_folder + "JohnHardworder.pdf")

# fill_in_pdf(template_pdf, employee_cyndi, root_folder + "CyndiSmartworker.pdf")
# FIXME: If you uncomment this second call, you get:
#   File "C:\forks\PyPDF2\PyPDF2\pdf.py", line 594, in _sweepIndirectReferences
#   if data.pdf.stream.closed:
#   AttributeError: 'PdfFileWriter' object has no attribute 'stream'


