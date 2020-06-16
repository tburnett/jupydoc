"""
Producing documents using Jupyterlab with Jupydoc

"""
import os
import numpy as np

from jupydoc import DocPublisher
__docs__ = ['JupyDoc', ]

class JupyDoc(DocPublisher):
    """
    title: |
            Jupydoc: Generate documents with Python code 
            Introduction and demonstration
    author: |
            Toby Burnett <tburnett@uw.edu>
            University of Washington
   
    sections: introduction
              basic
              variable_formatting [scalars list_and_dict latex images 
                                figures dataframes other_formatting_options]
              making_a_document [ class_docstring document_generation output_specification]
              file_structure 

    """ 
    def __init__(self,  **kwargs):
        doc_folder = kwargs.get('doc_folder', None)
        if doc_folder and doc_folder[0]!='/':
            doc_folder = os.path.join(doc_path, doc_folder)
        kwargs['doc_folder'] = doc_folder
        super().__init__( **kwargs)
                    
    def introduction(self):
        """
        Introduction
        
        ### What it is **not**
        Jupydoc, despite the name, does not explicitly depend on Jupyterlab. 
        It is not a nice way to turn 
        detailed notebooks into documents: If you want that, see this 
        [system](http://blog.juliusschulz.de/blog/ultimate-ipython-notebook). 
        
        ### What is it, and how does it work?
        Jupydoc is not centered on a jupyterlab notebook. It is designed to make it easy to *develop* a
        document with a noteboook, but the *medium* is a Python class, not a  notebook. Since it is
        based on code, that implies developing the code at well&mdash;the document 
        may represent the code development itself.
        
        While designed to be used to develop documents based on code in a JupyterLab enviornment,
        It does not actually require it, but depends on IPython and nbconvert.
         
        Some points to illustrate the design and operation are:
        
        * **Code and markdown cells in a Jupyterlab notebook**<br>
        The origin of this package was rooted in a desire to be able to combine 
        the nice formatting capability of   markdown cells, with the output from 
        the computation in a code cell. By default, any matplotlib
        figures created in its computation will automatically appear below the cell. 
        This behavior, it turns out, can be controlled  by code executed in the cell.
        The key here is that code can create markdown text,
        which will be interpreted just as the text in a markdown cell. 
        This includes LaTex. The markdown so created
        is nicely rendered in the notebook. 
        This is accomplishted by IPython. So a notebook is not actually required, 
        see `nbconvert` below.
         
        * **Python [inspection](https://docs.python.org/3/library/inspect.html)**
        <br>The inspection capability gives access to two important elements of a function:
         * docstring&mdash; a text string immediately following the function declaration.
         * symbol table&mdash;in python terms, a "dict" with variable names as keys, 
         and where each value is a reference to the object represented by the name
        
        * **Python string format method**<br>
        Since python 2.6, text strings have had a "format" method, which interprets 
        occurrences of "{{...}}",  replacing what it finds between the
        curly brackets with its evaluation as an expression. 
        (With python 3, this is built into special format strings.)
        
        * **[nbconvert](https://nbconvert.readthedocs.io/en/latest/)**
        <br>This separate package supports creation of an HTML document from notebook-formatted data, specifically 
        interpreting Jupyterlab's version of markdown. 
        It is necessary to produce an (almost) identical-looking  document to what is rendered in the notebook.
        
        ### What is it good for?
        
        * **A document like this**<br>
        This document is itself a demonstration, testing all the features it describes! 
        It was generated using member functions  of the class `jupydoc.Document`, 
        which inherits from `jupydoc.Publisher`.
        Each such function represents a section of the document. 
        The code that produced this document is in fact testing and 
        describing the code that produces it.
               
        * **Simple Jupyterlab-based analyses**<br>
        Rather than spreading output among several cells, this encourages 
        making a coherent description, including  plots, formulae, tables, etc. 
        in the area below a single cell.
        
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
        
    def basic(self):
        '''Basic framework

        The simplest use case was mentioned above: Annotating plots from an analysis.
        It can be implemented as this, which can be used to test the options in the next section.
        
        #### Example
        The following is in a Jupyter notebook cell:
        ```
        from jupydoc import Publisher

        class Basic(publisher.Publisher):

            def doit(self):
                """This is the output from a minimal example

                """
                #-------- code ---------
                #-----------------------
                self.publishme()
                
        doc = Basic(docpath='.')
        doc.doit()
        ```

        #### Requirements
        This shows the basic requirements for a function with this capability:

        1. Is a member of a class inheriting from  `jupydoc.Publisher` 
        1. Has a *docstring*, comment text which will be interpreted as JUpyter-style markdown, and which
         may contain  variable  names in curly-brackets, 
        2. Has executable code, presumably creating variables, the values of which will shown in the
        output.
        3. Last line of the code is `self.publishme()`.

        Unlike a formatted string, entries in curly brackets cannot be expressions.

        #### Output
        The above generates a display in the notebook. Note that the `docpath='.' specifies that output should go
        into the current folder, where the notebook is. To write it to a web doc as well, add the line
        ```
        doc.save()
        ```
        which will result in something like
        ```
        saved to  "/home/burnett/work/notebooks/Basic"
        ```

        The document was written into a "saved to" folder, as a file `index.html` and also folders `figures` or `images` 
        if needed. The name of that folder, in this case `Basic`, is by default constructed by appending the class name to the
        the Python *module* name, itself related to the *file* name by
        replacing dots with slashes and adding a ".py".  In this case there was no module. 
        
        In summary, the structure looks like this:
        ```
            docpath ("/home/burnett/work/notebooks")
              | docname ("Basic")
                 | index.html
                 | figures
                    | fig01.png
                    | ...
                 | images
                    | ...

        ```
        The folder pointed by `docpath` could contain other documents, a feature used in the multiple-document section of this 
        description.

        '''

        self.publishme()

    def variable_formatting(self):
        r"""Variable Formatting 
        


        The list of possible variable names comes from three sources, each one updating the previous
        set. 
        1. Built-in. A class variable `predefined`. This is set to the useful values discussed here,
        but of course the user may update or replace it.
        2. The local variables available to the code in the function, locally defined or defined 
        in the argument list, especially "self". (So predefined variables are also `self.predefined.var`)
        3. Variables defined in the call to `publishme`, collected with Python's `**kwargs` mechanism. 
        These may override any of the previous.

        This section examines formating options for such variables in curly brackets.

        """

        self.publishme()

    def scalars(self):
        """Scalars  
        
        A scalar variable, say from an expression in the code `q=1/3`, can be interpreted in the docstring  with `"q={{q:.3f}}"`, resulting in 
        {indent}
        q={q:.3f}.        
        {endp}
        """
        q = 1/3; 
 
        self.publishme()

    def list_and_dict(self):
        """Python lists and dicts

        These basic Python data structures are represented using the "pretty printer"
        [`pprint`](https://docs.python.org/3/library/pprint.html)

        For example a list generate by `n = list(range(1,11))` appears thus:  {n}.

        And a dict generated by `d = dict((i,2**i) for i in n)` is this: {d}
        """
        n = list(range(1,11))
        d = dict((i,2**i) for i in n)

        self.publishme()

    def images(self):
        """Images

        Images be inserted into the docucument, as follows: 
        Using the jupydoc function <samp>image</samp>, set a variable with
        a call `self.image(filename)':
        ```
        launch_image = self.image("$HOME/images/fermi-launch.jpg",
                            caption="The launch of Fermi on a Delta II on June 11, 2008",
                            width=300)
        ```
        
        referred to in this text as "{{launch_image}}", will produce this:
       
        {launch_image}
        
        This uses the [HTML5 `figure` tag](https://www.w3schools.com/tags/tag_figure.asp),
        which manages a caption. One can also set the width or height, 
        see the discussion on the 
        [HTML `img` tag](https://www.w3schools.com/tags/tag_img.asp).

        """
         
        launch_image = self.image("$HOME/images/fermi-launch.jpg",
                            caption="The launch of Fermi on a Delta II on June 11, 2008", width=300)
        self.publishme()

    def figures(self):
        """Figures

        *This feature requires that `matplotlib` has been installed.* 

        Any number of Matplotlib Figure objects can be included.
        An entry "{{fig1}}", along with code that defines `fig1` like this:
        ```
        x = np.linspace(0,10)
        fig1,ax=plt.subplots(num=self.newfignum(), figsize=(4,3))
        ax.plot(x, x**2)
        ax.set(xlabel='$x$', ylabel='$x^2$', title=f'figure {{fig1.number}}')
        fig1.caption='''Caption for Fig. {{fig1.number}}, which
                shows $x^2$ vs. $x$.'''
        ```
        produces:
        {fig1}
        
        Note the convenience of defining a caption by adding the text as an attribute of
        the Figure object.  
        The `self.newfignum()` returns a new figure number. It is necessary to for all
        the figures in a section to be unique. But the actual number is set to be sequential for
        the whole document.
        Then number can be referred to in the text as `{{fig1.number}}`.
        """
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            fig1 = f'**{e}**'
            self.publishme()
            return

        plt.rc('font', size=14) # worry about setting this!
        xlim = (0,10,21)
        x = np.linspace(*xlim)
        fig1,ax=plt.subplots(num=self.newfignum(), figsize=(4,3))
        ax.plot(x, x**2)
        ax.set(xlabel='$x$', ylabel='$x^2$', title=f'figure {fig1.number}')
        fig1.caption="""Caption for Fig. {fig1.number}, which
                shows $x^2$ vs. $x$.    
            """

        self.publishme()

    def dataframes(self):
        """DataFrames

        *(This feature is only available if [pandas](https://pandas.pydata.org/) is installed)*

        The code, from [this tutorial](https://www.geeksforgeeks.org/python-pandas-dataframe/):
        ```
            # intialise data of lists.
            data = {'Name':['Tom', 'nick', 'krish', 'jack'],
                    'Age':[20, 21, 19, 18]}
            
            # Create DataFrame
            df = pd.DataFrame(data)
        
        ```
        
        <br>Results in "{{df}}" being appearing as
        {df}
    

        """
        try:
            import pandas as pd
            
            # intialise data of lists.
            data = {'Name':['Tom', 'nick', 'krish', 'jack'],
                    'Age':[20, 21, 19, 18]}
            
            # Create DataFrame
            df = pd.DataFrame(data)
        except:
            df = 'Pandas not installed'
        #----------------------
        self.publishme()

    def latex(self):
        r"""LaTex

        Jupyter-style markdown can contain LaTex expressions. For the following, unlike the simple "`$E=mc^2$`" 
        &rarr; $E=mc^2$ , it is  necessary that the docstring be preceded by an "r". So,
        ```
        \begin{{align*}}
        \sin^2\theta + \cos^2\theta =1
        \end{{align*}}
        ```
        
        <br>Results in:   
            \begin{align*}
            \sin^2\theta + \cos^2\theta =1
            \end{align*}  

        Evaluation of variables can occur within the expression as well.  
        """

        self.publishme()

    def making_a_document(self):
        """Making a document
        
        This section introduces an enhancement to the basic framework to create a structured
          *document*, with a title page, sections, and subsections.
        To accomplish this there are two basic requirement:
        1. the class needs to inherit from `DocPublisher`, 
        2. the layout of the document must be defined in the *class* docstring. 
        
       

        """
        #------------------------
        r = np.random.random(1)[0] # will be available for subsection documents
        self.publishme()

    def class_docstring(self):
        """Class Docstring
        
        The docstring is in [`yaml`](http://zetcode.com/python/yaml/), a human-readable data-serialization language
        often used for configuration files. The following items, all optional, are used to define the document:

        * **title** If more than one line, the second is a subtitle
        * **author** Will be centered.
        * **sections** A single string with names of functions corresponding to sections and possible subsections that will be parsed
        * **abstract** Can be any length.
        
        About the sections specification, this is the specification for the present document:
        ```
   
        sections: introduction
                basic
                variable_formatting [scalars list_and_dict latex images 
                                    figures dataframes other_formatting_options]
                making_a_document [ class_docstring document_generation output_specification]
                file_structure 

        ```
        Commas and line breaks are ignored, and subsection names enclosed in square brakets following the section name.
        """
       
        self.publishme()
        
    def document_generation(self):
        """Document Generation
        
        Creation of the document is performed by invoking the instantiated call. `DodPublisher` itself allows for a demonstration:
        ```
        from jupydoc import DocPublisher
        doc = DocPublisher()
        doc('all')
        ```
        The "job" of the class is to produce the document that it is designed to do, which is performed by invoking it as a function.
        The interactive display is intended to select a single section, or subsection to examine while developing the 
        code. If an output has been set, it will always generate the full HTML version. The argument possibilites are: 'all'
        as above, the name of the function whose output to examine, or the section or subsection number.

        """    
        self.publishme()

    def output_specification(self):
        """Output Specification

        The call described here runs the `save()` function described in the <a href=#basic>Basic Framework sect</a>
        The HTML document is a folder, containing the the document in a file `index.html` and folders `figures` or `images` 
        if needed. The name of that folder, called `docname` is by default constructed by appending the class name to the
        the Python *module* name, itself related to the *file* name by
        replacing dots with slashes and adding a ".py".  The folder that it goes into is set by "docpath". 

        """
        self.publishme()
        
    def subsections(self):
        """Subsections
        
        Subsection functions have the **same** function structure as for sections. To be a subsection,
        it must be declared in the "subsections" par


        ```

        ```
        
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
        
        The Publisher superclass defines a `__call__` function, making it callable. So to produce, 
        and write out if the output document folder has been specified, one simply calls the document object.
        
        For development in the JupyterLab environment, one may display all, or a range of sections. 
        Optional calls to the function can be
        * a (start,stop) range of indeces
        * a single integer, the index of the section function in the list
        * the name of the section
        
        Figures are added to a "figs" folder in the current folder, as well as the destination document folder.
        """
        #----------------------------------------------------------------
        section_name_text = self.monospace("""title_page introduction formatting_summary document_structure
        file_structure other_formatting_options object_replacement workflow""")
        #----------------------------------------------------------------
        
        self.publishme()

    def file_structure(self):
        """
        File structure
        
        ## Web
        The resulting Web document has two components: the HTML file with all the text and formatting, and, in the
        same folder, a  subfolder "figs" with the figures, which are included via the 
        HTML e.g., `<img src="figs/fig_1.png"/>`.
                
        The use case motivating this was to develop the document in Jupyter, and easily save it as a 
        Web document. In order for the figures to be displayed in the notebook, the figures must be 
        saved in its folder.
       
        Creating the Web document then entails creating (using nbconvert) the HTML file in the destination
        document folder, and copying the figure folder into it.
                
        ### PDF?
        Using nbconvert for this seems to fail. A better solution, in the works, is to use code that I 
        found in [`notebook-as-pdf`](https://github.com/betatim/notebook-as-pdf), which uses a headless
        chrome, relying on [`pyppeteer`](https://pypi.org/project/pyppeteer/) to render the HTML to a PDF file.
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
        The function `monospace(*text*)` is provided to achieve insertion of 
        "preformatted" text with a monospace font.
        It can be invoked with a text string, or any object which returns a description of itself via its class `__str__` 
        function. For example "test_string = self.monospace('This is a multi-line test.\nAfter a newline.')", 
        with a corresponding  "{{test_string}}" will look like:
                 {linkto_top}
        {test_string}
        """
        test_string = self.monospace('This is a multi-line test.\nAfter a newline.')
        self.publishme()

    def object_replacement(self):
        """
        Some technical details
        
        ### Object replacement
        
        A key feature of jupydoc is its ability to recognize the class of a 
        variable appearing in the document, and  replace it with an instance of a "wrapper" class, 
        which implements a alternative to the `__str__` method of the 
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
        
