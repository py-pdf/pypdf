# PDF/A Compliance

PDF/A is a specialized, ISO-standardized version of the Portable Document Format
(PDF) specifically designed for the long-term preservation and archiving of
electronic documents. It ensures that files remain accessible, readable, and
true to their original appearance by embedding all necessary fonts, images, and
metadata within the document itself. By adhering to strict guidelines and
minimizing dependencies on external resources or proprietary software, PDF/A
ensures the consistent and reliable reproduction of content, safeguarding it
against future technological changes and obsolescence.

## PDF/A Versions

* **PDF/A-1**: Based on PDF 1.4, PDF/A-1 is the first version of the standard
  and is divided into two levels: PDF/A-1a (Level A, ensuring accessibility) and
  PDF/A-1b (Level B, ensuring visual preservation).
    * **Level B** (Basic): Ensures visual preservation and basic requirements for archiving.
    * **Level A** (Accessible): Everything from level B, but includes additional
      requirements for accessibility, such as tagging, Unicode character
      mapping, and logical structure.
* **PDF/A-2**: Based on PDF 1.7 (ISO 32000-1), PDF/A-2 adds features and
  improvements over PDF/A-1, while maintaining compatibility with PDF/A-1b
  (Level B) documents.
    * **Level B** (Basic): Like PDF/A-1b, but support for PDF 1.7 features such
      as transparency layers.
    * **Level U** (Unicode): Ensures Unicode mapping without the full
      accessibility requirements of PDF/A-1a (Level A).
    * **Level A** (Accessible): Similar to PDF/A-1a
* **PDF/A-3**: Based on PDF 1.7 (ISO 32000-1), PDF/A-3 is similar to PDF/A-2 but
  allows the embedding of non-PDF/A files as attachments, enabling the archiving
  of source or supplementary data alongside the PDF/A document. This is
  interesting for invoices which can add XML files.
* **PDF/A-4**: Based on PDF 2.0 (ISO 32000-2), PDF/A-4 introduces new features
  and improvements for better archiving and accessibility. The previous levels
  are replaced by PDF/A-4f (ensuring visual preservation and allowing attachments)
  and PDF/A-4e (Engineering, allows 3D content).

## PDF/A-1b

In contrast to other PDF documents, PDF/A-1b documents must fulfill those
requirements:

* **MarkInfo Object**: The MarkInfo object is a dictionary object within a PDF/A
  file that provides information about the logical structure and tagging of the
  document. The MarkInfo object indicates whether the document is tagged,
  contains optional content, or has a structure tree that describes the logical
  arrangement of content such as headings, paragraphs, lists, and tables. By
  including the MarkInfo object, PDF/A ensures that electronic documents are
  accessible to users with disabilities, such as those using screen readers or
  other assistive technologies.
* **Embedded fonts**: All fonts used in the document must be embedded to ensure
  consistent text rendering across different devices and systems.
* **Color Spaces**: DeviceRGB is a device-dependent color space that relies on
  the specific characteristics of the output device, which can lead to
  inconsistent color rendering across various devices. To achieve accurate and
  consistent color representation, PDF/A requires the use of device-independent
  color spaces, such as ICC-based color profiles.
* **XMP (Extensible Metadata Platform) metadata**: XMP metadata provides a
  standardized and extensible way to store essential information about a
  document and its properties. XMP metadata is an XML-based format embedded
  directly within a PDF/A file. It contains various types of information, such
  as document title, author, creation and modification dates, keywords, and
  copyright information, as well as PDF/A-specific details like conformance
  level and OutputIntent.

## Validation

[VeraPDF](https://docs.verapdf.org/install/) is the go-to PDF/A validator.

There are several online-validators which allow you to simply upload the document:

* [pdfen.com](https://www.pdfen.com/pdf-a-validator)
* [avepdf.com](https://avepdf.com/pdfa-validation) : Gives an error report
* [pdfa.org](https://pdfa.org/pdfa-online-verification-service/)
* [visual-paradigm.com](https://online.visual-paradigm.com/de/online-pdf-editor/pdfa-validator/) - can convert the PDF to a PDF/A
* [pdf2go.com](https://www.pdf2go.com/validate-pdfa)
* [slub-dresden.de](https://www.slub-dresden.de/veroeffentlichen/dissertationen-habilitationen/elektronische-veroeffentlichung/slub-pdfa-validator) links to relevant parts in the specification.

## pypdf and PDF/A

At the moment, pypdf does not make any guarantees regarding PDF/A.
[Support is very welcome](https://github.com/py-pdf/pypdf/labels/is-pdf%2Fa-compliance).
