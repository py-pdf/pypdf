"""
Sample code that copies a PDF, changing field values along the way (i.e. using a PDF with fillable fields as a template).
"""
import sys

from PyPDF2 import PdfFileReader, PdfFileWriter


def discover_fields(template_pdf, just_text=True):
    if just_text:
        available_fields = template_pdf.getFormTextFields()
    else:
        available_fields = template_pdf.getFields()
    if available_fields:
        for fieldname in available_fields:
            print(fieldname)
    else:
        print("ERROR: PDF has no text fields.")
        sys.exit(1)


def fill_in_pdf(template_pdf, field_values, filename):
    writer = PdfFileWriter()
    writer.set_need_appearances_writer()
    for page_no in range(template_pdf.getNumPages()):
        template_page = template_pdf.getPage(0)
        writer.addPage(template_page)
        page = writer.getPage(page_no)
        writer.updatePageFormFieldValues(page, field_values, read_only=True)
    with open(filename, "wb") as output_stream:
        writer.write(output_stream)


template_pdf = PdfFileReader("Resources/fillable_form.pdf", strict=False)

employee_john = {
    "employee_name": "John Hardworker",
    "employee_id": "0123",
    "department": "Human Resources",
    "manager_name": "Doris Stickler",
    "manager_id": "0072",
}
employee_cyndi = {
    "employee_name": "Cyndi Smartworker",
    "employee_id": "0199",
    "department": "Engineering",
    "manager_name": "Steven Wright",
    "manager_id": "0051",
}


discover_fields(template_pdf)

fill_in_pdf(template_pdf, employee_john, "JohnHardworder.pdf")
