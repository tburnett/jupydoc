"""Generate documents for Jupyterlab display 
"""

import os, sys, inspect, datetime

from .helpers import doc_formatter, md_to_html
from .replacer import ObjectReplacer

## special style stuff at start of document
jupydoc_css =\
"""
<style type="text/css">
 .jupydoc_fig { text-align: center; }
 .errorText {color:red;}
  hr.thick{border-top: 3px solid black;}  
 .rendered_html tr, .rendered_html th, .rendered_html td {
    text-align: left;
    vertical-align: top;
}
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
             **kwargs:'should be none',
            ):
        """
        """
        if kwargs:
            print(f'Publisher: unexpected kwargs: {kwargs}', file=sys.stderr)
         
        # output, display stuff
        if docpath:
            if docpath[0]=='$': 
                docpath = os.path.expandvars(docpath)
            if not os.path.isdir(docpath):
                print(f'Publisher: {docpath} is not an existing folder', file=sys.stderr)
                docpath=''

        self.docpath = docpath
        module = self.__module__
        self.docname = docname or (module+'.' if module!='__main__' else '')+self.__class__.__name__

        # if the name was compound, make version available, allowing multiple periods
        i = self.docname.find('.')
        self.version = '' if i<1 else self.docname[i+1:]

        if docpath:
            fp = os.path.abspath(os.path.join(docpath, self.docname))
        
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
        # make current date, and this file's path and name avaailable
        self.date=str(datetime.datetime.now())[:16]
        full_filename = inspect.stack()[0][1]
        self.path, self.filename = os.path.split(full_filename)

        self.display_on=True
        self.clear()

    def _repr_mimebundle_(self, include=None, exclude=None):
        if self._has_data:
            return {'text/markdown': self.data}
        return {'text/plain': str(self) }

    def publishme(self,  
                 **kwargs:'additional variable definitions',
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

        # Now use the helper function to do the formatting, replacing {xx} if xx is recognized
        md_data = doc_formatter(  doc,   vars,  )

        # self.data = self.data + '\n\n' + md_data._repr_mimebundle_()['text/markdown']
        # add this displayable object to the output tuple
        self.data += (md_data,)

        # perhaps display it
        self._display(md_data)
         
    def _display(self, md_data):
        import IPython.display as display #only explicit dependence on IPython

        if self.display_on:
            #display.display(display.Markdown(md_data)) 
            display.display( md_data )
            self._has_data = True

    def clear(self):
        # start the objs tuple 
        self.data = (doc_formatter(jupydoc_css + '\n<a id="top"></a>', ),)
        self._fignum = 0 # local convenience, not true 
        self._has_data = False
        self.object_replacer.clear() # for fig number at least

    def process_doc(self, doc, vars):
        # do nothing in this class
        return doc

    def save(self, append='', quiet=False):
        """ Create Web document
        """
        if not self.docpath: 
            self.markdown("""
            ---
            Document not saved.""")
            return
        fullpath = os.path.abspath(self.docpath)
        if self.docname!='Index':
            fullpath = os.path.join(fullpath, self.docname)

        if hasattr(self, 'docman'):
            module = self.docman.lookup_module.get(self.docname, 'not found?')
            from_file = f' From module <samp>{module}.py</samp>,'
        else: from_file=''
        docname = f'Document {self.docname}' if self.docname else 'Index document'
        self.markdown(
            f'<hr class="thick">\n{docname}, {from_file}'\
            f' created using [jupydoc](http://github.com/tburnett/jupydoc) on {self.date}'
            f'<br>Saved to <samp>{fullpath}</samp>'
            )
        if append:
            self.markdown(append, clean=False)

        html_title = self.docname if self.docname !='Index' else f'{os.path.split(self.docpath)[-1]} index'
        md_to_html(self.data, os.path.join(fullpath,'index.html'), title=html_title) 
         
        if not quiet:
            t = f'Document {self.docname}' if self.docname else 'Index'
            print(f'\n------\n{t} saved to "{fullpath}"')
             
    def markdown(self, text:"markdown text to add to document",
                 indent:'left margin in percent'=None,
                 clean:"if set, run inspect.cleandoc" =True,
                )->'markdown':
        """Add md text to the display"""
        if indent:
            text = f'<p style="margin-left: [indent]%" {text}</p>'
        if clean:
            text= inspect.cleandoc(text)
        self.data  += (doc_formatter( text ) ,)

    # disable for now--couidn't make it work
    # def html(self, text:'raw HTML text to add to document',
    #     )->'HTML':
    #     self.data += (doc_formatter(text, mimetype='text/html'),)

    def image(self, filename, 
              caption='', 
              width=None,height=None, 
              browser_subfolder:'The subfolder in the HTML location'='images',
              image_extensions=['.png', '.jpg', '.gif', '.jpeg'],
              fig_style='jupydoc_fig',
              )->'a JupydocImage object that generates HTML':
        error=''
        image_path = getattr(self, 'image_folder', self.path)
        if image_path[0]=='$':
            image_path = os.path.expandvars(image_path)
        filename = os.path.expandvars(filename)
        # Get, and increment, current figure number, prepend to caption.
        self.object_replacer.figure_number +=1
        fignum =  self.object_replacer.figure_number
        caption = f'<b>Figure {fignum}</b>. '+caption

        if not os.path.isfile(filename):
            filename = os.path.join(image_path, filename)
            if not os.path.isfile(filename):
                error = f'Image file {filename} not found.'
                print(error, sys.stderr)
        if not error:
            _, ext = os.path.splitext(filename)
            if not ext in image_extensions:
                error = f'File {filename} not an image? "{ext}" not in {image_extensions}' 
                print(error, sys.stderr)


        class JupydocImage(object):
            def __init__(self, folders):
                self.error = error
                self.fignum = fignum
                if self.error: 
                    return
                _, name=os.path.split(filename) 
                # make tne name unique by appending current fig number
                self.name = name.replace('.', f'_fig_{fignum:02d}.')
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
                return\
                    f'<div class="{fig_style}">'\
                    f' <a href="{browser_fn}">'\
                     '  <figure>'\
                    f'    <img src="{browser_fn}" {h} {w}'\
                    f'       alt="Image {self.name} at {browser_fn}">'\
                    f'\n  <figcaption>{caption}</figcaption>'\
                    '</figure></a></div>\n'
        r = JupydocImage(folders = self.doc_folders) 
        return r       
    
    def figure(self, fig, caption=None, width=None):
        """convenient way to add caption and width attributes
        """
        assert fig.__class__.__name__=='Figure', 'Expect fig to be a Figure'
        if caption: fig.caption=caption
        if width: fig.width=width
        return fig
    #-----------------------------------------------------------
    # User convenience functions

    def newfignum(self) -> "a new figure number":
        self._fignum+=1
        return self._fignum
        
    def monospace(self, text:'Either a string, or an object',
                    summary:'string for <details>'=None,
                    open:'initially show details'=False, 
                    indent='5%',
                  )->str:

        text = str(text).replace('\n', '<br>')
        out = f'<p style="margin-left: {indent}"><pre>{text}</pre></p>'
        if not summary:
            return out
        return f'<details {"open" if open else ""}><summary> {summary} </summary> {out} </details>'
    
    def shell(self, text:'a shell command ', monospace=True, **kwargs):
        import subprocess
        try:
            ret = subprocess.check_output([text], shell=True).decode('utf-8')
        except Exception as e:
            ret = f'Command {text} failed : {e}'
        return self.monospace(ret, **kwargs) if monospace else ret

    def capture_print(self, **kwargs):

        monospace = self.monospace

        class Capture_print(object):
            _stream = 'stdout'
            
            def __init__(self):
                import io
                self._new = io.StringIO()
                self._old = getattr(sys, self._stream)

            def __enter__(self):
                setattr(sys, self._stream, self._new)
                return self
            
            def __exit__(self, exctype, excinst, exctb):
                setattr(sys, self._stream, self._old)
                
            def __str__(self):
                return monospace(self._new.getvalue(), **kwargs)

        return Capture_print()

    def add_caption(self, 
                text:'text of caption for most recent figure'):
        fig = plt.gcf()
        fig.caption=f'Fig. {fig.number}.{text}'
