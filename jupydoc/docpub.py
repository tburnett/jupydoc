"""
Document creation 
"""
import os, sys
import jupydoc
import yaml

from .helpers import DocInfo
from .publisher import Publisher

class DocPublisher(Publisher):
    """
    title: |
            `DocPublisher`: Derived from `jupydoc.Publisher` to support structured documents
            Also, with `jupydoc.DocMan`, supports multiple documents 

    author: Toby Burnett
    sections: test_section

    abstract:  This class is meant to be subclassed to create documents using the
        python-function document creation capability of [`jupydoc`](https://github.com/tburnett/jupydoc).
        See this [detailed document](https://tburnett.github.io/docsrc.JupyDoc) produced using this class, explaining the ideas and usage. 
    """
    def __init__(self,  
                no_display:'set True to disable IPython display output'=False, 
                doc_dict:'Alternative to parsing docstring'={},
                client_mode:'Set for client mode'=False,
                **kwargs):

        super().__init__(**kwargs)

        # get the required docstring or alternate doc_dict           
        if not doc_dict:
            docstring = self.__doc__ 
            if not docstring:
                print('DocPublisher: a docstring or doc_dict arg is required', file=sys.stderr)
                return
            try:
                doc_dict = yaml.safe_load(docstring) 
            except Exception as e:
                print(f'yaml error: {e.__class__.__name__}: {e.args}\n{docstring}',file=sys.stderr)
                return               

        self.doc_info = DocInfo(doc_dict)
        self.doc_info['date'] = self.date
        self.doc_info['version'] = getattr(self, 'version', '')

        self._no_display = no_display
        self.display_on = not no_display # user can set
        self.client_mode = client_mode

        # make non-doc items available as attribues and in self.info
        info = doc_dict
        for k in 'title author sections'.split(): info.pop(k, None)
        if info: self.__dict__.update(info)
        self.info = info    
        self.clear()

    def __str__(self):
        r = self.doc_info.get('title', '').split('\n')[0]+'\n'
        for sid, sname, _ in self.doc_info:
            if sid==0: continue
            sid = str(sid).replace('.0', "")
            r += f'{sid}    {sname}\n'
        if self.docpath:
            r += f' -> {os.path.join(self.docpath, self.docname)}'
        return r

    def __repr__(self): return str(self)
    
    def title_page(self):
        """
        <a id="title_page"> <h1>{title}</h1> </a>
        <h2>{subtitle}</h2>
        {date_line} 
        {author_line}
       
        {abstract}
        """

        ti = self.doc_info # has title, etc.
        ts=self.doc_info['title'].split('\n')
        title=ts[0]
        subtitle = '' if len(ts)==1 else ' '.join(ts[1:])
        author=  ti.get('author', '').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')
        abstract=ti.get('abstract', '')
        author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
        date_line=f'<p style="text-align: right;">{self.date}</p>'
        self.publishme()

    def test_section(self):
        """Test Section

        This function is `test_section`, found in `self.doc_info.names`: 
        {indent}     {self.doc_info.names}    {endp}
        """
        self.publishme()

    def __call__(self, 
            examine:'"all" | section number | subsection number'=None, 
            save_ok:'will also save the doc if set'=True,
            client_mode:'Set True in this case'=False,
            quiet:'Set to avoid printing a line per section'='False',
            ):
        """assemble and save the document if docpath is set        
        """
        self.clear()
        
        # the DocInfo object implements an iterator, and detects selection for display
        self.doc_info.set_selection(examine)

        ok = True
        for sid, function, selected in self.doc_info:
            if not hasattr(self, function):
                raise Exception(f'Function {function} not defined')
                ok=False
                continue
            self._current_index = [int(sid), int(sid*10%10)]
            self.display_on = selected and not self.client_mode
            try:
                fail = eval(f'self.{function}()')
                if fail:
                    print(f"function '{function}' failure message: {fail}", file=sys.stderr)
                    return

            except Exception as e:
                import traceback
                print(f"Function '{function}' Failed: {e}", file=sys.stderr)
                tb = e.__traceback__
                traceback.print_tb(tb, limit=-1)
                ok=False

            if not selected and not self.client_mode:
                print(f'{sid:5} {function}')
 

        if ok and save_ok:
            # update the document index if instantiated by DocMan 
            if hasattr(self, 'docman'):
                self.docman.update(self)
            self.save(quiet=self.client_mode)

    def process_doc(self, doc, vars):
        """Override the base class to add document features to the output of a doc function
        * headers with (sub)section numbers
        * make section symbols available to subsections
        """

        section_number, subsection_number = self._current_index

        if section_number>0:
            doc_lines = doc.split('\n')

            if len(doc_lines)==0: 
                print(f'Warning: section {self.name} has no docstring')
                return doc
            first = 0 if  doc_lines[0] else 1
            section_title = doc_lines[0]
            if len(doc_lines)>1:            
                doc = '\n'.join(doc_lines[first+2:])
        else: self.section_title = ''
        
        if section_number==0:
            # flag for title page
            section_title = ''
        
        elif  subsection_number==0:
            # a new non-title section
            hnumber=f'{section_number:}.'
               
            # for subsections, if any
            self._saved_symbols = vars
        else: 
            # a subsection
            # maybe make numbering optional?
            hnumber=f'{section_number:}.{subsection_number}'
             # add the locals and kwargs to section symbol list
            vars.update(self._saved_symbols)

        # prepend section or subsection header if requested and not the title page
        header = f'{hnumber} {section_title}' if section_title else ''   

        # puths in anchors and links, maybe colappse                
        doc = self.doc_info.annotate(header, doc)
        # doc = self.doc_info.section_header + header + doc + self.doc_info.section_trailer
        return doc

