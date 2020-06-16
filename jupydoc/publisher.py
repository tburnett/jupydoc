"""Generate documents for Jupyterlab display 
"""

import os, inspect, datetime


from .helpers import doc_formatter, md_to_html
from .replacer import ObjectReplacer

## special style stuff or start of document
jupydoc_css =\
"""
<style >
 .jupydoc_fig { text-align: center; }
 .errorText {color:red;}
  hr.thick{border-top: 3px solid black;}
</style>
"""

class Publisher(object):
    """
    Base class for generating a document in Jupyter/IPython.
    A subclass must run `super().__init__(**kwargs)`. Then any member function that calls self.publishme()
    will have its docstring processed.
    """

    def __init__(self, 
             docpath:'if set, save() will write the output folder to this folder'='',
             docname:'if set, will be the name of the document folder; otherwise use its class name'='', 
             **kwargs
            ):
        """
        """
         
        # output, display stuff
        if docpath:
            if not os.path.isdir(docpath):
                raise Exception('{docpath} is not an existing folder')
        
        self.docpath = docpath
        module = self.__module__
        self.docname = docname or (module+'.' if module!='__main__' else '')+self.__class__.__name__

        if docpath:

            fp = os.path.abspath(os.path.join(docpath, self.docname))
            os.makedirs(fp, exist_ok=True)
        
        # a list for saving figures and or images -- will include '.' if interactive
        self.doc_folders = [fp, '.'] if docpath else ['.']
        
        self.object_replacer = ObjectReplacer(folders = self.doc_folders)
        
        # predefind symbols for convenience
        self.predefined= dict(
                margin_left='<p style="margin-left: 5%">',  
                indent='<p style="margin-left: 5%">',
                endp='</p>',
                linkto_top = '<a href="top">top</a>'
            )
        self.date=str(datetime.datetime.now())[:16]
        self.display_on=True
        self.clear()


    def __repr__(self):
        title = self.doc_info.get('title', '(no title)')
        return f'jupydoc.Publisher subclass "{self.__class__.__name__}", title {title}'
        
    def publishme(self,  **kwargs:'additional variable definitions',
                 )->None:
        """
        """
        import inspect

        # use inspect to get caller frame, the function name, locals dict, and doc
        back =inspect.currentframe().f_back
        name= self.name = inspect.getframeinfo(back).function
        locs = inspect.getargvalues(back).locals
        doc = inspect.getdoc(eval(f'self.{name}'))
 
        # symbol table: predefinded + locals + kwargs
        vars = self.predefined.copy()

        # hook to modify either, perhaps prepend to doc, more vars
        doc  = self.process_doc(doc, vars)


        # add locals and kwargs, run the object replacer
        vars.update(locs)
        vars.update(kwargs)
        self.object_replacer(vars)

        # Now use the helper function to the formatting, replace {xx} if xx is recognized
        md_data = doc_formatter(  doc,   vars,  )
        self.data = self.data + '\n\n' + md_data

        # perhaps display
        self._display(md_data)
         
    def _display(self, md_data):
        import IPython.display as display #only dependence on IPython

        if self.display_on:
            display.display(display.Markdown(md_data)) 

    def clear(self):
        self.data=jupydoc_css + '<a id="top"></a>'
        self._fignum = 0

    def process_doc(self, doc, vars):
        # do nothing in this class
        return doc

    def save(self):
        """ Create Web document
        """
        if not self.docpath: 
            self.markdown("""
            ---
            Document not saved.""")
            return
        fullpath = os.path.abspath(os.path.join(self.docpath, self.docname))

        self.markdown(
            f'<hr class="thick">\nDocument "{self.docname}", created using [jupydoc](http://github.com/tburnett/jupydoc)<br>'\
            #f'\nCreated by class <samp>{self.__class__.__name__}</samp> {source_text}<br>'\
            f'\nSaved to <samp>{fullpath})</samp>'
            )
        
        md_to_html(self.data, os.path.join(fullpath,'index.html'), title=self.docname) 
         
        print(f'\n------\nsaved to  "{fullpath}"')
             
    def markdown(self, text:"markdown text to add to document",
                 indent:'left margin in percent'=None,
                 clean:"if set, run inspect.cleandoc" =True,
                )->'markdown':
        """Add md text to the display"""
        if indent:
            text = f'<p style="margin-left: [indent]%" {text}</p>'
        if clean:
            text= inspect.cleandoc(text)
        self.data = self.data +'\n\n'+ text   
     
    def image(self, filename, 
              caption='', 
              width=None,height=None, 
              browser_subfolder:'The subfolder in the HTML location'='images',
              image_extensions=['.png', '.jpg', '.gif', '.jpeg'],
              fig_style='jupydoc_fig',
             )->'a JupydocImage object that generates HTML':
        error=''
        filename = os.path.expandvars(filename)
        if not os.path.isfile(filename):
            error = f'Image file {filename} not found.'
        else:
            _, ext = os.path.splitext(filename)
            if not ext in image_extensions:
                error = f'File {filename} not an image? "{ext}" not in {image_extensions}' 
            self.docpath

        class JupydocImage(object):
            def __init__(self, folders):
                self.error = error
                if self.error: 
                    return
                _, self.name=os.path.split(filename) 
                self.set_browser_folder(browser_subfolder)
                for folder in folders:
                    self.saveto(folder)
                
            def set_browser_folder(self, folder):
                self.browser_subfolder = folder

            def saveto(self, whereto):
                import shutil
                if self.error: return
                full_path = os.path.join(whereto, self.browser_subfolder)
                os.makedirs(full_path, exist_ok=True)
                shutil.copyfile(filename, os.path.join(full_path,self.name) )

            def __str__(self):
                if self.error:
                    return f'<p class="errorText"> <b>{self.error}</b></p>'
                h = '' if not height else f'height={height}'
                w  = '' if not width  else f'width={width}'
                browser_fn = self.browser_subfolder+'/'+self.name
                return f'<div class="{fig_style}"><figure> <img src="{browser_fn}" {h} {w}'\
                    f'  alt="Image {self.name} at {browser_fn}">'\
                    f' \n  <figcaption>{caption}</figcaption>'\
                    '\n</figure></div>\n'
        r = JupydocImage(folders = self.doc_folders) 
        return r       
    #-----------------------------------------------------------
    # User convenience functions

    def newfignum(self) -> "a new figure number":
        self._fignum+=1
        return self._fignum
        
    def monospace(self, text:'Either a string, or an object', 
                  indent='5%')->str:

        text = str(text).replace('\n', '<br>')
        return f'<p style="margin-left: {indent}"><samp>{text}</samp></p>'
    
    def add_caption(self, 
                text:'text of caption for most recent figure'):
        fig = plt.gcf()
        fig.caption=f'Fig. {fig.number}.{text}'