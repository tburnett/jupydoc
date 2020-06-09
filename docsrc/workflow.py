"""
"""
import os
import numpy as np
import pylab as plt
import pandas as pd

from jupydoc import DocPublisher
__docs__ = ['MultipleDocs', 'Workflow']

class MultipleDocs(DocPublisher):
    """
    title: Jupydoc Support for  Multiple Documents 
    author: Toby Burnett
    sections: 
        title_page setup usage code_development 
        
    abstract: I Discuss the design that extends the basic 
        jupydoc, and how it manages multiple documents.
        
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def setup(self):
        """Setup
        
        The basic Jupydoc makes it easy to create documents in the JupyterLab environmant
        perhaps combined with code development or analysis.
        This describes additional support to manage and index multiple documents, both the source files
        and the output documents.
                      
        The user iterface is very straightforward. Here is the contents
        of a JupyterLab notebook, a single cell:
        ```
        from jupydoc import DocMan
        dm = DocMan('docsrc')
        dm
        ```
        The first line imports the Jupydoc document manager <samp>DocMan</samp>. The second
        instantiates it with the name of the package, or folder containing source documents. 
        It must be in the Python path, or have been already loaded. 
        The last line generates a summary of the file structure
        and available document classes: 
        ```
        
            Modules                         Classes
             docsrc.jupydoc_doc             ['JupyDoc']
             docsrc.workflow                ['DocsDesign', 'Workflow']
        ```
        This is a list of the python module names that have been imported to discover
        their declared class names.
        The package containing these files has of necessity an `__init__.py`. It must declare
        a variable "docspath" to associate another folder with the output. In this case it is
        ```
        docspath = '../docs'
        ```
        So the generated documents are in the same folder as this package.

        The source file needs to declare class(es) that it contains. For the present one has
        the lines:
        ```
        from jupydoc import DocPublisher
        __docs__ = ['DocsDesign', 'Workflow']   
        ```
        
        Finally, a document class needs to have the following structure:
        ```
        class MyDoc(DocPublisher):
            '''
            title: My Document
            author: me
            sections: 
                title_page introduction first_section second_section 
            '''
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
        ```
        To support the document structure, the class docstring, which is in 
        [yaml](https://en.wikipedia.org/wiki/YAML),
        is used to define document properties.
        {linkto_top}
        """
        

        #-------------------------
        self.publishme()
        
    def usage(self):
        """Usage
        
        ### Editing and generating
        
        With the DocMan instance generated in the setup phase, the following instantiates
        a document instance "DocsDesign", makes the output HTML file, while displaying 
        a selected section, the title page in this case, in the notebook:
        ```
        self = dm('DocsDesign')
        self(0)
        ```
        
        <br>I may examine the document in the notbook window by executing `self('all')`.
        (Why "self"? Then I can test code destined for member functions in the instance
        of the Publisher superclass.)

        The options for the argument(s) to <samp>self</samp> are,
        assuming the first section is "title_page", a wired-function to display the title page are:
        * section name, e.g., "introduction" 
        * section number, where 0 is the title page, -1 the last section
        * a range (first, last) of sections. 
        
        To modify the code for a secction or its docstring, I have the file containing the class open in an editor, perhaps the one provided by JupyterLab.
        Also, I have a separate browser window to display the current version of the whole document. 
     
        Here is a screen on my 34" monitor, showing three views of this section.
        
        {screen_image}
        
        Re-creating the present document, which does no computing itself, takes 1/2 s. 
        
        Importantly, after rerunning "self=docman('DocsDesign')", the module is reloaded, with
        any compilation errors displayed.
               
        ### Web stuff
        The class DocPublisher coordinates with DocMan. As a subclass of  <samp>jupydoc.Publisher</samp>, it
        overrides the <samp>save</samp> function to:
        1. Instantiate the class <samp>DocIndex</samp>. The instance is a dict containing all 
        docments that it is   managing
        2. Provides access to the document information, as specified in its yaml-format docstring, 
        and update the  entry for the current document. The dictionary key is, 
        e.g. "jupydocs.DocDesign" the name  assigned to this document.
        3. Save the index state, in yaml, to <samp>index.yaml</samp>. 
        4. Rewrite the file <samp>index.html</samp> for lookup Web access.
        5. Finally call the base class's <samp>save</samp> method to save the document 
        in the same folder.
        
        The presence of the file <samp>index.html</samp> means that the folder can be opened
        in a browser. 
        Here is what the index looks like:
        
        {index_image}
         {linkto_top}
        """
        screen_image= self.image("$HOME/images/jupydoc-screen.png", caption='')
        index_image = self.image("$HOME/images/jupydoc-index.png", caption='')
        #--------------------------------------------------------------------
        self.publishme()
        
    def code_development(self):
        """Code Development
        
        This section discusses the organization of code beyond beyond that to define documents. 
        This should  be the location of important computation code&mdash; that should be elsewhere,
        and invoked from here.
        Detailed figure-generating code could be external, where it could be shared by
        different section functions.
        {linkto_top}
        """
        self.publishme()
        
    def future_tasks(self):
        """Future tasks
        
        A TODO list:
        
        * Add anchors and generate a table of contents with links to the sections.
        * Perhaps make the package nesting flexible, beyond the two present levels.
        * (new items as they occur to me as the first user)
        
        {linkto_top}
        """
        self.publishme()
        
class Workflow(DocPublisher):
    pass