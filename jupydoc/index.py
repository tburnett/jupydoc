
from . import DocPublisher, indexer

__docs__=['DocIndex']

class DocIndex(DocPublisher):
    """

    title: |
            Document Index

    abstract: |
            This is a base class, or and example for an optional **index** document, meant to provide a top-level guide to the related 
            documents in this folder. To be an index, the document name must be "Index".

    """

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

 