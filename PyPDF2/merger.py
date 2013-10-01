# vim: sw=4:expandtab:foldmethod=marker
#
# Copyright (c) 2006, Mathieu Fenniak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from generic import *
from pdf import PdfFileReader, PdfFileWriter
from StringIO import StringIO

class _MergedPage(object):
    """
    _MergedPage is used internally by PdfFileMerger to collect necessary information on each page that is being merged.
    """
    def __init__(self, pagedata, src, id):
        self.src = src
        self.pagedata = pagedata
        self.out_pagedata = None
        self.id = id
        
class PdfFileMerger(object):
    """
    PdfFileMerger merges multiple PDFs into a single PDF. It can concatenate, 
    slice, insert, or any combination of the above.
    
    See the functions "merge" (or "append") and "write" (or "overwrite") for
    usage information.
    """
    
    def __init__(self, strict=True):
        """
        >>> PdfFileMerger()
        
        Initializes a PdfFileMerger, no parameters required
        """
        self.inputs = []
        self.pages = []
        self.output = PdfFileWriter()
        self.bookmarks = []
        self.named_dests = []
        self.id_count = 0
        self.strict = strict
        
    def merge(self, position, fileobj, bookmark=None, pages=None, import_bookmarks=True):
        """
        >>> merge(position, file, bookmark=None, pages=None, import_bookmarks=True)
        
        Merges the pages from the source document specified by "file" into the output
        file at the page number specified by "position".
        
        Optionally, you may specify a bookmark to be applied at the beginning of the 
        included file by supplying the text of the bookmark in the "bookmark" parameter.
        
        You may prevent the source document's bookmarks from being imported by
        specifying "import_bookmarks" as False.
        
        You may also use the "pages" parameter to merge only the specified range of 
        pages from the source document into the output document.
        """
        
        # This parameter is passed to self.inputs.append and means
        # that the stream used was created in this method.
        my_file = False
        
        # If the fileobj parameter is a string, assume it is a path
        # and create a file object at that location. If it is a file,
        # copy the file's contents into a StringIO stream object; if 
        # it is a PdfFileReader, copy that reader's stream into a 
        # StringIO stream.
        # If fileobj is none of the above types, it is not modified
        if type(fileobj) in (str, unicode):
            fileobj = file(fileobj, 'rb')
            my_file = True
        elif type(fileobj) == file:
            fileobj.seek(0)
            filecontent = fileobj.read()
            fileobj = StringIO(filecontent)
            my_file = True
        elif type(fileobj) == PdfFileReader:
            orig_tell = fileobj.stream.tell()   
            fileobj.stream.seek(0)
            filecontent = StringIO(fileobj.stream.read())
            fileobj.stream.seek(orig_tell) # reset the stream to its original location
            fileobj = filecontent
            my_file = True
            
        # Create a new PdfFileReader instance using the stream
        # (either file or StringIO) created above
        pdfr = PdfFileReader(fileobj, strict=self.strict)
        
        # Find the range of pages to merge
        if pages == None:
            pages = (0, pdfr.getNumPages())
        elif type(pages) in (int, float, str, unicode):
            raise TypeError('"pages" must be a tuple of (start, end)')
        
        srcpages = []
        if bookmark:
            bookmark = Bookmark(TextStringObject(bookmark), NumberObject(self.id_count), NameObject('/Fit'))
        
        outline = []
        if import_bookmarks:
            outline = pdfr.getOutlines()
            outline = self._trim_outline(pdfr, outline, pages)
        
        if bookmark:
            self.bookmarks += [bookmark, outline]
        else:
            self.bookmarks += outline
        
        dests = pdfr.namedDestinations
        dests = self._trim_dests(pdfr, dests, pages)
        self.named_dests += dests
        
        # Gather all the pages that are going to be merged
        for i in range(*pages):
            pg = pdfr.getPage(i)
            
            id = self.id_count
            self.id_count += 1
            
            mp = _MergedPage(pg, pdfr, id)
            
            srcpages.append(mp)

        self._associate_dests_to_pages(srcpages)
        self._associate_bookmarks_to_pages(srcpages)
            
        
        # Slice to insert the pages at the specified position
        self.pages[position:position] = srcpages
        
        # Keep track of our input files so we can close them later
        self.inputs.append((fileobj, pdfr, my_file))
        
        
    def append(self, fileobj, bookmark=None, pages=None, import_bookmarks=True):
        """
        >>> append(file, bookmark=None, pages=None, import_bookmarks=True):
        
        Identical to the "merge" function, but assumes you want to concatenate all pages
        onto the end of the file instead of specifying a position.
        """
        
        self.merge(len(self.pages), fileobj, bookmark, pages, import_bookmarks)
        
    
    def write(self, fileobj):
        """
        >>> write(file)
        
        Writes all data that has been merged to "file" (which can be a filename or any
        kind of file-like object)
        """
        my_file = False
        if type(fileobj) in (str, unicode):
            fileobj = file(fileobj, 'wb')
            my_file = True


        # Add pages to the PdfFileWriter
        # The commented out line below was replaced with the two lines below it to allow PdfFileMerger to work with PyPdf 1.13
        for page in self.pages:
            self.output.addPage(page.pagedata)
            page.out_pagedata = self.output.getReference(self.output._pages.getObject()["/Kids"][-1].getObject())
            #idnum = self.output._objects.index(self.output._pages.getObject()["/Kids"][-1].getObject()) + 1
            #page.out_pagedata = IndirectObject(idnum, 0, self.output)

        # Once all pages are added, create bookmarks to point at those pages
        self._write_dests()
        self._write_bookmarks()
        
        # Write the output to the file   
        self.output.write(fileobj)
        
        if my_file:
            fileobj.close()


        
    def close(self):
        """
        >>> close()
        
        Shuts all file descriptors (input and output) and clears all memory usage
        """
        self.pages = []
        for fo, pdfr, mine in self.inputs:
            if mine:
                fo.close()
        
        self.inputs = []
        self.output = None

    def addMetadata(self, infos):
        """See addMetadata method in PdfFileWriter class"""
        self.output.addMetadata(infos)
    
    def setPageLayout(self, layout):
        """See setPageLayout() methods in pdf.py"""
        self.output.setPageLayout(layout)

    def setPageMode(self, mode):
        """See setPageMode() methods in pdf.py"""
        self.output.setPageMode(mode)

    def _trim_dests(self, pdf, dests, pages):
        """
        Removes any named destinations that are not a part of the specified page set
        """
        new_dests = []
        prev_header_added = True
        for k, o in dests.items():
            for j in range(*pages):
                if pdf.getPage(j).getObject() == o['/Page'].getObject():
                    o[NameObject('/Page')] = o['/Page'].getObject()
                    assert str(k) == str(o['/Title'])
                    new_dests.append(o)
                    break
        return new_dests
    
    def _trim_outline(self, pdf, outline, pages):
        """
        Removes any outline/bookmark entries that are not a part of the specified page set
        """
        new_outline = []
        prev_header_added = True
        for i, o in enumerate(outline):
            if type(o) == list:
                sub = self._trim_outline(pdf, o, pages)
                if sub:
                    if not prev_header_added:
                        new_outline.append(outline[i-1])
                    new_outline.append(sub)
            else:
                prev_header_added = False
                for j in range(*pages):
                    if pdf.getPage(j).getObject() == o['/Page'].getObject():
                        o[NameObject('/Page')] = o['/Page'].getObject()
                        new_outline.append(o)
                        prev_header_added = True
                        break
        return new_outline
   
    def _write_dests(self):
        dests = self.named_dests
        
        for v in dests:
            pageno = None
            pdf = None
            if v.has_key('/Page'):
                for i, p in enumerate(self.pages):
                    if p.id == v['/Page']:
                        v[NameObject('/Page')] = p.out_pagedata
                        pageno = i
                        pdf = p.src
                        break
            if pageno != None:
                self.output.addNamedDestinationObject(v)
 
    def _write_bookmarks(self, bookmarks=None, parent=None):
        
        if bookmarks == None:
            bookmarks = self.bookmarks
        

        last_added = None
        for b in bookmarks:
            if type(b) == list:
                self._write_bookmarks(b, last_added)
                continue
                
            pageno = None
            pdf = None
            if b.has_key('/Page'):
                for i, p in enumerate(self.pages):
                    if p.id == b['/Page']:
                        #b[NameObject('/Page')] = p.out_pagedata
                        args = [NumberObject(p.id), NameObject(b['/Type'])]
                        #nothing more to add
                        #if b['/Type'] == '/Fit' or b['/Type'] == '/FitB'
                        if b['/Type'] == '/FitH' or b['/Type'] == '/FitBH':
                            if b.has_key('/Top') and not isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Top']
                        elif b['/Type'] == '/FitV' or b['/Type'] == '/FitBV':
                            if b.has_key('/Left') and not isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Left']
                        elif b['/Type'] == '/XYZ':
                            if b.has_key('/Left') and not isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            if b.has_key('/Top') and not isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            if b.has_key('/Zoom') and not isinstance(b['/Zoom'], NullObject):
                                args.append(FloatObject(b['/Zoom']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Top'], b['/Zoom'], b['/Left']
                        elif b['/Type'] == '/FitR':
                            if b.has_key('/Left') and not isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            if b.has_key('/Bottom') and not isinstance(b['/Bottom'], NullObject):
                                args.append(FloatObject(b['/Bottom']))
                            else:
                                args.append(FloatObject(0))
                            if b.has_key('/Right') and not isinstance(b['/Right'], NullObject):
                                args.append(FloatObject(b['/Right']))
                            else:
                                args.append(FloatObject(0))
                            if b.has_key('/Top') and not isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Left'], b['/Right'], b['/Bottom'], b['/Top']

                        b[NameObject('/A')] = DictionaryObject({NameObject('/S'): NameObject('/GoTo'), NameObject('/D'): ArrayObject(args)})
                       
                        pageno = i
                        pdf = p.src
                        break
            if pageno != None:
                del b['/Page'], b['/Type']
                last_added = self.output.addBookmarkDict(b, parent)    

    def _associate_dests_to_pages(self, pages):
        for nd in self.named_dests:
            pageno = None
            np = nd['/Page']
            
            if type(np) == NumberObject:
                continue
            
            for p in pages:
                if np.getObject() == p.pagedata.getObject():
                    pageno = p.id
            
            if pageno != None:
                nd[NameObject('/Page')] = NumberObject(pageno)
            else:
                raise ValueError, "Unresolved named destination '%s'" % (nd['/Title'],)
    
    def _associate_bookmarks_to_pages(self, pages, bookmarks=None):
        if bookmarks == None:
            bookmarks = self.bookmarks

        for b in bookmarks:
            if type(b) == list:
                self._associate_bookmarks_to_pages(pages, b)
                continue
                
            pageno = None
            bp = b['/Page']
            
            if type(bp) == NumberObject:
                continue
                
            for p in pages:
                if bp.getObject() == p.pagedata.getObject():
                    pageno = p.id
            
            if pageno != None:
                b[NameObject('/Page')] = NumberObject(pageno)
            else:
                raise ValueError, "Unresolved bookmark '%s'" % (b['/Title'],)
                
    def findBookmark(self, bookmark, root=None):
    	if root == None:
    		root = self.bookmarks
    	
    	for i, b in enumerate(root):
    		if type(b) == list:
    			res = self.findBookmark(bookmark, b)
    			if res:
    				return [i] + res
    		if b == bookmark or b['/Title'] == bookmark:
    			return [i]
    
    	return None

    def addBookmark(self, title, pagenum, parent=None):
        """
        Add a bookmark to the pdf, using the specified title and pointing at 
        the specified page number. A parent can be specified to make this a
        nested bookmark below the parent.
        """

        if parent == None:
        	iloc = [len(self.bookmarks)-1]
        elif type(parent) == list:
        	iloc = parent
        else:
        	iloc = self.findBookmark(parent)
        
        dest = Bookmark(TextStringObject(title), NumberObject(pagenum), NameObject('/FitH'), NumberObject(826))
        
        if parent == None:
        	self.bookmarks.append(dest)
        else:
        	bmparent = self.bookmarks
        	for i in iloc[:-1]:
        		bmparent = bmparent[i]
        	npos = iloc[-1]+1
        	if npos < len(bmparent) and type(bmparent[npos]) == list:
        		bmparent[npos].append(dest)
        	else:
        		bmparent.insert(npos, [dest])
        		
        
    def addNamedDestination(self, title, pagenum):
        """
        Add a destination to the pdf, using the specified title and pointing
        at the specified page number.
        """
        
        dest = Destination(TextStringObject(title), NumberObject(pagenum), NameObject('/FitH'), NumberObject(826))
        self.named_dests.append(dest)


class OutlinesObject(list):
    def __init__(self, pdf, tree, parent=None):
        list.__init__(self)
        self.tree = tree
        self.pdf = pdf
        self.parent = parent
    
    def remove(self, index):
        obj = self[index]
        del self[index]
        self.tree.removeChild(obj)
        
    def add(self, title, page):
        pageRef = self.pdf.getObject(self.pdf._pages)['/Kids'][pagenum]
        action = DictionaryObject()
        action.update({
            NameObject('/D') : ArrayObject([pageRef, NameObject('/FitH'), NumberObject(826)]),
            NameObject('/S') : NameObject('/GoTo')
        })
        actionRef = self.pdf._addObject(action)
        bookmark = TreeObject()

        bookmark.update({
            NameObject('/A') : actionRef,
            NameObject('/Title') : createStringObject(title),
        })

        pdf._addObject(bookmark)

        self.tree.addChild(bookmark)
        
    def removeAll(self):
        for child in [x for x in self.tree.children()]:
            self.tree.removeChild(child)
            self.pop()
