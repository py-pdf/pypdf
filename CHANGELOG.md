# CHANGELOG

## Version 5.0.0, 2024-09-15

This version drops support for Python 3.7 (not maintained since July 2023), PdfMerger (use PdfWriter instead) and AnnotationBuilder (use annotations instead).


### Deprecations (DEP)
- Remove the deprecated PfdMerger and AnnotationBuilder classes and other deprecations cleanup (#2813)
- Drop Python 3.7 support (#2793)

### New Features (ENH)
- Add capability to remove /Info from PDF (#2820)
- Add incremental capability to PdfWriter (#2811)
- Add UniGB-UTF16 encodings (#2819)
- Accept utf strings for metadata (#2802)
- Report PdfReadError instead of RecursionError (#2800)
- Compress PDF files merging identical objects (#2795)

### Bug Fixes (BUG)
- Fix sheared image (#2801)

### Robustness (ROB)
- Robustify .set_data() (#2821)
- Raise PdfReadError when missing /Root in trailer (#2808)
- Fix extract_text() issues on damaged PDFs (#2760)
- Handle images with empty data when processing an image from bytes (#2786)

### Developer Experience (DEV)
- Fix coverage uploads (#2832)
- Test against Python 3.13 (#2776)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.3.1...5.0.0)

## Version 4.3.1, 2024-07-21

### Bug Fixes (BUG)
- Cope with Matrix entry in field annotations (#2736)

### Robustness (ROB)
- Cope with fields with upside down box/rectangle (#2729)

### Maintenance (MAINT)
- Add deprecate_with_replacement to StreamObject.initializeFromD… (#2728)
- Deal with cryptography>=43 moving ARC4 (#2765)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.3.0...4.3.1)

## Version 4.3.0, 2024-06-23

### New Features (ENH)
- Accept ETen-B5 and UniCNS-UTF16 encodings (#2721)
- Add decode_as_image() to ContentStreams (#2615)
- context manager for PdfReader (#2666)
- Add capability to set font and size in fields (#2636)
- Allow to pass input file without named argument (#2576)

### Bug Fixes (BUG)
- Fix deprecation for Ressources when using old constants (#2705)
- Fix images issue 4 bits encoding and LUT starting with UTF16_BOM (#2675)
- Reading large compressed images takes huge time to process (#2644)
- Highlighted Text Cannot Be Printed (#2604)
- Fix UnboundLocalError on malformed pdf (#2619)

### Robustness (ROB)
- Cope with missing Standard 14 fonts in fields (#2677)
- Improve inline image extraction (#2622)
- Cope with loops in Fields tree (#2656)
- Discard /I in choice fields for compatibility with Acrobat (#2614)
- Cope with some issues in pillow (#2595)
- Cope with some image extraction issues (#2591)

### Documentation (DOC)
- Various improvements on docstrings and examples

### Maintenance (MAINT)
- Deprecate interiour_color with replacement interior_color (#2706)
- Add deprecate_with_replacement to PdfWriter.find_bookmark (#2674)

### Code Style (STY)
- Change Link to be a non-markup annotation (#2714)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.2.0...4.3.0)

## Version 4.2.0, 2024-04-07

### New Features (ENH)
- Allow multiple charsets for NameObject.read_from_stream (#2585)
- Add support for /Kids in page labels (#2562)
- Allow to update fields on many pages (#2571)
- Tolerate PDF with invalid xref pointed objects (#2335)
- Add Enforce from PDF2.0 in viewer_preferences (#2511)
- Add += and -= operators to ArrayObject (#2510)

### Bug Fixes (BUG)
- Fix merge_page sometimes generating unknown operator 'QQ' (#2588)
- Fix fields update where annotations are kids of field (#2570)
- Process CMYK images without a filter correctly (#2557)
- Extract text in layout mode without finding resources (#2555)
- Prevent recursive loop in some PDF files (#2505)

### Robustness (ROB)
- Tolerate "truncated" xref (#2580)
- Replace error by warning for EOD in RunLengthDecode/ASCIIHexDecode (#2334)
- Rebuild xref table if one entry is invalid (#2528)
- Robustify stream extraction (#2526)

### Documentation (DOC)
- Update release process for latest changes (#2564)
- Encryption/decryption: Clone document instead of copying all pages (#2546)
- Minor improvements (#2542)
- Update annotation list (#2534)
- Update references and formatting (#2529)
- Correct threads reference, plus minor changes (#2521)
- Minor readability increases (#2515)
- Simplify PaperSize examples (#2504)
- Minor improvements (#2501)

### Developer Experience (DEV)
- Remove unused dependencies (#2572)
- Remove page labels PR link from message (#2561)
- Fix changelog generator regarding whitespace and handling of "Other" group (#2492)
- Add REL to known PR prefixes (#2554)
- Release using the REL commit instead of git tag (#2500)
- Unify code between PdfReader and PdfWriter (#2497)
- Bump softprops/action-gh-release from 1 to 2 (#2514)

### Maintenance (MAINT)
- Ressources → Resources (and internal name childs) (#2550)
- Fix typos found by codespell (#2549)
- Update Read the Docs configuration (#2538)
- Add root_object, _info and _ID to PdfReader (#2495)

### Testing (TST)
- Allow loading truncated images if required (#2586)
- Fix download issues from #2562 (#2578)
- Improve test_get_contents_from_nullobject to show real use-case (#2524)
- Add missing test annotations (#2507)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.1.0...4.2.0)

## Version 4.1.0, 2024-03-03

Generating name objects (`NameObject`) without a leading slash
is considered deprecated now. Previously, just a plain warning
would be logged, leading to possibly invalid PDF files. According
to our deprecation policy, this will log a *DeprecationWarning*
for now.

### New Features (ENH)
- Add get_pages_from_field  (#2494)
- Add reattach_fields function (#2480)
- Automatic access to pointed object for IndirectObject (#2464)

### Bug Fixes (BUG)
- Missing error on name without leading / (#2387)
- encode_pdfdocencoding() always returns bytes (#2440)
- BI in text content identified as image tag (#2459)

### Robustness (ROB)
- Missing basefont entry in type 3 font (#2469)

### Documentation (DOC)
- Improve lossless compression example (#2488)
- Amend robustness documentation (#2479)

### Developer Experience (DEV)
- Fix changelog for UTF-8 characters (#2462)

### Maintenance (MAINT)
- Add _get_page_number_from_indirect in writer (#2493)
- Remove user assignment for feature requests (#2483)
- Remove reference to old 2.0.0 branch (#2482)

### Testing (TST)
- Fix benchmark failures (#2481)
- Broken test due to expired test file URL (#2468)
- Resolve file naming conflict in test_iss1767 (#2445)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.0.2...4.1.0)

## Version 4.0.2, 2024-02-18

### Bug Fixes (BUG)
-  Use NumberObject for /Border elements of annotations (#2451)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.0.1...4.0.2)

## Version 4.0.1, 2024-01-28

### Bug Fixes (BUG)
-  layout mode text extraction ZeroDivisionError (#2417)

### Testing (TST)
-  Skip tests using fpdf2 if it's not installed (#2419)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/4.0.0...4.0.1)

## Version 4.0.0, 2024-01-19

### Deprecations (DEP)
-  Drop Python 3.6 support (#2369)
-  Remove deprecated code (#2367)
-  Remove deprecated XMP properties (#2386)

### New Features (ENH)
-  Add "layout" mode for text extraction (#2388)
-  Add Jupyter Notebook integration for PdfReader (#2375)
-  Improve/rewrite PDF permission retrieval (#2400)

### Bug Fixes (BUG)
-  PdfWriter.add_uri was setting the wrong type (#2406)
-  Add support for GBK2K cmaps (#2385)

### Maintenance (MAINT)
-  Return None instead of -1 when page is not attached (#2376)
-  Complete FileSpecificationDictionaryEntries constants (#2416)
-  Replace warning with logging.error (#2377)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.17.4...4.0.0)

## Version 3.17.4, 2023-12-24

### Bug Fixes (BUG)
-  Handle IndirectObject as image filter (#2355)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.17.3...3.17.4)

## Version 3.17.3, 2023-12-17

### Robustness (ROB)
-  Out-of-bounds issue in handle_tj (text extraction) (#2342)

### Developer Experience (DEV)
-  Make make_release.py easier to configure (#2348)

### Maintenance (MAINT)
-  Bump actions/download-artifact from 3 to 4 (#2344)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.17.2...3.17.3)

## Version 3.17.2, 2023-12-10

### Bug Fixes (BUG)
-  Cope with deflated images with CMYK Black Only (#2322)
-  Handle indirect objects as parameters for CCITTFaxDecode (#2307)
-  check words length in _cmap type1_alternative function (#2310)

### Robustness (ROB)
-  Relax flate decoding for too many lookup values (#2331)
-  Let _build_destination skip in case of missing /D key (#2018)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.17.1...3.17.2)

## Version 3.17.1, 2023-11-14

### Bug Fixes (BUG)
-  Mediabox expansion size when applying non-right angle rotation (#2282)

### Robustness (ROB)
-  MissingWidth is IndirectObject (#2288)
-  Initialize states array with an empty value (#2280)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.17.0...3.17.1)

## Version 3.17.0, 2023-10-29

### Security (SEC)
-  Infinite recursion when using PdfWriter(clone_from=reader) (#2264)

### New Features (ENH)
-  Add parameter to select images to be removed (#2214)

### Bug Fixes (BUG)
-  Correctly handle image mode 1 with FlateDecode (#2249)
-  Error when filling a value with parentheses #2268 (#2269)
-  Handle empty root outline (#2239)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.16.4...3.17.0)

## Version 3.16.4, 2023-10-10

### Bug Fixes (BUG)
-  Avoid exceeding recursion depth when retrieving image mode (#2251)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.16.3...3.16.4)

## Version 3.16.3, 2023-10-08

### Bug Fixes (BUG)
-  Invalid cm/tm in visitor functions (#2206)
-  Encrypt / decrypt Stream object dictionaries (#2228)
-  Support nested color spaces for the /DeviceN color space (#2241)
-  Images property fails if NullObject in list (#2215)

### Developer Experience (DEV)
-  Unify mypy options and warn redundant workarounds (#2223)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.16.2...3.16.3)

## Version 3.16.2, 2023-09-24

### Bug Fixes (BUG)
-  PDF size increases because of too high float writing precision (#2213)
-  Fix test_watermarking_reportlab_rendering() (#2203)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.16.1...3.16.2)

## Version 3.16.1, 2023-09-17

⚠️ The 'rename PdfWriter.create_viewer_preference to
PdfWriter.create_viewer_preferences (#2190)' could be a breaking change for you,
if you use it. As it was only introduced last week I'm confident enough that
nobody will be affected though. Hence only the patch update.

### Bug Fixes (BUG)
-  Missing new line in extract_text with cm operations (#2142)
-  _get_fonts not processing properly CIDFonts and annotations (#2194)

### Maintenance (MAINT)
-  Rename PdfWriter.create_viewer_preference to PdfWriter.create_viewer_preferences (#2190)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.16.0...3.16.1)

## Version 3.16.0, 2023-09-10

### Security (SEC)
-  Infinite recursion caused by IndirectObject clone (#2156)

### New Features (ENH)
-  Ease access to ViewerPreferences (#2144)

### Bug Fixes (BUG)
-  Catch the case where w[0] is an IndirectObject instead of an int (#2154)
-  Cope with indirect objects in filters and remove deprecated code (#2177)
-  Accept tabs in cmaps (#2174) / cope with extra space (#2151)
-  Merge pages without resources (#2150)
-  getcontents() shall return None if contents is NullObject (#2161)
-  Fix conversion from 1 to LA (#2175)

### Robustness (ROB)
-  Accept XYZ with no arguments (#2178)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.5...3.16.0)

## Version 3.15.5, 2023-09-03

### Bug Fixes (BUG)
-  Cope with missing /I in articles (#2134)
-  Fix image look-up table in EncodedStreamObject (#2128)
-  remove_images not operating in sub level forms (#2133)

### Robustness (ROB)
-  Cope with damaged PDF (#2129)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.4...3.15.5)

## Version 3.15.4, 2023-08-27

### Performance Improvements (PI)
-  Making pypdf as fast as pdfrw (#2086)

### Maintenance (MAINT)
-  Relax typing_extensions version (#2104)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.3...3.15.4)

## Version 3.15.3, 2023-08-26

### Bug Fixes (BUG)
-  Check version of crypt provider (#2115)
-  TypeError: can't concat str to bytes (#2114)
-  Require flit_core >= 3.9 (#2091)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.2...3.15.3)

## Version 3.15.2, 2023-08-20

### Security (SEC)
-  Avoid endless recursion of reading damaged PDF file (#2093)

### Performance Improvements (PI)
-  Reuse content stream (#2101)

### Maintenance (MAINT)
-  Make ParseError inherit from PyPdfError (#2097)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.1...3.15.2)

## Version 3.15.1, 2023-08-13

### Performance Improvements (PI)
-  optimize _decode_png_prediction (#2068)

### Bug Fixes (BUG)
-  Fix incorrect tm_matrix in call to visitor_text (#2060)
-  Writing German characters into form fields (#2047)
-  Prevent stall when accessing image in corrupted pdf (#2081)
-  append() fails when articles do not have /T (#2080)

### Robustness (ROB)
-  Cope with xref not followed by separator (#2083)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.15.0...3.15.1)

## Version 3.15.0, 2023-08-06

### New Features (ENH)
-  Add `level` parameter to compress_content_streams (#2044)
-  Process /uniHHHH for text_extract (#2043)

### Bug Fixes (BUG)
-  Fix AnnotationBuilder.link (#2066)
-  JPX image without ColorSpace  (#2062)
-  Added check for field /Info when cloning reader document (#2055)
-  Fix indexed/CMYK images (#2039)

### Maintenance (MAINT)
-  Cryptography as primary dependency (#2053)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.14.0...3.15.0)

## Version 3.14.0, 2023-07-29

### New Features (ENH)
-  Accelerate image list keys generation (#2014)
-  Use `cryptography` for encryption/decryption as a fallback for PyCryptodome (#2000)
-  Extract LaTeX characters (#2016)
-  ASCIIHexDecode.decode now returns bytes instead of str (#1994)

### Bug Fixes (BUG)
-  Add RunLengthDecode filter (#2012)
-  Process /Separation ColorSpace (#2007)
-  Handle single element ColorSpace list (#2026)
-  Process lookup decoded as TextStringObjects (#2008)

### Robustness (ROB)
-  Cope with garbage collector during cloning (#1841)

### Maintenance (MAINT)
-  Cleanup of annotations (#1745)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.13.0...3.14.0)

## Version 3.13.0, 2023-07-23

### New Features (ENH)
-  Add is_open in outlines in PdfReader and PdfWriter (#1960)

### Bug Fixes (BUG)
-  Search /DA in hierarchy fields (#2002)
-  Cope with different ISO date length (#1999)
-  Decode Black only/CMYK deviceN images (#1984)
-  Process CMYK in deflate images (#1977)

### Developer Experience (DEV)
-  Add mypy to pre-commit (#2001)
-  Release automation (#1991, #1985)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.12.2...3.13.0)

## Version 3.12.2, 2023-07-16

### Bug Fixes (BUG)
-  Accept calRGB and calGray color_spaces (#1968)
-  Process 2bits and 4bits images (#1967)
-  Check for AcroForm and ensure it is not None (#1965)

### Developer Experience (DEV)
-  Automate the release process (#1970)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.12.1...3.12.2)

## Version 3.12.1, 2023-07-09

### Bug Fixes (BUG)
-  Prevent updating page contents after merging page (stamping/watermarking) (#1952)
-  % to be hex encoded in names (#1958)
-  Inverse color in CMYK images (#1947)
-  Dates conversion not working with Z00\'00\' (#1946)
-  Support UTF-16-LE Strings (#1884)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.12.0...3.12.1)

## Version 3.12.0, 2023-07-02

### New Features (ENH)
-  Add AES support for encrypting PDF files (#1918, #1935, #1936, #1938)
-  Add page deletion feature to PdfWriter (#1843)

### Bug Fixes (BUG)
-  PdfReader.get_fields() attempts to delete non-existing index "/Off" (#1933)
-  Remove unused objects when cloning_from (#1926)
-  Add the TK.SIZE into the trailer (#1911)
-  add_named_destination() maintains named destination list sort order (#1930)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.11.1...3.12.0)

## Version 3.11.1, 2023-06-25

### Bug Fixes (BUG)
- Cascaded filters in image objects (#1913)
- Append pdf with named destination using numbers for pages (#1858)
- Ignore "/B" fields only on pages in PdfWriter.append() (#1875)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.11.0...3.11.1)

## Version 3.11.0, 2023-06-23

### New Features (ENH)
-  Add page_number property (#1856)

### Bug Fixes (BUG)
- File expansion when updating with Page Contents (#1906)
- Missing Alternate in indexed/ICCbased colorspaces (#1896)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.10.0...3.11.0)

## Version 3.10.0, 2023-06-18

### New Features (ENH)
-  Extraction of inline images (#1850)
-  Add capability to replace image (#1849)
-  Extend images interface by returning an ImageFile(File) class (#1848)
-  Add set_data to EncodedStreamObject (#1854)

### Bug Fixes (BUG)
-  Fix RGB FlateEncode Images(PNG) and transparency (#1834)
-  Generate static appearance for fields (#1864)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.9.1...3.10.0)

## Version 3.9.1, 2023-06-04

### Deprecations (DEP)
-  Deprecate PdfMerger (#1866)

### Bug Fixes (BUG)
-  Ignore UTF-8 decode errors (#1865)

### Robustness (ROB)
-  Handle missing /Type entry in Page tree (#1859)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.9.0...3.9.1)

## Version 3.9.0, 2023-05-21

### New Features (ENH)
-  Simplify metadata input (Document Information Dictionary) (#1851)
-  Extend cmap compatibility to GBK_EUC_H/V (#1812)

### Bug Fixes (BUG)
-  Prevent infinite loop when no character follows after a comment (#1828)
-  get_contents does not return ContentStream (#1847)
-  Accept XYZ destination with zoom missing (default to zoom=0.0) (#1844)
-  Cope with 1 Bit images (#1815)

### Robustness (ROB)
-  Handle missing /Type entry in Page tree (#1845)

### Documentation (DOC)
-  Expand file size explanations (#1835)
-  Add comparison with pdfplumber (#1837)
-  Clarify that PyPDF2 is dead (#1827)
-  Add Hunter King as Contributor for #1806

### Maintenance (MAINT)
-  Refactor internal Encryption class (#1821)
-  Add R parameter to generate_values (#1820)
-  Make encryption_key parameter of write_to_stream optional (#1819)
-  Prepare for adding AES encryption support (#1818)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.8.1...3.9.0)


## Version 3.8.1, 2023-04-23

### Bug Fixes (BUG)
-  Convert color space before saving (#1802)

### Documentation (DOC)
-  PDF/A (#1807)
-  Use append instead of add_page
-  Document core mechanics of pypdf (#1783)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.8.0...3.8.1)

## Version 3.8.0, 2023-04-16

### New Features (ENH)
-  Add transform method to Transformation class (#1765)
-  Cope with UC2 fonts in text_extraction (#1785)

### Robustness (ROB)
-  Invalid startxref pointing 1 char before (#1784)

### Maintenance (MAINT)
-  Mark code handling old parameters as deprecated (#1798)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.7.1...3.8.0)


## Version 3.7.1, 2023-04-09

### Security (SEC)
-  Warn about PDF encryption security (#1755)

### Robustness (ROB)
-  Prevent loop in Cloning (#1770)
-  Capture UnicodeDecodeError at PdfReader.pdf_header (#1768)

### Documentation (DOC)
-  Add .readthedocs.yaml and bump docs dependencies using `tox -e deps` (#1750, #1752)

### Developer Experience (DEV)
-  Make make_changelog.py idempotent

### Maintenance (MAINT)
-  Move generation of file identifiers to a method (#1760)

### Testing (TST)
-  Add xmp test (#1775)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.7.0...3.7.1)

## Version 3.7.0, 2023-03-26

### Security (SEC)
-  Use Python's secrets module instead of random module (#1748)

### New Features (ENH)
-  Add AnnotationBuilder.highlight text markup annotation (#1740)
-  Add AnnotationBuilder.popup (#1665)
-  Add AnnotationBuilder.polyline annotation support (#1726)
-  Add clone_from parameter in PdfWriter constructor (#1703)

### Bug Fixes (BUG)
-  'DictionaryObject' object has no attribute 'indirect_reference' (#1729)

### Robustness (ROB)
-  Handle params NullObject in decode_stream_data (#1738)

### Documentation (DOC)
-  Project scope (#1743)

### Maintenance (MAINT)
-  Add AnnotationFlag (#1746)
-  Add LazyDict.__str__ (#1727)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.6.0...3.7.0)


## Version 3.6.0, 2023-03-18

### New Features (ENH)
-  Extend PdfWriter.append() to PageObjects (#1704)
-  Support qualified names in update_page_form_field_values (#1695)

### Robustness (ROB)
-  Tolerate streams without length field (#1717)
-  Accept DictionaryObject in /D of NamedDestination (#1720)
-  Widths def in cmap calls IndirectObject (#1719)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.5.2...3.6.0)


## Version 3.5.2, 2023-03-12

⚠️ We discovered that compress_content_stream has to be applied to a page of
  the PdfWriter. It may not be applied to a page of the PdfReader!

### Bug Fixes (BUG)
-  compress_content_stream not readable in Adobe Acrobat (#1698)
-  Pass logging parameters correctly in set_need_appearances_writer (#1697)
-  Write /Root/AcroForm in set_need_appearances_writer (#1639)

### Robustness (ROB)
-  Allow more whitespaces within linearized file (#1701)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.5.1...3.5.2)


## Version 3.5.1, 2023-03-05

### Robustness (ROB)
-  Some attributes not copied in DictionaryObject._clone (#1635)
-  Allow merging multiple time pages with annots (#1624)

### Testing (TST)
-  Replace pytest.mark.external by enable_socket (#1657)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.5.0...3.5.1)

## Version 3.5.0, 2023-02-26

### New Features (ENH)
-  Add reader.attachments public interface (#1611, #1661)
-  Add PdfWriter.remove_objects_from_page(page: PageObject, to_delete: ObjectDeletionFlag) (#1648)
-  Allow free-text annotation to have transparent border/background (#1664)

### Bug Fixes (BUG)
-  Allow decryption with empty password for AlgV5 (#1663)
-  Let PdfWriter.pages return PageObject after calling `clone_document_from_reader()` (#1613)
-  Invalid font pointed during merge_resources (#1641)

### Robustness (ROB)
-  Cope with invalid objects in IndirectObject.clone (#1637)
-  Improve tolerance to invalid Names/Dests (#1658)
-  Decode encoded values in get_fields (#1636)
-  Let PdfWriter.merge cope with missing "/Fields" (#1628)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.4.1...3.5.0)


## Version 3.4.1, 2023-02-12

### Bug Fixes (BUG)
-  Switch from trimbox to cropbox when merging pages (#1622)
-  Text extraction not working with one glyph to char sequence (#1620)

### Robustness (ROB)
-  Fix 2 cases of "object has no attribute \'indirect_reference\'" (#1616)

### Testing (TST)
-  Add multiple retry on get_url for external PDF downloads (#1626)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.4.0...3.4.1)

## Version 3.4.0, 2023-02-05

NOTICE: pypdf changed the way it represents numbers parsed from PDF files.
  pypdf<3.4.0 represented numbers as Decimal, pypdf>=3.4.0 represents them as
  floats. Several other PDF libraries to this, as well as many PDF viewers.
  We hope to fix issues with too high precision like this and get a speed boost.
  In case your PDF documents rely on more than 18 decimals of precision you
  should check if it still works as expected.
  To clarify: This does not affect the text shown in PDF documents. It affects
  numbers, e.g. when graphics are drawn on the PDF or very exact positions are
  used. Typically, 5 decimals should be enough.

### New Features (ENH)
-  Enable merging forms with overlapping names (#1553)
-  Add 'over' parameter to merge_transformend_page & co (#1567)

### Bug Fixes (BUG)
-  Fix getter of the PageObject.rotation property with an indirect object (#1602)
-  Restore merge_transformed_page & co (#1567)
-  Replace decimal by float (#1563)

### Robustness (ROB)
-  PdfWriter.remove_images: /Contents might not be in page_ref (#1598)

### Developer Experience (DEV)
-  Introduce ruff (#1586, #1609)

### Maintenance (MAINT)
-  Remove decimal (#1608)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.3.0...3.4.0)

## Version 3.3.0, 2023-01-22

### New Features (ENH)
-  Add page label support to PdfWriter (#1558)
-  Accept inline images with space before EI (#1552)
-  Add circle annotation support (#1556)
-  Add polygon annotation support (#1557)
-  Make merging pages produce a deterministic PDF (#1542, #1543)

### Bug Fixes (BUG)
-  Fix error in cmap extraction (#1544)
-  Remove erroneous assertion check (#1564)
-  Fix dictionary access of optional page label keys (#1562)

### Robustness (ROB)
-  Set ignore_eof=True for read_until_regex (#1521)

### Documentation (DOC)
-  Paper size (#1550)

### Developer Experience (DEV)
-  Fix broken combination of dependencies of docs.txt
-  Annotate tests appropriately (#1551)

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.2.1...3.3.0)


## Version 3.2.1, 2023-01-08

### Bug Fixes (BUG)
-  Accept hierarchical fields (#1529)

### Documentation (DOC)
-  Use google style docstrings (#1534)
-  Fix linked markdown documents (#1537)

### Developer Experience (DEV)
-  Update docs config (#1535)

## Version 3.2.0, 2022-12-31

### Performance Improvement (PI)
-  Help the specializing adaptive interpreter (#1522)

### New Features (ENH)
-  Add support for page labels (#1519)

### Bug Fixes (BUG)
-  upgrade clone_document_root (#1520)


[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.1.0...3.1.1)

## Version 3.1.0, 2022-12-23

Move PyPDF2 to pypdf (#1513). This now it's all lowercase, no number in the
name. For installation and for import. PyPDF2 will no longer receive updates.
The community should move back to its roots.

If you were still using pyPdf or PyPDF2 < 2.0.0, I recommend reading the
migration guide: https://pypdf.readthedocs.io/en/latest/user/migration-1-to-2.html

pypdf==3.1.0 is only different from PyPDF2==3.0.0 in the package name.
Replacing "PyPDF2" by "pypdf" should be enough if you migrate from
`PyPDF2==3.0.0` to `pypdf==3.1.0`.

[Full Changelog](https://github.com/py-pdf/pypdf/compare/3.0.0...3.1.0)

## Version 3.0.0, 2022-12-22

### BREAKING CHANGES ⚠️
-  Deprecate features with PyPDF2==3.0.0 (#1489)
-  Refactor Fit / Zoom parameters (#1437)

### New Features (ENH)
-  Add Cloning  (#1371)
-  Allow int for indirect_reference in PdfWriter.get_object (#1490)

### Documentation (DOC)
-  How to read PDFs from S3 (#1509)
-  Make MyST parse all links as simple hyperlinks (#1506)
-  Changed 'latest' for 'stable' generated docs (#1495)
-  Adjust deprecation procedure (#1487)

### Maintenance (MAINT)
-  Use typing.IO for file streams (#1498)


[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.12.1...3.0.0)

## Version 2.12.1, 2022-12-10

### Documentation (DOC)
-  Deduplicate extract_text docstring (#1485)
-  How to cite PyPDF2 (#1476)

### Maintenance (MAINT)
Consistency changes:
  -  indirect_ref/ido ➔ indirect_reference, dest➔ page_destination (#1467)
  -  owner_pwd/user_pwd ➔ owner_password/user_password (#1483)
  -  position ➜ page_number in Merger.merge (#1482)
  -  indirect_ref ➜ indirect_reference (#1484)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.12.0...2.12.1)


## Version 2.12.0, 2022-12-10

### New Features (ENH)
-  Add support to extract gray scale images (#1460)
-  Add 'threads' property to PdfWriter (#1458)
-  Add 'open_destination' property to PdfWriter (#1431)
-  Make PdfReader.get_object accept integer arguments (#1459)

### Bug Fixes (BUG)
-  Scale PDF annotations (#1479)

### Robustness (ROB)
-  Padding issue with AES encryption (#1469)
-  Accept empty object as null objects (#1477)

### Documentation (DOC)
-  Add module documentation the PaperSize class (#1447)

### Maintenance (MAINT)
-  Use 'page_number' instead of 'pagenum' (#1365)
-  Add List of pages to PageRangeSpec (#1456)

### Testing (TST)
-  Cleanup temporary files (#1454)
-  Mark test_tounicode_is_identity as external (#1449)
-  Use Ubuntu 20.04 for running CI test suite (#1452)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.11.2...2.12.0)


## Version 2.11.2, 2022-11-20

### New Features (ENH)
-  Add remove_from_tree (#1432)
-  Add AnnotationBuilder.rectangle (#1388)

### Bug Fixes (BUG)
-  JavaScript executed twice (#1439)
-  ToUnicode stores /Identity-H instead of stream (#1433)
-  Declare Pillow as optional dependency (#1392)

### Developer Experience (DEV)
-  Link 'Full Changelog' automatically
-  Modify read_string_from_stream to a benchmark (#1415)
-  Improve error reporting of read_object (#1412)
-  Test Python 3.11 (#1404)
-  Extend Flake8 ignore list (#1410)
-  Use correct pytest markers (#1407)
-  Move project configuration to pyproject.toml (#1382)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.11.1...2.11.2)

## Version 2.11.1, 2022-10-09

### Bug Fixes (BUG)
- td matrix (#1373)
- Cope with cmap from #1322 (#1372)

### Robustness (ROB)
-  Cope with str returned from get_data in cmap (#1380)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.11.0...2.11.1)

## Version 2.11.0, 2022-09-25

### New Features (ENH)
-  Addition of optional visitor-functions in extract_text() (#1252)
-  Add metadata.creation_date and modification_date (#1364)
-  Add PageObject.images attribute (#1330)

### Bug Fixes (BUG)
-  Lookup index in _xobj_to_image can be ByteStringObject (#1366)
-  'IndexError: index out of range' when using extract_text (#1361)
-  Errors in transfer_rotation_to_content() (#1356)

### Robustness (ROB)
-  Ensure update_page_form_field_values does not fail if no fields (#1346)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.9...2.11.0)

## Version 2.10.9, 2022-09-18

### New Features (ENH)
-  Add rotation property and transfer_rotate_to_content (#1348)

### Performance Improvements (PI)
-  Avoid string concatenation with large embedded base64-encoded images (#1350)

### Bug Fixes (BUG)
-  Format floats using their intrinsic decimal precision (#1267)

### Robustness (ROB)
-  Fix merge_page for pages without resources (#1349)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.8...2.10.9)

## Version 2.10.8, 2022-09-14

### New Features (ENH)
-  Add PageObject.user_unit property (#1336)

### Robustness (ROB)
-  Improve NameObject reading/writing (#1345)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.7...2.10.8)

## Version 2.10.7, 2022-09-11

### Bug Fixes (BUG)
-  Fix Error in transformations (#1341)
-  Decode #23 in NameObject (#1342)

### Testing (TST)
-  Use pytest.warns() for warnings, and .raises() for exceptions (#1325)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.6...2.10.7)


## Version 2.10.6, 2022-09-09

### Robustness (ROB)
-  Fix infinite loop due to Invalid object (#1331)
-  Fix image extraction issue with superfluous whitespaces (#1327)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.5...2.10.6)

## Version 2.10.5, 2022-09-04

### New Features (ENH)
-  Process XRefStm (#1297)
-  Auto-detect RTL for text extraction (#1309)

### Bug Fixes (BUG)
-  Avoid scaling cropbox twice (#1314)

### Robustness (ROB)
-  Fix offset correction in revised PDF (#1318)
-  Crop data of /U and /O in encryption dictionary to 48 bytes (#1317)
-  MultiLine bfrange in cmap (#1299)
-  Cope with 2 digit codes in bfchar (#1310)
-  Accept '/annn' charset as ASCII code (#1316)
-  Log errors during Float / NumberObject initialization (#1315)
-  Cope with corrupted entries in xref table (#1300)

### Documentation (DOC)
-  Migration guide (PyPDF2 1.x ➔ 2.x) (#1324)
-  Creating a coverage report (#1319)
-  Fix AnnotationBuilder.free_text example (#1311)
-  Fix usage of page.scale by replacing it with page.scale_by (#1313)

### Maintenance (MAINT)
-  PdfReaderProtocol (#1303)
-  Throw PdfReadError if Trailer can't be read (#1298)
-  Remove catching OverflowException (#1302)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.4...2.10.5)


## Version 2.10.4, 2022-08-28

### Robustness (ROB)
-  Fix errors/warnings on no /Resources within extract_text (#1276)
-  Add required line separators in ContentStream ArrayObjects (#1281)

### Maintenance (MAINT)
-  Use NameObject idempotency (#1290)

### Testing (TST)
-  Rectangle deletion (#1289)
-  Add workflow tests (#1287)
-  Remove files after tests ran (#1286)

### Packaging (PKG)
-  Add minimum version for typing_extensions requirement (#1277)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.3...2.10.4)

## Version 2.10.3, 2022-08-21

### Robustness (ROB)
-  Decrypt returns empty bytestring (#1258)

### Developer Experience (DEV)
-  Modify CI to better verify built package contents (#1244)

### Maintenance (MAINT)
-  Remove 'mine' as PdfMerger always creates the stream (#1261)
-  Let PdfMerger._create_stream raise NotImplemented (#1251)
-  password param of _security._alg32(...) is only a string, not bytes (#1259)
-  Remove unreachable code in read_block_backwards (#1250)
   and sign function in _extract_text (#1262)

### Testing (TST)
-  Delete annotations (#1263)
-  Close PdfMerger in tests (#1260)
-  PdfReader.xmp_metadata workflow (#1257)
-  Various PdfWriter (Layout, Bookmark deprecation) (#1249)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.2...2.10.3)

## Version 2.10.2, 2022-08-15

BUG: Add PyPDF2.generic to PyPI distribution

## Version 2.10.1, 2022-08-15

### Bug Fixes (BUG)
-  TreeObject.remove_child had a non-PdfObject assignment for Count (#1233, #1234)
-  Fix stream truncated prematurely (#1223)

### Documentation (DOC)
-  Fix docstring formatting (#1228)

### Maintenance (MAINT)
-  Split generic.py (#1229)

### Testing (TST)
-  Decrypt AlgV4 with owner password (#1239)
-  AlgV5.generate_values (#1238)
-  TreeObject.remove_child / empty_tree (#1235, #1236)
-  create_string_object (#1232)
-  Free-Text annotations (#1231)
-  generic._base (#1230)
-  Strict get fonts (#1226)
-  Increase PdfReader coverage (#1219, #1225)
-  Increase PdfWriter coverage (#1237)
-  100% coverage for utils.py (#1217)
-  PdfWriter exception non-binary stream (#1218)
-  Don't check coverage for deprecated code (#1216)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.10.0...2.10.1)


## Version 2.10.0, 2022-08-07

### New Features (ENH)
-  "with" support for PdfMerger and PdfWriter (#1193)
-  Add AnnotationBuilder.text(...) to build text annotations (#1202)

### Bug Fixes (BUG)
-  Allow IndirectObjects as stream filters (#1211)

### Documentation (DOC)
-  Font scrambling
-  Page vs Content scaling (#1208)
-  Example for orientation parameter of extract_text (#1206)
-  Fix AnnotationBuilder parameter formatting (#1204)

### Developer Experience (DEV)
-  Add flake8-print (#1203)

### Maintenance (MAINT)
-  Introduce WrongPasswordError / FileNotDecryptedError / EmptyFileError  (#1201)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.9.0...2.10.0)

## Version 2.9.0, 2022-07-31

### New Features (ENH)
-  Add ability to add hex encoded colors to outline items (#1186)
-  Add support for pathlib.Path in PdfMerger.merge (#1190)
-  Add link annotation (#1189)
-  Add capability to filter text extraction by orientation (#1175)

### Bug Fixes (BUG)
-  Named Dest in PDF1.1 (#1174)
-  Incomplete Graphic State save/restore (#1172)

### Documentation (DOC)
-  Update changelog url in package metadata (#1180)
-  Mention camelot for table extraction (#1179)
-  Mention pyHanko for signing PDF documents (#1178)
-  Weow have CMAP support since a while (#1177)

### Maintenance (MAINT)
-  Consistent usage of warnings / log messages (#1164)
-  Consistent terminology for outline items (#1156)


[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.8.1...2.9.0)

## Version 2.8.1, 2022-07-25

### Bug Fixes (BUG)
-  u_hash in AlgV4.compute_key (#1170)

### Robustness (ROB)
-  Fix loading of file from #134 (#1167)
-  Cope with empty DecodeParams (#1165)

### Documentation (DOC)
-  Typo in merger deprecation warning message (#1166)

### Maintenance (MAINT)
-  Package updates; solve mypy strict remarks (#1163)

### Testing (TST)
-  Add test from #325 (#1169)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.8.0...2.8.1)


## Version 2.8.0, 2022-07-24

### New Features (ENH)
-  Add writer.add_annotation, page.annotations, and generic.AnnotationBuilder (#1120)

### Bug Fixes (BUG)
-  Set /AS for /Btn form fields in writer (#1161)
-  Ignore if /Perms verify failed (#1157)

### Robustness (ROB)
-  Cope with utf16 character for space calculation (#1155)
-  Cope with null params for FitH / FitV destination (#1152)
-  Handle outlines without valid destination (#1076)

### Developer Experience (DEV)
-  Introduce _utils.logger_warning (#1148)

### Maintenance (MAINT)
-  Break up parse_to_unicode (#1162)
-  Add diagnostic output to exception in read_from_stream (#1159)
-  Reduce PdfReader.read complexity (#1151)

### Testing (TST)
-  Add workflow tests found by arc testing (#1154)
-  Decrypt file which is not encrypted (#1149)
-  Test CryptRC4 encryption class; test image extraction filters (#1147)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.7.0...2.8.0)

## Version 2.7.0, 2022-07-21

### New Features (ENH)
-  Add `outline_count` property (#1129)

### Bug Fixes (BUG)
-  Make reader.get_fields also return dropdowns with options (#1114)
-  Add deprecated EncodedStreamObject functions back until PyPDF2==3.0.0 (#1139)

### Robustness (ROB)
-  Cope with missing /W entry (#1136)
-  Cope with invalid parent xref (#1133)

### Documentation (DOC)
-  Contributors file (#1132)
-  Fix type in signature of PdfWriter.add_uri (#1131)

### Developer Experience (DEV)
-  Add .git-blame-ignore-revs (#1141)

### Code Style (STY)
-  Fixing typos (#1137)
-  Reuse code via get_outlines_property in tests (#1130)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.6.0...2.7.0)

## Version 2.6.0, 2022-07-17

### New Features (ENH)
-  Add color and font_format to PdfReader.outlines[i] (#1104)
-  Extract Text Enhancement (whitespaces) (#1084)

### Bug Fixes (BUG)
-  Use `build_destination` for named destination outlines (#1128)
-  Avoid a crash when a ToUnicode CMap has an empty dstString in beginbfchar (#1118)
-  Prevent deduplication of PageObject (#1105)
-  None-check in DictionaryObject.read_from_stream (#1113)
-  Avoid IndexError in _cmap.parse_to_unicode (#1110)

### Documentation (DOC)
-  Explanation for git submodule
-  Watermark and stamp (#1095)

### Maintenance (MAINT)
-  Text extraction improvements (#1126)
-  Destination.color returns ArrayObject instead of tuple as fallback (#1119)
-  Use add_bookmark_destination in add_bookmark (#1100)
-  Use add_bookmark_destination in add_bookmark_dict (#1099)

### Testing (TST)
-  Add test for arab text (#1127)
-  Add xfail for decryption fail (#1125)
-  Add xfail test for IndexError when extracting text (#1124)
-  Add MCVE showing outline title issue (#1123)

### Code Style (STY)
-  Use IntFlag for permissions_flag / update_page_form_field_values (#1094)
-  Simplify code (#1101)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.5.0...2.6.0)

## Version 2.5.0, 2022-07-10

### New Features (ENH)
-  Add support for indexed color spaces / BitsPerComponent for decoding PNGs (#1067)
-  Add PageObject._get_fonts (#1083)

### Performance Improvements (PI)
-  Use iterative DFS in PdfWriter._sweep_indirect_references (#1072)

### Bug Fixes (BUG)
-  Let Page.scale also scale the crop-/trim-/bleed-/artbox (#1066)
-  Column default for CCITTFaxDecode (#1079)

### Robustness (ROB)
-  Guard against None-value in _get_outlines (#1060)

### Documentation (DOC)
-  Stamps and watermarks (#1082)
-  OCR vs PDF text extraction (#1081)
-  Python Version support
-  Formatting of CHANGELOG

### Developer Experience (DEV)
-  Cache downloaded files (#1070)
-  Speed-up for CI (#1069)

### Maintenance (MAINT)
-  Set page.rotate(angle: int) (#1092)
-  Issue #416 was fixed by #1015 (#1078)

### Testing (TST)
-  Image extraction (#1080)
-  Image extraction (#1077)

### Code Style (STY)
-  Apply black
-  Typo in Changelog

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.4.2...2.5.0)

## Version 2.4.2, 2022-07-05

### New Features (ENH)
-  Add PdfReader.xfa attribute (#1026)

### Bug Fixes (BUG)
-  Wrong page inserted when PdfMerger.merge is done (#1063)
-  Resolve IndirectObject when it refers to a free entry (#1054)

### Developer Experience (DEV)
-  Added {posargs} to tox.ini (#1055)

### Maintenance (MAINT)
-  Remove PyPDF2._utils.bytes_type (#1053)

### Testing (TST)
-  Scale page (indirect rect object) (#1057)
-  Simplify pathlib PdfReader test (#1056)
-  IndexError of VirtualList (#1052)
-  Invalid XML in xmp information (#1051)
-  No pycryptodome (#1050)
-  Increase test coverage (#1045)

### Code Style (STY)
-  DOC of compress_content_streams (#1061)
-  Minimize diff for #879 (#1049)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.4.1...2.4.2)

## Version 2.4.1, 2022-06-30

### New Features (ENH)
-  Add writer.pdf_header property (getter and setter) (#1038)

### Performance Improvements (PI)
-  Remove b_ call in FloatObject.write_to_stream (#1044)
-  Check duplicate objects in writer._sweep_indirect_references (#207)

### Documentation (DOC)
-  How to surppress exceptions/warnings/log messages (#1037)
-  Remove hyphen from lossless (#1041)
-  Compression of content streams (#1040)
-  Fix inconsistent variable names in add-watermark.md (#1039)
-  File size reduction
-  Add CHANGELOG to the rendered docs (#1023)

### Maintenance (MAINT)
-  Handle XML error when reading XmpInformation (#1030)
-  Deduplicate Code / add mutmut config (#1022)

### Code Style (STY)
-  Use unnecessary one-line function / class attribute (#1043)
-  Docstring formatting (#1033)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.4.0...2.4.1)

## Version 2.4.0, 2022-06-26

### New Features (ENH):
-  Support R6 decrypting (#1015)
-  Add PdfReader.pdf_header (#1013)

### Performance Improvements (PI):
-  Remove ord_ calls (#1014)

### Bug Fixes (BUG):
-  Fix missing page for bookmark (#1016)

### Robustness (ROB):
-  Deal with invalid Destinations (#1028)

### Documentation (DOC):
-  get_form_text_fields does not extract dropdown data (#1029)
-  Adjust PdfWriter.add_uri docstring
-  Mention crypto extra_requires for installation (#1017)

### Developer Experience (DEV):
-  Use /n line endings everywhere (#1027)
-  Adjust string formatting to be able to use mutmut (#1020)
-  Update Bug report template

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.3.1...2.4.0)

## Version 2.3.1, 2022-06-19

BUG: Forgot to add the internal `_codecs` subpackage.

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.3.0...2.3.1)

## Version 2.3.0, 2022-06-19

The highlight of this release is improved support for file encryption
(AES-128 and AES-256, R5 only). See #749 for the amazing work of
@exiledkingcc 🎊 Thank you 🤗

### Deprecations (DEP)
-  Rename names to be PEP8-compliant (#967)
  - `PdfWriter.get_page`: the pageNumber parameter is renamed to page_number
  - `PyPDF2.filters`:
    * For all classes, a parameter rename: decodeParms ➔ decode_parms
    * decodeStreamData ➔ decode_stream_data
  - `PyPDF2.xmp`:
    * XmpInformation.rdfRoot ➔ XmpInformation.rdf_root
    * XmpInformation.xmp_createDate ➔ XmpInformation.xmp_create_date
    * XmpInformation.xmp_creatorTool ➔ XmpInformation.xmp_creator_tool
    * XmpInformation.xmp_metadataDate ➔ XmpInformation.xmp_metadata_date
    * XmpInformation.xmp_modifyDate ➔ XmpInformation.xmp_modify_date
    * XmpInformation.xmpMetadata ➔ XmpInformation.xmp_metadata
    * XmpInformation.xmpmm_documentId ➔ XmpInformation.xmpmm_document_id
    * XmpInformation.xmpmm_instanceId ➔ XmpInformation.xmpmm_instance_id
  - `PyPDF2.generic`:
    * readHexStringFromStream ➔ read_hex_string_from_stream
    * initializeFromDictionary ➔ initialize_from_dictionary
    * createStringObject ➔ create_string_object
    * TreeObject.hasChildren ➔ TreeObject.has_children
    * TreeObject.emptyTree ➔ TreeObject.empty_tree

### New Features (ENH)
-  Add decrypt support for V5 and AES-128, AES-256 (R5 only) (#749)

### Robustness (ROB)
-  Fix corrupted (wrongly) linear PDF (#1008)

### Maintenance (MAINT)
-  Move PDF_Samples folder into resources
-  Fix typos (#1007)

### Testing (TST)
-  Improve encryption/decryption test (#1009)
-  Add merger test cases with real PDFs (#1006)
-  Add mutmut config

### Code Style (STY)
-  Put pure data mappings in separate files (#1005)
-  Make encryption module private, apply pre-commit (#1010)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.2.1...2.3.0)

## Version 2.2.1, 2022-06-17

### Performance Improvements (PI)
-  Remove b_ calls (#992, #986)
-  Apply improvements to _utils suggested by perflint (#993)

### Robustness (ROB)
-  utf-16-be codec can't decode (...) (#995)

### Documentation (DOC)
-  Remove reference to Scripts (#987)

### Developer Experience (DEV)
-  Fix type annotations for add_bookmarks (#1000)

### Testing (TST)
-  Add test for PdfMerger (#1001)
-  Add tests for XMP information (#996)
-  reader.get_fields / zlib issue / LZW decode issue (#1004)
-  reader.get_fields with report generation (#1002)
-  Improve test coverage by extracting texts (#998)

### Code Style (STY)
-  Apply fixes suggested by pylint (#999)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.2.0...2.2.1)

## Version 2.2.0, 2022-06-13

The 2.2.0 release improves text extraction again via (#969):

* Improvements around /Encoding / /ToUnicode
* Extraction of CMaps improved
* Fallback for font def missing
* Support for /Identity-H and /Identity-V: utf-16-be
* Support for /GB-EUC-H / /GB-EUC-V / GBp/c-EUC-H / /GBpc-EUC-V (beta release for evaluation)
* Arabic (for evaluation)
* Whitespace extraction improvements

Those changes should mainly improve the text extraction for non-ASCII alphabets,
e.g. Russian / Chinese / Japanese / Korean / Arabic.

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.1.1...2.2.0)

## Version 2.1.1, 2022-06-12

### New Features (ENH)
-  Add support for pathlib as input for PdfReader (#979)

### Performance Improvements (PI)
-  Optimize read_next_end_line (#646)

### Bug Fixes (BUG)
-  Adobe Acrobat 'Would you like to save this file?' (#970)

### Documentation (DOC)
-  Notes on annotations (#982)
-  Who uses PyPDF2
-  intendet \xe2\x9e\x94 in robustness page  (#958)

### Maintenance (MAINT)
-  pre-commit / requirements.txt updates (#977)
-  Mark read_next_end_line as deprecated (#965)
-  Export `PageObject` in PyPDF2 root (#960)

### Testing (TST)
-  Add MCVE of issue #416 (#980)
-  FlateDecode.decode decodeParms (#964)
-  Xmp module (#962)
-  utils.paeth_predictor (#959)

### Code Style (STY)
-  Use more tuples and list/dict comprehensions (#976)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.1.0...2.1.1)


## Version 2.1.0, 2022-06-06

The highlight of the 2.1.0 release is the most massive improvement to the
text extraction capabilities of PyPDF2 since 2016 🥳🎊 A very big thank you goes
to [pubpub-zz](https://github.com/pubpub-zz) who took a lot of time and
knowledge about the PDF format to finally get those improvements into PyPDF2.
Thank you 🤗💚

In case the new function causes any issues, you can use `_extract_text_old`
for the old functionality. Please also open a bug ticket in that case.

There were several people who have attempted to bring similar improvements to
PyPDF2. All of those were valuable. The main reason why they didn't get merged
is the big amount of open PRs / issues. pubpub-zz was the most comprehensive
PR which also incorporated the latest changes of PyPDF2 2.0.0.

Thank you to [VictorCarlquist](https://github.com/VictorCarlquist) for #858 and
[asabramo](https://github.com/asabramo) for #464 🤗

### New Features (ENH)
-  Massive text extraction improvement (#924). Closed many open issues:
    - Exceptions / missing spaces in extract_text() method (#17) 🕺
      - Whitespace issues in extract_text() (#42) 💃
      - pypdf2 reads the hifenated words in a new line (#246)
    - PyPDF2 failing to read unicode character (#37)
      - Unable to read bullets (#230)
    - ExtractText yields nothing for apparently good PDF (#168) 🎉
    - Encoding issue in extract_text() (#235)
    - extractText() doesn't work on Chinese PDF (#252)
    - encoding error (#260)
    - Trouble with apostophes in names in text "O'Doul" (#384)
    - extract_text works for some PDF files, but not the others (#437)
    - Euro sign not being recognized by extractText (#443)
    - Failed extracting text from French texts (#524)
    - extract_text doesn't extract ligatures correctly (#598)
    - reading spanish text - mark convert issue (#635)
    - Read PDF changed from text to random symbols (#654)
    - .extractText() reads / as 1. (#789)
-  Update glyphlist (#947) - inspired by #464
-  Allow adding PageRange objects (#948)

### Bug Fixes (BUG)
-  Delete .python-version file (#944)
-  Compare StreamObject.decoded_self with None (#931)

### Robustness (ROB)
-  Fix some conversion errors on non conform PDF (#932)

### Documentation (DOC)
-  Elaborate on PDF text extraction difficulties (#939)
-  Add logo (#942)
-  rotate vs Transformation().rotate (#937)
-  Example how to use PyPDF2 with AWS S3 (#938)
-  How to deprecate (#930)
-  Fix typos on robustness page (#935)
-  Remove scripts (pdfcat) from docs (#934)

### Developer Experience (DEV)
-  Ignore .python-version file
-  Mark deprecated code with no-cover (#943)
-  Automatically create Github releases from tags (#870)

### Testing (TST)
-  Text extraction for non-latin alphabets (#954)
-  Ignore PdfReadWarning in benchmark (#949)
-  writer.remove_text (#946)
-  Add test for Tree and _security (#945)

### Code Style (STY)
-  black, isort, Flake8, splitting buildCharMap (#950)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/2.0.0...2.1.0)

## Version 2.0.0, 2022-06-01

The 2.0.0 release of PyPDF2 includes three core changes:

1. Dropping support for Python 3.5 and older.
2. Introducing type annotations.
3. Interface changes, mostly to have PEP8-compliant names

We introduced a [deprecation process](https://github.com/py-pdf/PyPDF2/pull/930)
that hopefully helps users to avoid unexpected breaking changes.

### Breaking Changes (DEP)
- PyPDF2 2.0 requires Python 3.6+. Python 2.7 and 3.5 support were dropped.
- PdfFileReader: The "warndest" parameter was removed
- PdfFileReader and PdfFileMerger no longer have the `overwriteWarnings`
  parameter. The new behavior is `overwriteWarnings=False`.
- merger: OutlinesObject was removed without replacement.
- merger.py ➔ _merger.py: You must import PdfFileMerger from PyPDF2 directly.
- utils:
  * `ConvertFunctionsToVirtualList` was removed
  * `formatWarning` was removed
  * `isInt(obj)`: Use `instance(obj, int)` instead
  * `u_(s)`: Use `s` directly
  * `chr_(c)`: Use `chr(c)` instead
  * `barray(b)`: Use `bytearray(b)` instead
  * `isBytes(b)`: Use `instance(b, type(bytes()))` instead
  * `xrange_fn`: Use `range` instead
  * `string_type`: Use `str` instead
  * `isString(s)`: Use `instance(s, str)` instead
  * `_basestring`: Use `str` instead
  * All Exceptions are now in `PyPDF2.errors`:
    - PageSizeNotDefinedError
    - PdfReadError
    - PdfReadWarning
    - PyPdfError
- `PyPDF2.pdf` (the `pdf` module) no longer exists. The contents were moved with
  the library. You should most likely import directly from `PyPDF2` instead.
  The `RectangleObject` is in `PyPDF2.generic`.
- The `Resources`, `Scripts`, and `Tests` will no longer be part of the distribution
  files on PyPI. This should have little to no impact on most people. The
  `Tests` are renamed to `tests`, the `Resources` are renamed to `resources`.
  Both are still in the git repository. The `Scripts` are now in
  [cpdf](https://github.com/py-pdf/cpdf). `Sample_Code` was moved to the `docs`.

For a full list of deprecated functions, please see the changelog of version
1.28.0.

### New Features (ENH)
-  Improve space setting for text extraction (#922)
-  Allow setting the decryption password in `PdfReader.__init__` (#920)
-  Add Page.add_transformation (#883)

### Bug Fixes (BUG)
-  Fix error adding transformation to page without /Contents (#908)

### Robustness (ROB)
-  Cope with invalid length in streams (#861)

### Documentation (DOC)
-  Fix style of 1.25 and 1.27 patch notes (#927)
-  Transformation (#907)

### Developer Experience (DEV)
-  Create flake8 config file (#916)
-  Use relative imports (#875)

### Maintenance (MAINT)
-  Use Python 3.6 language features (#849)
-  Add wrapper function for PendingDeprecationWarnings (#928)
-  Use new PEP8 compliant names (#884)
-  Explicitly represent transformation matrix (#878)
-  Inline PAGE_RANGE_HELP string (#874)
-  Remove unnecessary generics imports (#873)
-  Remove star imports (#865)
-  merger.py ➔ _merger.py (#864)
-  Type annotations for all functions/methods (#854)
-  Add initial type support with mypy (#853)

### Testing (TST)
-  Regression test for xmp_metadata converter (#923)
-  Checkout submodule sample-files for benchmark
-  Add text extracting performance benchmark
-  Use new PyPDF2 API in benchmark (#902)
-  Make test suite fail for uncaught warnings (#892)
-  Remove -OO testrun from CI (#901)
-  Improve tests for convert_to_int (#899)

[Full Changelog](https://github.com/py-pdf/PyPDF2/compare/1.28.4...2.0.0)

## PyPDF2 1.X

See [CHANGELOG PyPDF2 1.X](changelog-v1.md)
