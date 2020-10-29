import pandas as pd
from . import DocPublisher, indexer

__docs__=['Index']

class Index(DocPublisher):
    """

    title: |
            Document Index

    abstract: |
            This is an **index** document, meant to provide a top-level guide to the related 
            documents in this folder.

    """

    def __init__(self, **kwargs):        
        super().__init__(**kwargs)
        # this makes it an index for the docpath folder (expect the class to be named 'Index')
        self.docname='' 

    def title_page(self):
        """        
        <h2> {title}</h2> 
       
        {abstract}

        {index_table}

        """
        title = self.doc_info.get('title', '')
        abstract = self.doc_info.get('abstract', '')

        index_table = indexer.DocIndex(self)._repr_html_()
                
        self.publishme()

      
