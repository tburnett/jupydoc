"""
local enhancement of jupydoc
"""
import os
import jupydoc
#import matplotlib.pylab as plt

from .indexer import DocIndex#, get_docs_info
from .doc_manager import docman_instance as docman

class DocPublisher(jupydoc.Publisher):
    """title: Derived publisher for local use
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # define the output folder name
        if not hasattr(self, 'info'):
            # add something here?
            self.info = {}
        import inspect
        stack = inspect.stack()
        filename = stack[1].filename
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
            print(f'No document path defined')
            return
        indexer = self.setup_save()
        if not indexer: return
        self.indexer = indexer 
        indexer.to_html()
        indexer.save()        
        super().save()
