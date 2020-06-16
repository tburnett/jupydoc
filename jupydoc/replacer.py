"""
THis defines a jupydoc helper which manages creation of HTML for objects of selected classes
 
For such classes, replace the object in the variable dictionary with a new one that implements a __str__ function, which returns
markdown, usually HTML.

Implemented here: dict, and if can be importer plt.Figure, pd.Dataframe
"""
import os, shutil
import pprint 

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
    Itself uses the str for the object in question
    """
    def __init__(self, *pars, **kwargs):
        self.obj = pars[0]
        self.vars=pars[1]
        self.indent = kwargs.pop('indent', '5%')
    def set_folders(self, folders):
        pass
    def __repr__(self): return str(self)
    def _repr_html_(self): return str(self)
    def __str__(self):
        text = str(self.obj).replace('\n', '\n<br>')
        return f'<p style="margin-left: {self.indent}"><samp>{text}</samp></p>'



if plt: 
    class FigNumberer(object):
        """ used"""
        def __init__(self, previous_number=0):
            self.number = previous_number
        
        def __call__(self):
            self.number+=1
            return self.number  
    fig_numberer = FigNumberer()

    class FigureWrapper(Wrapper,plt.Figure):
        
        def __init__(self, *pars, **kwargs): 
                    #fig, vars, folder_name='figs', fig_folders=[], fig_numberer=FigNumberer(),   fig_class='jupydoc_fig'):
            
            super().__init__(*pars, **kwargs)

            fig = self.obj
            self.__dict__.update(fig.__dict__)
            self.fig = fig
            # from kwargs
            self.folder_name=kwargs.pop('folder_name', 'figs')
            self.fig_folders=kwargs.pop('fig_folders', [])
            
            self.number = fig.number = fig_numberer() # get a new number
            self.fig_class=kwargs.pop('fig_class', 'jupydoc_fig') 

            for folder in self.fig_folders:
                os.makedirs(os.path.join(folder,  self.folder_name),exist_ok=True)

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
 

    def __str__(self):
        return str(self.img)
if pd:
    class DataFrameWrapper(Wrapper): 
        def __init__(self, *pars, **kwargs):

            super().__init__(*pars, **kwargs)
            self._df = self.obj
            self.kw = kwargs

        def __str__(self):
            if not hasattr(self, '_html'):
                self._html = self._df.to_html(**self.kw)                
            return self._html

class PPWrapper(Wrapper):
    """Use PrettyPrint
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=2)
        text = pp.pformat(self.obj).replace('\n', '<br>\n')
        return f'<p style="margin-left: {self.indent}"><samp>{text}</samp></p>'

    
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

        self.add_rep('dict', PPWrapper)  
        self.add_rep('list', PPWrapper)
        
        
    def add_rep(self, class_name:'name of class to replace', 
                    out_class:'replacement class', 
                    kwargs:'Any parameters to pass to output class'={}):
        """
        add a replacement entry
        """
        self[class_name] = (out_class, kwargs)
    
    def set_folders(self, folders):
        # folder management for these guys
        global document_folders
        document_folders = folders
        # set up 

        if pd:
            df_kwargs= dict( notebook=True, 
                    max_rows=10, 
                    index=False,
                    show_dimensions=False, 
                    justify='right',
                    float_format=lambda x: f'{x:.3f}',
                    )
            self.add_rep('DataFrame', DataFrameWrapper, df_kwargs)
            
        if plt:
            self.add_rep('Figure', FigureWrapper, dict(fig_folders=folders) )
                            

    @property
    def folders(self):
        return document_folders

    def __call__(self, vars):
        """for each value in the vars dict, replace it with a new object that
        implements return of appropriate HTML for the original object
        (Note uses the *class name*, which may not be unique, as a key)
        """
        for key,value in vars.items():

            new_class, kwargs = self.get(value.__class__.__name__, (None,None))
            
            if new_class:
                newvalue = new_class(value, vars, **kwargs)
                vars[key] = newvalue
                
    def test(self, var:'any object'):
        """Test replacement for a given value. print str(var) before and after replacement
        """
        _class = var.__class__
        _name = _class.__name__
        if _name not in self:
            print(f'no subsitution for class {_name}: "{var}"')
            return

        print(f'replacement: {self[_name]}')
        print(f'before: "{var}"')
        # make a simple vars dict: key is the variable name, value its object
        vars = {'x': var}
        self(vars)
        x = vars['x']
        print(f'after : "{x}"')
        return 

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
