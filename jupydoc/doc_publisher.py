"""
local enhancement of jupydoc
"""
import os
import jupydoc
#import matplotlib.pylab as plt

from .indexer import DocIndex, get_docs_info

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
        
        # where documents  will be stored, from spec in our module
        self.docpath = os.path.join(get_docs_info()['docspath'], name)
        os.makedirs(self.docpath, exist_ok=True)
        
        # reset the replacer instantiated by base 'class'
        folders = [self.docpath]
        if not self._no_display:
            # so figures or images will go into local foder
            folders.append('.')
        self.object_replacer.set_folders(folders)
            
        self.info.update(docname=name, filename=filename)
        
    def setup_save(self):        
        indexer = DocIndex(self.docpath)
        #  update the entry in the index
        t = dict()
        docname = self.info.get('docname', None)
        assert docname is not None,f'No name?: {self.info}'
        t[docname] = dict(
                title=self.title_info['title'], 
                date=self.date, 
                author=self.title_info['author'],
                info=self.info,
            )
        # 
        indexer.update(t)
        return indexer
        
    def save(self):
        # overide the file save to update the entry in the index
        self.indexer = indexer = self.setup_save()
        indexer.to_html()
        indexer.save()        
        super().save()
