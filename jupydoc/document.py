"""
Generate illustrative document
"""
import numpy as np
import pylab as plt
import pandas as pd
import os, sys
from jupydoc import Publisher

class Document(Publisher):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    def introduction(self):
        """
        ### Purpose
        This package addresses a long-term frustration I've had with using Jupyterlab for my
        analysis. That is, how do I combine the output of a notebook, entries in my logbook, and
        the python code to produce a document to present to collaborators, or translate to an actual 
        publishable document? And finally, how to maintain some sort of version control with inputs to such
        a document from several sources? Jupyter notebooks are tempting since they have markdown cells that
        provide for nice formatting, even including LaTex. And of course the figures are nicely 
        inserted in the output. But I wanted to have the text reflect the calcualations, that is,
        be as dynamic as the generation of figures. And I certainly want the appearance of the
        notebook to reflect the appearance of any final document. 
        
        Some important features of the jupyter environment that are essential:

        * IPython.display is very flexible for generating formatted output following a code cell. 
        Especially, it interprets markdown text in the same way as for markdown cells. Thus why not 
        generate markdown text as a part of the processing that produces figures?

        * The "docstring" of a python function is easily accessible to via Python's inspection.

        * The `str.format` function that replaces curly-bracketed fields in a string with representations
        of expressions in curly brackets. That is used here with the `locals()` dictionary as an argument.

        * The related package nbconvert which supports creation of an HTML document from a notebook,
        in this case the Juptyer version of markdown. It is necessary to produce an idential-looking (almost)
        document to what is rendered in the notebook.
        
        Thus one can use this to document a function that does some calculation, generating various figures,
        with that function's docstring. A further evolution of this idea was to have the function reflect
        a *section* of the final document. And to encapsulate the whole thing into a Python class,
        inheriting from a class that handles all the details. This completely addresses my frustration
        in that the code for such a class is all I need to procuce a nice document.
        
        It is no longer necessary to maintain separate notebook files&mdash;but Jupyter/IPython is not only
        crutial for producing the document, but the Jupyter environment is essential for developing the
        analysis and generating the associated documentation. The modular section-oriented structure
        allows invoking each function independently, with the resulting document section displayed
        immediatly following the code cell. 
        
        ### About this document
        This document is itself a demonstration! It was generated using member functions
        of the class `jupydoc.Document`, which inherits from `jupydoc.Publisher`.
        Each such function represents a section in the document.
        
        """
        self.publishme('Introduction')
        
    def formatting_summary(self):
        r"""
        There are three elements in such a function: the docstring, written in 
        markdown, containing 
        local names in curly-brackets, the code, and a final call `self.publishme(section_name)`.  
        Unlike a formatted string, entries in curly brackets cannot be expressions.
        
        #### Local variables  
        Any variable, say from an expression in the code `q=1/3`, can be interpreted
        with `"q={{q:.3f}}"`, resulting in  
        q={q:.3f}.    
        
        #### Figures
        
        Any number of Matplotlib Figure objects can be added, with unique numbers.
        An entry "{{fig1}}", along with code that defines `fig1` like this:
        ```
        x = np.linspace(0,10)
        fig1,ax=plt.subplots(num=self.newfignum(), figsize=(4,3))
        ax.plot(x, x**2)
        ax.set(xlabel='$x$', ylabel='$x^2$', title=f'figure {{fig1.number}}')
        fig1.caption='''Caption for Fig. {fig1.number}, which
                shows $x^2$ vs. $x$.'''
        ```
        produces:
        
        {fig1}
        
        The display processing replaces the `fig1` reference in a copy of `locals()`
        with a object that implements a `__str__()` function returning an HTML reference 
        to a saved png representation of the figure.   
        Note the convenience of defining a caption by adding the text as an attribute of
        the Figure object.  
        Also, the `self.newfignum()` returns a new figure number. Its number can be referred to
        in the text as `{{fig1.number}}`.
    
        
        #### DataFrames
        A `pandas.DataFrame` object is treated similarly. 
        
        The code
        ```
        df = pd.DataFrame.from_dict(dict(x=x, xx=x**2)).T
        
        ```
        
        <br>Results in "{{df}}" being replaced with
        {df}
    
        #### LaTex 
        Jupyter-style markdown can contain LaTex expressions. For this, it is 
        necessary that the docstring be preceded by an "r". So,
        ```
        \begin{{align*}}
        \sin^2\theta + \cos^2\theta =1
        \end{{align*}}
        ```
        
        <br>Results in:   
            \begin{align*}
            \sin^2\theta + \cos^2\theta =1
            \end{align*}
        
        ---
        The capability shown here for the Figure and DataFrame objects could be easily extended to other
        classes. For user objects it only necessary to define a `__str__` function to the class.
        """
        q = 1/3
        xlim=(0,10)
        plt.rc('font', size=14)
        x=np.linspace(*xlim)
        df= pd.DataFrame([x,x**2,np.sqrt(x)], index='x xx sqrtx'.split()).T
        dfhead =df.head(2)

        fig1,ax=plt.subplots(num=self.newfignum(), figsize=(4,3))
        ax.plot(x, x**2)
        ax.set(xlabel='$x$', ylabel='$x^2$', title=f'figure {fig1.number}')
        fig1.caption="""Caption for Fig. {fig1.number}, which
                shows $x^2$ vs. $x$.    
               ."""
        
        df = pd.DataFrame.from_dict(dict(x=x, xx=x**2))
        dfhead = df.head()
        
        self.publishme('Docstring Formatting')
        
    def document_structure(self):
        """
        ### Title page
        The document has an optional title page containing the title, a date, 
        and perhaps other text. This is managed by setting the dictionary `self.title_info` with
        keys "title", "author" perhaps "subtitle" and "abstract".
        The page is produced with a call to `title_page`.
        
        ### Sections
        Each member function, with a docstring and call to `self.publishme(`*section_name*`)` will 
        generate a numbered section. The numbers are sequential as called by default, but can be specified
        by setting `self.section_number` in the code.
        
        ### Other text
        Text not fitting into the section structure can be added with a call to the member function
        `markdown`, providing a text string. 
        
        """
        self.publishme('Document Structure')
        
    def file_structure(self):
        """
        ## Web
        The resulting Web document has two components: the HTML file with all the text and formatting, and, in the
        same folder, a  subfolder "figs" with the figures, which are included via the HTML e.g., `<img src="figs/fig_1.png"/>`.
                
        The use case motivating this was to develop the document in Jupyter, and easiiy save it as a 
        Web document. In order for the figures to be displayed in the notebook, the figures must be 
        saved in its folder.
       
        Creating the Web document then entails creating (using nbconvert) the HTML file in the destination
        document folder, and copying the figure folder into it.
                
        ### PDF?
        Using nbconvert for this seems to fail. A better solution, in the works, is to use code that I 
        found in [`notebook-as-pdf`](https://github.com/betatim/notebook-as-pdf), which uses a headless
        chrome, relying on (`pyppeteer`)[https://pypi.org/project/pyppeteer/] to render the HTML to a PDF file.
        """
        self.publishme('File structure')
        
    def workflow(self):
        """
        This facility has transformed the way I generate analysis code. The objective is to *minimize* notebooks. 
        I now regard them as temporary, but essential, sratch pads for developing code. Such a process requires 
        creating plots showing the results, validating assumptions about the data and analysis methods. 
        So there are two coding elements in this procedure: the actual analysis, and the creation of associated plots.
        
        Thus I separate the two, with the ploting and discussion of which, put into members of a `jupydoc.Publisher` class.
        
        An interesting situation arises: How to "reuse" such member functions in a new, but related presentation analysis?
        Related to this is what goes into the Jupyter notebook, which is being used to develop analysis and its 
        associated documentation. With the goal of minimizing the notebook, my answer is multiple inheritance. 
        So I create a class only for the notebook,
        
        ```
        class LocalDoc(A,B...):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
            def new_section(self):
                '''
                <text>
                '''
                <code>
                self.publishme('New Section')
        ```
        where each of the super classes, which also inherit from ju_doc.Publisher has a similar constructor. 
        Any keywords are passed to all, presumably acted on by the one that recognizes them. All the respective 
        member functions are of course available.
        
        Finally, to produce the HTML (and eventual PDF) document, I write a function that call the relevant 
        sequence of member fuctions, followed by a self.save. For this document, that is `__call__`:
        
        ```
        from jupydoc import document
        doc=document.Document(
            title_info= dict(
                title='Producing documents in Jupyter',
                author='T. Burnett <tburnett@uw.edu>',
                ),
            doc_folder='/nfs/farm/g/glast/u/burnett/git/tburnett.github.io/jupydoc',)
        doc()
        ```
        """
        self.publishme('Workflow')
        
    def __call__(self):
        # assemble and save the document
        self.title_page()
        self.introduction()
        self.formatting_summary()
        self.document_structure()
        self.file_structure()
        self.workflow()
        self.save()
        