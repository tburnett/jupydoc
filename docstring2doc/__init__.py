"""Generate documents for Jupyter display 
"""

import os, inspect, string, io, datetime
#import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def doc_display(funct, figure_path='docs/figs', fig_kwargs={}, df_kwargs={},  **kwargs):
    """Format the docstring, as an alternative to matplotlib inline in jupyter notebooks
    
    Parameters
    ----------    
    funct : function object | dict
        if a dict, has keys name, doc, locs
        otherlwise, the calling function, used to obtain is name, the docstring, and locals
    figure_path : string, optional, default 'docs/figs'
    fig_kwargs : dict,  optional
        additional kwargs to pass to the savefig call.
    df_kwargs : dict, optional, default {"float_format":lambda x: f'{x:.3f}', "notebook":True, "max_rows":10, "show_dimensions":}
        additional kwargs to pass to the to_html call for a DataFrame
    kwargs : used only to set variables referenced in the docstring.    
    
    Expect this to be called from a function or class method that may generate one or more figures.
    It takes the function's docstring, assumed to be in markdown, and applies format() to format values of any locals. 
    
    Each Figure to be displayed must have a reference in the local namespace, say `fig`, and have a unique number. 
    Then the  figure will be rendered at the position of a '{fig}' entry.
    In addition, if an attribute "caption" is found in a Figure object, its text will be displayed as a caption.
    
    Similarly, if there is a reference to a pandas DataFrame, say a local variable `df`, then any occurrence of `{df}`
    will be replaced with an HTML table, truncated according to the notebook format.
    
    A possibly important detail, given that The markdown processor expects key symbols, like #, to be the first on a line:
    Docstring text is processed by inspect.cleandoc, which cleans up indentation:
        All leading whitespace is removed from the first line. Any leading whitespace that can be uniformly
        removed from the second line onwards is removed. Empty lines at the beginning and end are subsequently
        removed. Also, all tabs are expanded to spaces.
      Unrecognized entries are ignored, allowing latex expressions. (The string must be preceded by an "r"). In case of
    confusion, double the curly brackets.

    """  
    # check kwargs
    dfkw = dict(float_format=lambda x: f'{x:.3f}', notebook=True, max_rows=10, show_dimensions=False, justify='right')
    dfkw.update(df_kwargs)

    # get docstring from function object
    expected_keys='doc name locs'.split()
    if inspect.isfunction(funct): #, f'Expected a function: got {funct}'
        doc = inspect.getdoc(funct)

        # use inspect to get caller frame, the function name, and locals dict
        back =inspect.currentframe().f_back
        name= inspect.getframeinfo(back).function
        locs = inspect.getargvalues(back).locals.copy() # since may modify

    elif (type(funct) == dict) and (set(expected_keys) == set(funct.keys())):
        doc=funct['doc']
        name=funct['name']
        locs = funct['locs'].copy()
    else:
        raise Exception(f'Expected a function or a dict with keys {expected_keys}: got {funct}')
    
    # add kwargs if any
    locs.update(kwargs)
    
   
    # process each Figure or DataFrame found in local for display 
    
    class FigureWrapper(plt.Figure):
        def __init__(self, fig):
            self.__dict__.update(fig.__dict__)
            self.fig = fig
            
        @property
        def html(self):
            # backwards compatibility with previous version
            return self.__str__()
            
        def __str__(self):
            if not hasattr(self, '_html'):
                fig=self.fig
                n = fig.number
                caption=getattr(fig,'caption', '').format(**locs)
                # save the figure to a file, then close it
                fig.tight_layout(pad=1.05)
                fn = f'{figure_path}/fig_{n}.png'
                fig.savefig(fn, **fig_kwargs)
                plt.close(fig) 

                # add the HTML as an attribute, to insert the image, including optional caption

                self._html =  f'<figure> <img src="{fn}" alt="Figure {n} at {fn}">'\
                        f' <figcaption>{caption}</figcaption>'\
                        '</figure>\n'
            return self._html
        
        def __repr__(self):
            return self.__str__()

        
    class DataFrameWrapper(object): #pd.DataFrame):
        def __init__(self, df):
            #self.__dict__.update(df.__dict__) #fails?
            self._df = df
        @property
        def html(self):
            # backwards compatibility with previous version
            return self.__str__()
        def __repr__(self):
            return self.__str__()
        def __str__(self):
            if not hasattr(self, '_html'):
                self._html = self._df.to_html(**dfkw) # self._df._repr_html_()                
            return self._html

            
    def figure_html(fig):
        if hasattr(fig, 'html'): return
        os.makedirs(figure_path, exist_ok=True)
        
        return FigureWrapper(fig)
        
    def dataframe_html(df):
        if hasattr(df, 'html'): return None
        return DataFrameWrapper(df)
   
    def processor(key, value):
        # value: an object reference to be processed 
        ptable = {plt.Figure: figure_html,
                  pd.DataFrame: dataframe_html,
                 }
        f = ptable.get(value.__class__, lambda x: None)
        # process the reference: if recognized, there may be a new object
        newvalue = f(value)
        if newvalue is not None: 
            locs[key] = newvalue
            #print(f'key={key}, from {value.__class__.__name__} to  {newvalue.__class__.__name__}')
    
    for key,value in locs.items():
        processor(key,value)
   
    # format local references. Process Figure or DataFrame objects found to include .html representations.
    # Use a string.Formatter subclass to ignore bracketed names that are not found
    #adapted from  https://stackoverflow.com/questions/3536303/python-string-format-suppress-silent-keyerror-indexerror

    class Formatter(string.Formatter):
        class Unformatted:
            def __init__(self, key):
                self.key = key
            def format(self, format_spec):
                return "{{{}{}}}".format(self.key, ":" + format_spec if format_spec else "")

        def vformat(self, format_string,  kwargs):
            try:
                return super().vformat(format_string, [], kwargs)
            except AttributeError as msg:
                return f'Failed processing because: {msg.args[0]}'
        def get_value(self, key, args, kwargs):
            return kwargs.get(key, Formatter.Unformatted(key))

        def format_field(self, value, format_spec):
            if isinstance(value, Formatter.Unformatted):
                return value.format(format_spec)
            #print(f'\tformatting {value} with spec {format_spec}') #', object of class {eval(value).__class__}')
            return format(value, format_spec)
                        
    docx = Formatter().vformat(doc+'\n', locs)       
    # replaced: docx = doc.format(**locs)

    return docx

def md_to_html(output, filename):
    """write nbconverted markdown to a file 
    
    parameters
    ----------
    output : string | IPython.utils.capture.CapturedIO object
        if not a string extract the markdown from each of the outputs list 
    """
    from nbconvert.exporters import  HTMLExporter
       
    if type(output)==str:
        md_text=output
    elif hasattr(output, 'outputs'):
        md_text=''
        for t in output.outputs:            
            md_text += '\n\n'+t.data['text/markdown']
    else:
        raise Exception(f'output not recognized: {output.__class__} not a string or CapturedIO object?')
    
    class Dict(dict):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.update(kwargs)
    nb = Dict(
            cells= [Dict(cell_type="markdown", 
                         metadata={}, 
                         source=md_text,
                        )
                   ],
            metadata={},
            nbformat=4,
            nbformat_minor=4,
            )

    # now pass it to nbconvert to write as an HTML file
    exporter = HTMLExporter()
    output, resources = exporter.from_notebook_node(nb) 
    with open(filename, 'wb') as f:
        f.write(output.encode('utf8'))

class Publisher(object):
    """Base class for generating a document in Jupyter/IPython.
    A subclass must run super().__init__(). Then any member function that calls self.publishme()
    will have its docstring processed.
    
    Implements the "with" construction. 
   
    """
    def __init__(self, 
            title_info={'title':'untitled'},
             title:'Title for the document'='no title',
             author:'Optional author line'=None,
             doc_path:'path to store the document and figures'='docs', 
             fignum=1, 
             section_number:'Initial section number'=0, 
             html_file:'if set, save the accumulated output to an HTML file when closed'='', 
             pdf_file:'eventually implement'='', 
             no_display:'set True to avoid Jupyter display output'=False,
            ):
        """
        doc_path : None or string
            Path to save figures
            if None, use figs/<classname>
        fignum : optional, default 1
            First figure number to use
        html_file : optional, default None
            if set, save the accumulated output to an HTML file when closed
        pdf_file : optional default None
            If set, save the accumulated docstring output to the PDF file when closed.
        """
        self.doc_path= doc_path or 'docs/'
        self.fig_path=f'{self.doc_path}/figs/{self.__class__.__name__}'
        os.makedirs(self.fig_path, exist_ok=True)
        self.title_info=title_info
        self._fignum=fignum-1
        self.section_number = section_number

        self.date=str(datetime.datetime.now())[:16]
        self.pdf_file=pdf_file
        self.html_file= f'{self.doc_path}/{html_file}' if html_file else ''
        self.no_display=no_display
        self.data = ''
    
    def __str__(self):
        return f'classname "{self.__class__.__name__}", title "{self.title_info["title"]}"'
    
    # Support the 'with ...'
    def __enter__(self): return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.finish()

    def _publish(self, text):
        """ add text to docuemnt, display with IPython if set"""        
        import IPython.display as display #only dependence on IPython
        self.data = self.data + '\n\n' + text
        
        if self.no_display: return
        display.display(display.Markdown(text)) 
        
    def title_page(self, text:'additional text'=''):
        """
        {title_line}
        {date_line} 
        {subtitle_line}
        {author_line}
        {text}
        """
        if self.title_info:
            ti = self.title_info
            title=ti.get('title', 'untitled?')
            subtitle=ti.get('subtitle', '')
            author=ti.get('author', '')
            abstract=ti.get('abstract', '')
            
        date_line=f'<p style="text-align: right;">{self.date}</p>'
        author= author.replace('<','&lt;').replace('>','&gt;')
        author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
        title_line=f'<p style="text-align:center;"> <H1>{title}</H1></p>' 
        subtitle_line=f'<p style="text-align:center;"> {subtitle}</p>' if subtitle else '' 
        self.publishme()
        self.section_number=0
            
    def markdown(self, text:"markdown text to add to document", clean=True)->'markdown':
        """Add md text to the display"""
        if clean:
            text= inspect.cleandoc(text)
        self._publish(text)

    def newfignum(self) -> "a new figure number":
        self._fignum+=1
        return self._fignum
    
    def publishme(self, 
                  section_name:'Optional name for the section'=None, 
                  section_number:'Optional number to apply'=None, 
                  **kwargs:'not used')->None:
        # numbering: a new section and 
        self.section_name = section_name
        self.section_number = section_number or self.section_number+1
        #self._fignum = 10*self.section_number
        
        # use inspect to get caller frame, the function name, and locals dict
        back =inspect.currentframe().f_back
        name= inspect.getframeinfo(back).function
        locs = inspect.getargvalues(back).locals
        
        # construct the calling function object to get its docstring
        funct =eval(f'self.{name}')
        doc = inspect.getdoc(funct)

        # process it all with helper function that returns markdown
        md_data = doc_display( 
                    dict(name=name, doc=doc, locs=locs),  
                    no_display=True,
                    figure_path=self.fig_path, **kwargs)
        # prepend formatted header 
        if section_name:
            header = f'\n\n## {self.section_number:d}. {section_name}\n\n'
            md_data = header + md_data
        # and send if off
        self._publish(md_data)
        
    def finish(self):

        if self.pdf_file:
            print('*** PDF generation not yet implemented!')
        if self.html_file:
            md_to_html(self.data, self.html_file )
        
        self.markdown(f"""
            ---
            Saved file to "{self.html_file}"
            """
        )
        self.data=''