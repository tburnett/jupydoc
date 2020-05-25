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
    def __init__(self, df, vars, **kwargs):
        super().__init__(vars)
        self._df = df
        self.kw = kwargs

    def __str__(self):
        if not hasattr(self, '_html'):
            self._html = self._df.to_html(**self.kw) #**dfkw) # self._df._repr_html_()                
        return self._html

class DictWrapper(Wrapper):
    def __init__(self, d, vars, **kwargs):
        self.df=pd.DataFrame([d.keys(), d.values()], 
                             index='key value'.split()).T
    def __str__(self):
        return self.df.to_html(index=False)

# Maps classes, and associated keywords to replacements for display purposes

class ObjectReplacer(dict):
    """
    Functor that will replace objects in a variables dictionary
    It is a dictionary,
        key: a class to have it instances replaced
        value: tuple with two elements: 
            1. the replacement class, which implements a __str__ method
            2. kwargs to apply to generating the 
    """
    def __init__(self):
        # set up 
        df_kwargs= dict( notebook=True, 
                         max_rows=10, 
                         index=False,
                         show_dimensions=False, 
                         justify='right',
                         float_format=lambda x: f'{x:.3f}',
                       )
        self.update(dict(
                Figure=    (FigureWrapper, dict(fig_folders=[],) ),
                DataFrame= (DataFrameWrapper,df_kwargs),
                dict=      (DictWrapper,{} ),
                )
            )
  
    def __repr__(self):
        r= pd.DataFrame.from_dict(self,orient='index', columns=['wrapper class','keyword dict'])
        r.index.name='key'
        return r._repr_html_()
        
    def __call__(self, vars):
        """for each value in the vars dict, replace it with a new object that
        implements return of appropriate HTML for the original object
        (Note uses the *name* as a key)
        """
        for key,value in vars.items():

            new_class, kwargs = self.get(value.__class__.__name__, (None,None))
            
            if new_class:
                newvalue = new_class(value, vars, **kwargs)
                vars[key] = newvalue