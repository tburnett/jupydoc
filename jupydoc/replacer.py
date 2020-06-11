"""
THis defines a jupydoc helper which manages creation of HTML for objects of selected classes
 
For such classes, replace the object in the variable dictionary with a new one that implements a __str__ function, which returns
markdown, usually HTML.

Implemented here: Figure, Dataframe, dict
"""
import os, shutil
try:
    import matplotlib.pyplot as plt
except:
    plt=None
try: 
    import pandas as pd
except:
    pd=None

document_folders = ['.']
                     
class Wrapper(object):
    """Base class for the replacement classes
    """
    def __init__(self, vars):
        self.vars=vars
    def __repr__(self): return str(self)
    def _repr_html_(self): return str(self)

if plt:        
    class FigureWrapper(Wrapper,plt.Figure):
        
        def __init__(self, fig, vars, folder_name='figs', fig_folders=[], fig_numberer=None,
                    fig_class='jupydoc_fig'):
            super().__init__(vars)
            self.__dict__.update(fig.__dict__)
            self.fig = fig
            self.folder_name=folder_name
            self.fig_folders=fig_folders
            self.numberer=fig_numberer
            self.number = fig.number = fig_numberer()
            self.fig_class=fig_class 

            for folder in fig_folders:
                os.makedirs(os.path.join(folder,  folder_name),exist_ok=True)

        def __str__(self):
            
            if not hasattr(self, '_html') :
            
                # only has to do this once:
                fig=self.fig
                caption=getattr(fig,'caption', '').format(**self.vars)
                # save the figure to a file, then close it
                fig.tight_layout(pad=1.05)
                n =self.number
                fn = os.path.join(self.folder_name, f'fig_{n:02d}.png')
                browser_fn =fn
                # actually save it for the document, perhaps both in the local, and document folders
                for folder in self.fig_folders:
                    fig.savefig(os.path.join(folder,fn))#, **fig_kwargs)
                plt.close(fig) 

                # add the HTML as an attribute, to insert the image, including optional caption

                self._html =  f'<div class="{self.fig_class}"><figure> <img src="{browser_fn}" alt="Figure {n} at {browser_fn}">'\
                        f' <figcaption>{caption}</figcaption>'\
                        '</figure></div>\n'
            return self._html
       

class JupydocImageWrapper(Wrapper):
    def __init__(self, img, vars, folder_name='images', **kwargs):
        super().__init__(vars)
        self.img=img
        
        for df in document_folders:
            os.makedirs(os.path.join(df, folder_name),exist_ok=True)
            img.saveto(df)

    def __str__(self):
        return str(self.img)
if pd:
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

def check_image_file(filename):
    if not os.path.isfile(filename): return False
    ext = os.path.splitext(filename)[-1]
    return ext  in ['.png', '.jpg']



class FigNumberer(object):
    """ used"""
    def __init__(self, previous_number=0):
        self.number = previous_number
    
    def __call__(self):
        self.number+=1
        return self.number
    
# Maps classes, and associated keywords to replacements for display purposes

class ObjectReplacer(dict):
    """
    Functor that will replace objects in a variables dictionary
    It is a dictionary,
        key: a name of a class to have its instances replaced
        value: tuple with two elements: 
            1. the replacement class, which implements a __str__ method
            2. kwargs to apply to new object
    """
    def __init__(self, 
                  folders:'one or more document folders to save images'=['.'], 
                ):
        self.set_folders(folders)
        
    def set_folders(self, folders):
        global document_folders
        document_folders = folders
        # set up 
        df_kwargs= dict( notebook=True, 
                         max_rows=10, 
                         index=False,
                         show_dimensions=False, 
                         justify='right',
                         float_format=lambda x: f'{x:.3f}',
                       )
        self.update(dict( 
                JupydocImage =( JupydocImageWrapper, {}),                
                )
        )
        if pd:
            self.update(dict(  
                DataFrame= (DataFrameWrapper, df_kwargs),
                )
            )
        if plt:
            self.update(dict(  
                Figure=    (FigureWrapper, dict(fig_folders=folders,
                                                fig_numberer=FigNumberer() ),),
                ),
            )

    @property
    def folders(self):
        return document_folders

  
    def __repr__(self):
        r= pd.DataFrame.from_dict(self,orient='index', columns=['wrapper class','keyword dict'])
        r.index.name='key'
        return r._repr_html_()
        
    def __call__(self, vars):
        """for each value in the vars dict, replace it with a new object that
        implements return of appropriate HTML for the original object
        (Note uses the *class name* as a key)
        """
        for key,value in vars.items():

            new_class, kwargs = self.get(value.__class__.__name__, (None,None))
            
            if new_class:
                newvalue = new_class(value, vars, **kwargs)
                vars[key] = newvalue
                
def test(previous=20):
    # define a few figures, assign differned fignumbers
    fig1, ax1 = plt.subplots(num=1) 
    fig2, ax2 = plt.subplots(num=2) 
    
    # set up the replacer, to start after given value
    r = ObjectReplacer(previous_fignumber=previous)
    
    # set up variable dictionary
    vars = dict(fig1=fig1, fig2=fig2)
    before = (vars['fig1'].number, vars['fig2'].number)
    r(vars)
    after = (vars['fig1'].number, vars['fig2'].number)
    print(f'Figure nubers:\nbefore: {before}\nafter : {after}')
    plt.close('all')
    
    assert after[0]==previous+1,f'Failed to set number: got {after[0]}'
