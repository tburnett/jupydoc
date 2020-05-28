"""
Generate illustrative document
"""
import numpy as np
import pylab as plt
import pandas as pd
import os, sys
from jupydoc import Publisher

class Document(Publisher):
    0
    def __init__(self,**kwargs):
        super().__init__(
            title_info= dict(
                title='Producing documents in Jupyter with jupydoc',
                author='T. Burnett <tburnett@uw.edu>',
                ) ,
            **kwargs
        )
                    
    def introduction(self):
        """
        ### What is it, and how does it work?
        It is lightweight, some ~400 lines of code in Python exclusive of this document, with, besides depending on
        IPython and nbconvert, non-essential dependencies on pandas, matplotlib, and numpy.   
        The key elements that explain the design and operation are:
        
        * **Code and markdown cells in a Jupyter notebook**<br>
        The origin of this package was rooted in a desire to be able to combine the nice formatting capability of
        markdown cells, with the output from the computation in a code cell. By default, any matplotlib
        figures created in its computation will automatically appear below the cell. This behavior, it turns out, can be controlled 
        by code executed in the cell. The key here is that code can create markdown text, which will be interpreted
        just as the text in a markdown cell. This includes LaTex.
         
        * **Python [inspection](https://docs.python.org/3/library/inspect.html)**<br>
        The inspection capability gives access to two important elements of a function:
         * docstring&mdash; a text string immediately following the function declaration.
         * symbol table&mdash;in python terms, a "dict" with variable names as keys, and values the actual value of the
        variables
        
        * **Python string format method**<br>
        Since python 2.6, text strings have had a "format" method, which interprets occurrences of"{{...}}", 
        replacing what it finds between the
        curly brackets with its evaluation as an expression. (With python 3, this is built into special format strings.)
        
        * **[nbconvert](https://nbconvert.readthedocs.io/en/latest/)**<br>
        This separate package supports creation of an HTML document from a notebook, specifically 
        interpreting Jupyter's version of markdown, in this case the Juptyer version of markdown. 
        It is necessary to produce an (almost) identical-looking  document to what is rendered in the notebook.
        
        ### What is it good for?
        
        * **A document like this**<br>
        This document is itself a demonstration, testing all the features it describes! It was generated using 
        member functions  of the class `jupydoc.Document`, which inherits from `jupydoc.Publisher`.
        Each such function represents a section in the document. The code that produced this document is in fact testing and 
        describing the code that produces it.
               
        * **Simple Jupyter-based analyses**<br>
        Rather than spreading output among several cells, this encourages making a coherent description, 
        including output plots, say, in the area below a single cell.
        
        * **Personal notebook**<br>
        Rather than cutting and pasting single plots to a personal notebook, this allows the clipping 
        to include many details, with LaTex formulas perhaps.
        
        * **Presentations and analysis documents**<br>
        Sharing ones analysis results with others is a small step from the personal notebook. The days of 
        needing PowerPoint to make presentations seem to be over, so the document can be the presentation medium.
        
        * **Publication?**<br>
        Well, I'd not go that far, but the evolution to such should be easy, especially if relevant LaTex
        formulae, plots with captions and relevant description have already been done.
 
        """
        self.publishme('Introduction', 1)
        
    def formatting_summary(self):
        r"""
        A member function of a class inheriting from `jupydoc.Publisher` needs to have three elements; the docstring, written in 
        markdown, containing  variable names in curly-brackets, the code, and a final call `self.publishme(section_name)`.  
        Unlike a formatted string, entries in curly brackets cannot be expressions.
        
        #### Local variables  
        Any variable, say from an expression in the code `q=1/3`, can be interpreted in the docstring
        with `"q={{q:.3f}}"`, resulting in 
        {indent}
        q={q:.3f}.        
        {endp}
        
        #### Figures
        
        Any number of Matplotlib Figure objects can be included.
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
        
        The display processing replaces the `fig1` reference in a copy of the local variable dictionary
        with a object that implements a `__str__()` function returning an HTML reference 
        to a saved png representation of the figure.   
        Note the convenience of defining a caption by adding the text as an attribute of
        the Figure object.  
        The `self.newfignum()` returns a new figure number. It is necessary to for all
        the figures in a section to be unique. But the actual number is set to be sequential for the whole document.
        It can be referred to in the text as `{{fig1.number}}`.
    
        
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
                
        The use case motivating this was to develop the document in Jupyter, and easily save it as a 
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
        #### Development
        This facility has transformed the way I generate analysis code.  
        I use notebooks only to develop the code *and* documentation. This is an incremental process, with one 
        section at a time. But the computation up to the point of adding something in a new section is perhaps 
        lengthy. Since changing code in the module requires reloading and re-executing it, it can be 
        prohibitive to edit it.
        
        An approach I'm using is to create a new module, say "dev", only for the development code, with this pattern:        
      
        ```
        from jupydoc import Publisher
        class Development(Publisher): 
            def __init__(self, *args **kwargs):
                super().__init__( **kwargs)
                ''' 
                text to summarize setup
                '''
                # setup self to correspond to needs of code here
                self.publishme('Setup')
                
            def new_section(self):
                '''
                <text>
                '''
                # code using self
                self.publishme('New Section')
        ```
        
        In the notebook, I use `%autoreload` when executing the development module with code like. 
        
        ```
        %aimport dev
        from dev import Development
        ```
        
        Followed by
        ```
        %autoreload 1
        self=Development( input_data):
        self.new_section()
        ```
        
        To play with new code in the notebook before inserting into the module, I have "self" available. Executing such
        cells may need a "%autoreload 0" to disable the automatic reloading of the development module.
        
        While generating and testing a document, the display in the notebook may be large. For this reason,
        it is possible to suppress display in the notebook by setting executing "display_on=False" to suppress notebook 
        output. This does not affect the document itself, all of which will be written to the "doc_folder" folder. It is
        very useful to a have a window open to the browser display of this file, to monitor the entire document.
        
        
        #### Output to HTML
        To produce the HTML (and eventual PDF) document, I add a member function that calls the relevant 
        sequence of member fuctions, followed by a self.save. For this document, that is `__call__`:
        
        ```
        from jupydoc import Document
        doc=Document( doc_folder='/nfs/farm/g/glast/u/burnett/git/tburnett.github.io/jupydoc',)
        ```
        To produce a copy, or display it in your notebook, just try this online.
        """
        self.publishme('Workflow')
    
    def other_formatting_options(self):
        r"""
        Markdown text is designed to be readable and easy to compose, a huge difference from
        the formal HTML, to which it is translated. One can of course insert HTML 
        directly into the text, of course compromising the readability, and requiring HTML knowledge. 
        Jupydoc processing allows inserting predefined strings when processing the docstring text, 
        which represents a  compromise. 
        
        Variable names in the docstring text come from three sources, each one updating the previous
        set. 
        1. Built-in. A class variable `predefined`. This is set to the useful values discussed here,
        but of course the user may update or replace it.
        2. The local variables available to the code in the function, locally defined or defined 
        in the argument list, especially "self". (So predefined variables are also `self.predefined.var`)
        3. Variables defined in the call to `publishme`, collected with Python's `**kwargs` mechanism. 
        These may override any of the previous.

        #### Indenting
        Indenting a paragraph is not directly possible with markdown. But we predefine:
        
        * {{indent}}: `{indent}` &mdash;the margin is predefined, easily changed by the user
        *  {{endp}}: `{endp}` &mdash; Since it represents the end of a paragraph.
        
        Demonstration:
        {indent}
        This paragraph is indented 5%. It was preceded by {{indent}} and followed by {{endl}}.
        <br>To start a new line in this, or any other paragraph, insert "&lt;br&gt;". 
        {endp}
        
        #### Preformatted text
        The function `monospace(text)` is provided to achieve insertion of "preformatted" text with a monospace font.
        It can be invoked with a text string, or any object, that returns a description of itself via its class `__str__` 
        function. For example "test_string = self.monospace('This is a multi-line test.\nAfter a newline.')", 
        with a corresponding  "{{test_string}}" will look like:
        {test_string}
        """
        test_string = self.monospace('This is a multi-line test.\nAfter a newline.')
        self.publishme('Other Formatting options')

    def object_replacement(self):
        """A key element of jupydoc is the ability to recognize the class of a variable appearing in the document, and 
        replace it with an instance of a "wrapper" class, which implements a alternative to the `__str__` method of the 
        original class. This is implemented by default for Figure, DataFrame and dict.
        It is all done in the class `jupydoc.replacer.ObjectReplacer`, which inherits from `dict`. 
        An instance is in the Publisher instance.
        The initial value of `self.object_replacer` is:
        
        {self.object_replacer}
        
        where the value is a tuple, the two columns displayed.
        
       
        So in the constructor of a subclass, one can modify this instance, using 'update`, to change current keyword args, or 
        add a new wrapper class.
        A wrapper class is instantiated with two arguments: the instance that it will interpret, and the kwargs. 
        """
        #---------------------------------------------------------------------------------
        self.publishme('Object replacement')
        
    def __call__(self, section_number=None):
        sections = [
            self.title_page,
            self.introduction,
            self.formatting_summary,
            self.document_structure,
            self.file_structure,
            self.other_formatting_options,
            self.workflow,
            self.object_replacement,
            ]
        if section_number is not None:
            n = section_number
            #print(f'selected section {section_number}')
            self.section_number = n-1 if n>0 else len(sections)+n 
            sections[section_number]()
            return
        
        # assemble and save the whole document
        for f in sections:
            f()
        self.save()
        
def main( doc_folder='jupydoc_document',):
           
    doc=Document(doc_folder=doc_folder, no_display=True)
    doc()
    
## make this executable?