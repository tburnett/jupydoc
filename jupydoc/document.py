"""
Producing documents using Jupyterlab with Jupydoc

"""
import os
import numpy as np
import pylab as plt
import pandas as pd

from jupydoc import Publisher

class JupyDoc(Publisher):
    """
    title: |
            Jupydoc: Generate documents with Python code 
            Introduction and demonstration
    author: |
            Toby Burnett <tburnett@uw.edu>
            University of Washington
   
    sections: title_page introduction formatting_summary document_structure
        file_structure other_formatting_options object_replacement workflow
    """ 
    
    def __init__(self,  **kwargs):
        doc_folder = kwargs.get('doc_folder', None)
        if doc_folder and doc_folder[0]!='/':
            doc_folder = os.path.join(doc_path, doc_folder)
        kwargs['doc_folder'] = doc_folder
        super().__init__( **kwargs)
                    
    def introduction(self):
        """Introduction
        
        ### What it is **not**
        Jupydoc, despite the name, does not explicitly depend on Jupyterlab. It is not a nice way to turn 
        detailed notebooks into documents: If you want that, see this 
        [system](http://blog.juliusschulz.de/blog/ultimate-ipython-notebook). 
        
        ### What is it, and how does it work?
        Jupydoc is not centered on a jupyterlab notebook. It is designed to make it easy to *develop* a
        document with a noteboook, but the *medium* is a Python class, not a  notebook. Since it is
        based on code, that implies developing the code at well&mdash;the document may represent the
        code development itself.
        
        It is lightweight, some ~400 lines of code in Python exclusive of this document, depending on
        IPython and nbconvert, and also with non-essential dependencies on pandas, matplotlib, and numpy.   
        Some points to illustrate the design and operation are:
        
        * **Code and markdown cells in a Jupyterlab notebook**<br>
        The origin of this package was rooted in a desire to be able to combine the nice formatting capability of
        markdown cells, with the output from the computation in a code cell. By default, any matplotlib
        figures created in its computation will automatically appear below the cell. This behavior, it turns out,
        can be controlled  by code executed in the cell. The key here is that code can create markdown text,
        which will be interpreted just as the text in a markdown cell. This includes LaTex. The markdown so created
        is nicely rendered in the notebook. This is accomplishted by IPython. So a notebook is not actually required, 
        see `nbconvert` below.
         
        * **Python [inspection](https://docs.python.org/3/library/inspect.html)**<br>
        The inspection capability gives access to two important elements of a function:
         * docstring&mdash; a text string immediately following the function declaration.
         * symbol table&mdash;in python terms, a "dict" with variable names as keys, and where each value is a
           reference to the object represented by the name
        
        * **Python string format method**<br>
        Since python 2.6, text strings have had a "format" method, which interprets occurrences of "{{...}}", 
        replacing what it finds between the
        curly brackets with its evaluation as an expression. (With python 3, this is built into special format strings.)
        
        * **[nbconvert](https://nbconvert.readthedocs.io/en/latest/)**<br>
        This separate package supports creation of an HTML document from notebook-formatted data, specifically 
        interpreting Jupyterlab's version of markdown. 
        It is necessary to produce an (almost) identical-looking  document to what is rendered in the notebook.
        
        ### What is it good for?
        
        * **A document like this**<br>
        This document is itself a demonstration, testing all the features it describes! It was generated using 
        member functions  of the class `jupydoc.Document`, which inherits from `jupydoc.Publisher`.
        Each such function represents a section of the document. The code that produced this document is in fact testing and 
        describing the code that produces it.
               
        * **Simple Jupyterlab-based analyses**<br>
        Rather than spreading output among several cells, this encourages making a coherent description, 
        including  plots, formulae, tables, etc. in the area below a single cell.
        
        * **Personal notebook**<br>
        Rather than cutting and pasting single plots to a personal notebook, this allows the clipping 
        to include many details, with LaTex formulas perhaps. Since it is easy to produce web pages at the
        same time, they could function as a notebook.
        
        * **Presentations and analysis documents**<br>
        Sharing one's analysis results with others is a small step from the personal notebook. The days of 
        needing PowerPoint to make presentations seem to be over, so the document can be the presentation medium.
        
        * **Publication?**<br>
        Well, I'd not go that far, but the evolution to such should be easy, especially if relevant LaTex
        formulae, plots with captions and relevant description have already been done.
 
        """
        self.publishme()
        
    def formatting_summary(self):
        r"""
        A member function of a class inheriting from `jupydoc.Publisher` should have three elements:
        * a *docstring*, comment text that will be interpreted as markdown, which may contain  variable
        names in curly-brackets, 
        * Python executable code, presumably creating objects to be discussed, 
        * a line `self.publishme(`*section_name* `)`, where the optional *section_name* will be the header for output. 
        Unlike a formatted string, entries in curly brackets cannot be expressions. An alternative is that,
        if it is not present, the first line of the docstring, if followed by a blank line, will be the section 
        header.
        
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
        the figures in a section to be unique. But the actual number is set to be sequential for
        the whole document.
        It can be referred to in the text as `{{fig1.number}}`.
    
        #### Images
        Images be inserted into the docucument, as follows: 
        The jupydoc function <samp>image</samp> is provided for this purpose. In the code, set an accessible variable with
        a call `self.image(filename)':
        ```
        launch_image = self.image("/nfs/farm/g/glast/u/burnett/images/launch.jpg",
                            caption="The launch of Fermi on a Delta II on June 11, 2008", width=300)
        
        ```
        
        referred to in this text as "{{launch_image}}, will produce this:
       
        {launch_image}
        
        One can set the width or height.
        
        
        #### DataFrames
        A `pandas.DataFrame` object is treated similarly. 
        
        The code
        ```
        df = pd.DataFrame.from_dict(dict(x=x, xx=x**2), orient='index')
        
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
            
        The "{{}}" formatting may modify LaTex expressions: e.g. 
        `$q^2={{qsq:.3f}}$` &rarr; $q^2={qsq:.3f}$.
        ---
        The capability shown here for the Figure and DataFrame objects could be easily extended to other
        classes. For user objects it only necessary to define an appropriate class `__str__` function.
        
        """
        q = 1/3; qsq=q*q
        xlim=(0,10,21)
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
        
        df = pd.DataFrame.from_dict(dict(x=x, xx=x**2), orient='index')
        dfhead = df.head()
     
        launch_image = self.image("/nfs/farm/g/glast/u/burnett/images/fermi-launch.jpg",
                            caption="The launch of Fermi on a Delta II on June 11, 2008", width=300)
        
        self.publishme('Docstring Formatting')
        
    def title(self):
        """Title page
        
        The document has an optional title page containing the title, a date, 
        and perhaps an abstract. This is set either with an argument  to  the superclass `self.title_info` with
        keys "title", "author", and "abstract", or by providing the three fields in the class docstring, separated
        by a blank line.
        
        The page is produced with a call to `self.title_page`.
        """
       
        self.publishme()
        
    def sections(self):
        """Sections
        
        Each member function, with a docstring and call to `self.publishme` will 
        generate a numbered section. 
        The optional section heading can be specified either as an argument to `publishme` or as the
        first line of the function docstring, followed by a blank line.
        The numbers are sequential as called by default, but can be specified
        by setting `self.section_number` in the code.
        """    
        self.publishme()
        
    def subsections(self):
        """Subsections
        
        One can define a subsection with the **same** function structure as for a section. To be a subsection,
        a call to it must be at the end of the code for the section to which it belongs, after its call to `self.publishme`.
        
        Any symbols accessible in the section are available in the docstring portion here. For example,
        the section to which this subsection belongs set a random number $r$ to {r:.3f}.
        """
        self.publishme()
        
    def other_text(self):
        """Other text
        
        Text not fitting into the section structure can be added with a call to the member function
        `markdown`, providing a text string. 
        """
        self.publishme()
        
    def assembly(self):
        """Assembly
        
        Assembling the document requires calling the section functions in the desired order, starting with 
        the built in `title_page`. This may be done by hand of course, by adding a function to do that to
        the user subclass, or from code external to the class. But a simpler way, in the spirt of the class code
        transparently defining itself: There are up to four fields in the *class* docstring, 
        separated by empty lines: title, author, abstract, and section list. The section list is a list of the
        section function names, separated by blanks on one or more lines. For this document, for example, it is
        
        {section_name_text}
        
        The Publisher superclass defines a `__call__` function, making it callable. So to produce, and write out if the output 
        document folder has been specified, one simply calls the document object.
        
        For development in the Jupyterlab environment, one may display all, or a range of sections. Optional calls to
        the function can be
        * a (start,stop) range of indeces
        * a single integer, the index of the section function in the list
        * the name of the section
        
        Figures are added to a "figs" folder in the current folder, as well as the destination document folder.
        
        """
        section_name_text = self.monospace("""title_page introduction formatting_summary document_structure
    file_structure other_formatting_options object_replacement workflow""")
        
        self.publishme()
        
    def document_structure(self):
        """Document Structure
        
        The output document may be a single page without any title or section organization. This section discusses
        the more complete use case, with a title page, sections, and perhaps subsections as for the current document.
        
        There is of course a close correlation with the structure of the Python class that defines the document.
        This section illustrates the use of numbered subsections.
        
        The code of this section sets a random number $r$ to {r:.3f} &mdast; the symbol "r" will be available
        to any of its subsection documents. 
        
        Future enhancements could include a table of contents, appendices, and links within the document.
        """
        #------------------------
        r = np.random.random(1)[0] # will be available for subsection documents
        self.publishme()
        self.title()
        self.sections()
        self.subsections()
        self.other_text()
        self.assembly()
        
    def file_structure(self):
        """
        File structure
        
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
        self.publishme()
        
    def workflow(self):
        """
        Workflow
        
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
            '''title: The title of this document
               sections: new_section
            '''
            def __init__(self, **kwargs):
                super().__init__( **kwargs)
                ''' 
                text to summarize setup
                '''
                # setup self to correspond to needs of code here
                self.publishme('Setup')
                
            def new_section(self):
                '''New Section
                <text>
                '''
                # code using self
                self.publishme()
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
        This does not affect the document itself, all of which will be written to the "doc_folder" folder. It is
        very useful to a have a window open to the browser display of this file, to monitor the entire document.
        
        """
        self.publishme()
    
    def other_formatting_options(self):
        r"""
        Other Formatting options
        
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
        Indenting a paragraph is not directly possible with markdown. But we can easily insert the appropriate HTML
        
        * {{indent}}: `{indent}` &mdash;the margin is predefined, easily changed by the user
        *  {{endp}}: `{endp}` &mdash; Since it represents the end of a paragraph.
        
        Demonstration:
        {indent}
        This paragraph is indented 5%. It was preceded by {{indent}} and followed by {{endl}}.
        <br>To start a new line in this, or any other paragraph, insert "&lt;br&gt;". 
        {endp}
        
        #### Preformatted text
        The function `monospace(*text*)` is provided to achieve insertion of "preformatted" text with a monospace font.
        It can be invoked with a text string, or any object which returns a description of itself via its class `__str__` 
        function. For example "test_string = self.monospace('This is a multi-line test.\nAfter a newline.')", 
        with a corresponding  "{{test_string}}" will look like:
        {test_string}
        """
        test_string = self.monospace('This is a multi-line test.\nAfter a newline.')
        self.publishme()

    def object_replacement(self):
        """
        Some technical details
        
        ### Object replacement
        
        A key feature of jupydoc is its ability to recognize the class of a variable appearing in the document, and 
        replace it with an instance of a "wrapper" class, which implements a alternative to the `__str__` method of the 
        original class. This is done by default for Figure, DataFrame and dict.
        It happens in the class `jupydoc.replacer.ObjectReplacer`, which inherits from `dict`. 
        An instance is in the Publisher instance.
        The initial value of `self.object_replacer` is:
        
        {self.object_replacer}
        
        (illustrating the replacement for a Python dict)
        The value is a tuple, the two columns displayed.
        
       
        So in the constructor of a subclass, one can modify this instance, using 'update`, to change current keyword args, or 
        add a new wrapper class.
        A wrapper class is instantiated with two arguments: the instance that it will interpret, and the kwargs. 
        """
        #---------------------------------------------------------------------------------
        self.publishme()
        
        
def main( doc_folder='jupydoc_document',):
           
    doc=Document(doc_folder=doc_folder, no_display=True)
    doc()
    
## make this executable?