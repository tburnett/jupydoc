
from . import DocPublisher, indexer

__docs__=['DocIndex']

class DocIndex(DocPublisher):
    """

    title: |
            Document Index

    abstract: |
            This is a special, optional **index** document, meant to provide a top-level guide to the related 
            documents in this folder. To be an index, the constructor must set the docname to "".

    index: true
    """

    def __init__(self, **kwargs):        
        super().__init__(**kwargs)
        # this makes it an index for the docpath folder (expect the class to be named 'Index')
        self.docname='' 

    def title_page(self):
        """        
        <h2> {title}</h2> 
       
        {author_line}

        {abstract}

        {index_table}

        """
        ti = self.doc_info # has title, etc.
        title = ti.get('title', '')
        abstract = ti.get('abstract', '')

        author=  ti.get('author', '').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')
        author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
        index_table = indexer.DocIndex(self)._repr_html_()
                
        self.publishme()

      
