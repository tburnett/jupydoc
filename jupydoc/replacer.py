"""
THis defines a jupydoc helper function which manages creation of HTML for objects of selected classes
 
For such classes, replace the object in the variable dictionary with a new one that implements a __str__ function, which returns
markdown, usually HTML.

Implemented here: Figure, Dataframe, dict
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Wrapper(object):
    """Base class for the replacement classes
    """
    def __init__(self, vars):
        self.vars=vars
    def __repr__(self): return str(self)
    def _repr_html_(self): return str(self)

        
class FigureWrapper(Wrapper,plt.Figure):
    
    def __init__(self, fig, vars, folder_name='figs', fig_folders=[]):
        super().__init__(vars)
        self.__dict__.update(fig.__dict__)
        print(fig_folders)
        self.fig = fig
        self.folder_name=folder_name
        self.fig_folders=fig_folders
        for folder in fig_folders:
            os.makedirs(os.path.join(folder,  folder_name),exist_ok=True)

    def __str__(self):
        if not hasattr(self, '_html'):
            fig=self.fig
            n = fig.number
            caption=getattr(fig,'caption', '').format(**self.vars)
            # save the figure to a file, then close it
            fig.tight_layout(pad=1.05)
            fn = os.path.join(self.folder_name, f'fig_{n}.png')
            # actually save it for the document, perhaps both in the local, and document folders
            for folder in self.fig_folders:
                fig.savefig(os.path.join(folder,fn))#, **fig_kwargs)
            plt.close(fig) 

            # add the HTML as an attribute, to insert the image, including optional caption

            self._html =  f'<figure> <img src="{fn}" alt="Figure {n} at {fn}">'\
                    f' <figcaption>{caption}</figcaption>'\
                    '</figure>\n'
        return self._html

class DataFrameWrapper(Wrapper): 
    def __init__(self, df, vars,**kwargs):
        super().__init__(vars)
        self._df = df

    def __str__(self):
        if not hasattr(self, '_html'):
            self._html = self._df.to_html(index=False) #**dfkw) # self._df._repr_html_()                
        return self._html

class DictWrapper(Wrapper):
    def __init__(self, d, vars, **kwargs):
        self.df=pd.DataFrame([d.keys(), d.values()], 
                             index='key value'.split()).T
    def __str__(self):
        return self.df.to_html(index=False)

# Maps classes, and associated keywords to replacements for display purposes
default_replace_table = {
        plt.Figure:  (FigureWrapper, {'fig_folders': ['.'], } ),
        pd.DataFrame: (DataFrameWrapper,{}),
        dict:         (DictWrapper,{} ),
     }

classs Rekplacer(object):
    def __init__(self, 
             replace_table=default_replace_table, 
            ):
        self.replace_table = replace_table
        
    def __call__(self, vars):
        """for each value in the vars dict, replace it with a new object that
        implements return of appropriate HTML for the original object
        """
        if not replace_table: return

        for key,value in vars.items():

            new_class, kwargs = self.replace_table.get(value.__class__, None)

            if new_class is None:
                continue
            newvalue = new_class(value, vars, **kwargs)
            vars[key] = newvalue