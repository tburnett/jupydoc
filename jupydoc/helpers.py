"""
jupydoc helper functions
"""
import os, string, io, inspect

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def doc_display(funct:'function object or dict with keys name, doc, locs', 
                fig_folders:'path to one or more folders'=['.'],
                fig_kwargs:'additional kwargs to pass to the savefig call'={}, 
                df_kwargs:'additional kwargs to pass to the to_html call for a DataFrame'={}, 
                predefined:'dict of predfinded variables'={},
                **kwargs:'',
               )->str:
    """Format the docstring, as an alternative to matplotlib inline in jupyter notebooks
    
    Parameters
    ----------    
    funct : function object | dict
        if a dict, has keys name, doc, locs
        otherlwise, the calling function, used to obtain is name, the docstring, and locals
    fig_folders : list, default ['.']
        save into a 'figs' folder in each of these. Document will refer to "figs/fig_x.png"
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
        locs = funct['locs']
    else:
        raise Exception(f'Expected a function or a dict with keys {expected_keys}: got {funct}')

    # create variable dictionary: predefined, locals, kwargs
    vars = predefined.copy()
    vars.update(locs)
    vars.update(kwargs)
   
   
    # process each Figure or DataFrame found in local for display 
    
    class FigureWrapper(plt.Figure):
        def __init__(self, fig, folder_name='figs'):
            self.__dict__.update(fig.__dict__)
            self.fig = fig
            self.folder_name=folder_name
            for folder in fig_folders:
                os.makedirs(os.path.join(folder,  folder_name),exist_ok=True)
            
        @property
        def html(self):
            # backwards compatibility with previous version
            return self.__str__()
            
        def __str__(self):
            if not hasattr(self, '_html'):
                fig=self.fig
                n = fig.number
                caption=getattr(fig,'caption', '').format(**vars)
                # save the figure to a file, then close it
                fig.tight_layout(pad=1.05)
                fn = os.path.join(self.folder_name, f'fig_{n}.png')
                # actually save it for the document, perhaps both in the local, and document folders
                for folder in fig_folders:
                    fig.savefig(os.path.join(folder,fn), **fig_kwargs)
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
        if hasattr(fig, 'html'): returnfig_fold
        return FigureWrapper(fig)
        
    def dataframe_html(df):
        if hasattr(df, 'html'): return None
        return DataFrameWrapper(df)
   
    def processor(key, value):
        # value: an object reference to be processed 
        print(key,value)
        ptable = {plt.Figure: figure_html,
                  pd.DataFrame: dataframe_html,
                 }
        f = ptable.get(value.__class__, lambda x: None)
        # process the reference: if recognized, there may be a new object
        newvalue = f(value)
        if newvalue is not None: 
            vars[key] = newvalue
            print(f'key={key}, from {value.__class__.__name__} to  {newvalue.__class__.__name__}')
    
    for key,value in vars.items():
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
        
    print(f'doc:{doc}\nvariable names:{vars.keys()}')                    
    docx = Formatter().vformat(doc+'\n', vars)       
    # enhances this: docx = doc.format(**vars)

    return docx

def md_to_html(output, filename, title='jupydoc'):
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
    
    # Change the title from default "Notebook"
    output = output.replace('Notebook', title)
    
    with open(filename, 'wb') as f:
        f.write(output.encode('utf8'))
#---------------------------------------------------------------------------------
def test_display():
    print('testing...')
    def test():
        """
        The value of x is: {x}
        """
        x=99
    r = doc_display(test)    
    print(f'Resulting string:\n "{r}"'  ) 