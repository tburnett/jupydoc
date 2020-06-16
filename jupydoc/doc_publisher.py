"""
Document creation 
"""
import os
import jupydoc
import yaml

from .indexer import DocIndex
from .helpers import doc_formatter, DocInfo
from .doc_manager import docman_instance as docman


class DocPublisher(jupydoc.Publisher):
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
                **kwargs):
        super().__init__(**kwargs)

        # get the required docstring            
        
        docstring = self.__doc__ 
        if not docstring:
            raise Exception('a docstring is required')
        try:
            doc_dict = yaml.safe_load(docstring) 
        except Exception as e:
            print(f'yaml error: {e.__class__.__name__}: {e.args}\n{docstring}')
            raise

        self.doc_info = DocInfo(doc_dict)
        self._no_display = no_display
        self.display_on = not no_display # user can set
    
        self.clear()
        # define the output folder name
        if not hasattr(self, 'info'):
            # add something here?
            self.info = {}
        import inspect
        stack = inspect.stack()
        filename = stack[1].filename
        if filename.startswith('<ipython-input'):
            module_name=''
            filename='(interactive)'
        else:
            module_name = filename.split('/')[-2]
        name = module_name +'.'+ self.__class__.__name__  
        self.info.update(docname=name, filename=filename)
        
        docspath = kwargs.pop('docman_docspath', '') # set in DocMan
        if docspath: self.set_doc_folders(docspath)
        
    def set_doc_folders(self,
                    docspath:'Abs path to the folder where this doc will be saved'):
        # where documents  will be stored, from spec in our module
        
        self.docpath = os.path.abspath(os.path.join(docspath, self.info['docname']))
        os.makedirs(self.docpath, exist_ok=True)

        # reset the replacer instantiated by base 'class'
        folders = [self.docpath]
        if not self._no_display:
            # so figures or images will go into local foder
            folders.append('.')
        self.doc_folders = folders
        self.object_replacer.set_folders(folders)

    def title_page(self):
        """
        <a id="title_page"> <h1>{title}</h1> </a>
        <h2>{subtitle}</h2>
        {date_line} 
        {author_line}
       
        {abstract}
        """

        #ti = self._title_info
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

    def __call__(self, examine=None, 
            display_only:'set to only use the display'=False,
            ):
        """assemble and save the document if docpath is set
        Choose a range of sections to display in the notebook
        """
        self.clear()
        
        # the DocInfo object implements an iterator, and detects selection for display
        self.doc_info.set_selection(examine)

        for sid, function, selected in self.doc_info:
            if not hasattr(self, function):
                raise Exception(f'Function {function} not defined')
            self._current_index = [int(sid), int(sid*10%10)]
            self.display_on = selected
            # try:
            #     eval(f'self.{function}()')
            # except Exception as e:
            #     print(f'Function {function} Failed: {e}')
            # TODO: sensible reaction here--info for user function
            eval(f'self.{function}()')
            
        if not display_only:
            self.save()

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
            hchars ='##'
            hnumber=f'{section_number:}'
               
            # for subsections, if any
            self._saved_symbols = vars
        else: 
            # a subsection
            hchars = '###'
            # maybe make numbering optional?
            hnumber=f'{section_number:}.{subsection_number}'
             # add the locals and kwargs to section symbol list
            vars.update(self._saved_symbols)

        # prepend section or subsection header if requested and not the title page
        header = f'\n\n{hchars} {hnumber} {section_title}\n\n' if section_title else ''   
                        
        doc = self.doc_info.section_header + header + doc
        return doc

    def setup_save(self):        

        indexer = DocIndex(self.docpath)
        #  update the entry in the index
        t = dict()
        docname = self.info.get('docname', None)
        if None:
            print(f'No name for the document?: {self.info}')
            return
        # title = self._title_info['title'].split('\n')[0]
        title = self.doc_info['title'].split('\n')[0]
        t[docname] = dict(
                title=title, 
                date=self.date, 
                author=self.doc_info['author'],
                info=self.info,
            )
        # 
        indexer.update(t)
        return indexer
        
    def save(self):
        # overide the file save to update the entry in the index
        if not self.docpath:
            print(f'(Not saved --no document path was defined)')
            return
        indexer = self.setup_save()
        if not indexer: return
        self.indexer = indexer 
        indexer.to_html()
        indexer.save()        
        super().save()
