"""Generate documents for Jupyterlab display 
"""

import os, inspect, datetime
import yaml

from .helpers import doc_formatter, md_to_html
from .replacer import ObjectReplacer

## special style stuff or start of document
jupydoc_css =\
"""
<style >
 .jupydoc_fig { text-align: center; }
 .errorText {color:red;}
</style>
"""

class Publisher(object):
    """
    Base class for generating a document in Jupyter/IPython.
    A subclass must run `super().__init__(**kwargs)`. Then any member function that calls self.publishme()
    will have its docstring processed.
    """

    def __init__(self, 
             docpath:'if set, save() will write the accumulated output to an HTML document index.html in this folder'='', 
             no_display:'set True to disable IPython display output'=False,
             **kwargs
            ):
        """

        """
        
        # document information from kwargs if set, or yaml-format class docsting
        docstring = self.__doc__
        doc_info = yaml.safe_load(docstring) if docstring else {} 
        if not type(doc_info)==dict: doc_info={}
        self.title_info = kwargs.get('title_info', 
                                    dict(title=doc_info.pop('title', ''),
                                        author=doc_info.pop('author', ''),
                                        abstract=doc_info.pop('abstract', ''),
                                        )
                              )
        self.section_names=kwargs.get('section_names',
                                      doc_info.pop('sections','title_page')
                                     ).split()    
        self.info = doc_info # any other stuff available to user
        self.section_functions = []
        for name in self.section_names:
            try:
                self.section_functions.append(eval(f'self.{name}'))
            except Exception as err:
                raise Exception(f'{err}: Section name {name} not defined?')

        # output, display stuff
        self.docpath = docpath
        self._no_display = no_display
        self.display_on = not no_display # user can set
        
        # predefind symbols for convenience
        self.predefined= dict(
                margin_left='<p style="margin-left: 5%">',  
                indent='<p style="margin-left: 5%">',
                endp='</p>',
            )
        self.date=str(datetime.datetime.now())[:16]
        self.clear()
        
        #  always saving figures and images locally, also to document destination if set
        fig_folders = ['.']
        if self.docpath:   
            fig_folders.append(self.docpath)
             
        # instantiate the object replacer: set "fig_folder" for the Figure processing, and set the first figure number
        rp =self.object_replacer = ObjectReplacer(folders=fig_folders)
#         assert 'Figure' in rp, 'Expected the replacement object to support plt.Figure'
#         #upate the qwargs for the Figure processing
#         rp['Figure'][1].update(fig_folders = fig_folders)
    
    def __repr__(self):
        return f'jupydoc.Publisher subclass "{self.__class__.__name__}", title "{self.title_info["title"]}"'

    def _publish(self, text):
        """ add text to the document, display with IPython if set"""        
        import IPython.display as display #only dependence on IPython
        self.data = self.data + '\n\n' + text
         
        if self.display_on: 
            # perhaps not generating display for this section
            display.display(display.Markdown(text)) 
        
    def title_page(self):
        """
        <header>
        <h1>{title}</h1>
        <h2>{subtitle}</h2>
        {date_line} 
        {author_line}
        {abstract_text}
        </header>
        """
        if self.title_info:
            ti = self.title_info
            ts=ti.get('title', 'untitled?').split('\n')
            ts=self.title_info['title'].split('\n')
            title=ts[0]
            subtitle = '' if len(ts)==1 else ' '.join(ts[1:])
            author=ti.get('author', '').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')
            abstract=ti.get('abstract', '')
            abstract_text=f'<p style="margint: 0% 10%" >ABSTRACT: {abstract}</p>' if abstract else ''
            author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
            title_line=f'<h1 text-align:center;>{title}</h1>' if title else '*no title*' 
            subtitle_line=f'<H2> {subtitle}</H2>' if subtitle else '' 
        else:
            # No info: only date
            title=subtitle=date_line=author_line=abstract_text=''
            
        date_line=f'<p style="text-align: right;">{self.date}</p>'
        self.publishme()
        self.section_number=0
            
    def markdown(self, text:"markdown text to add to document",
                 indent:'left margin in percent'=None,
                 clean:"if set, run inspect.cleandoc" =True,
                )->'markdown':
        """Add md text to the display"""
        if indent:
            text = f'<p style="margin-left: [indent]%" {text}</p>'
        if clean:
            text= inspect.cleandoc(text)
        self._publish(text)

    def publishme(self, 
                  section_title:'Optional title for the section'=None, 
                  **kwargs:'additional variable definitions',
                 )->None:
        """
        """
        import inspect
        
        self.section_title = section_title
         
        # use inspect to get caller frame, the function name, locals dict, and doc
        back =inspect.currentframe().f_back
        name= self.name = inspect.getframeinfo(back).function
        locs = inspect.getargvalues(back).locals
        doc = inspect.getdoc(eval(f'self.{name}'))
        
        # check for first non-blank line follwed by a blank line to define title
        if section_title is None:
            doc_lines = doc.split('\n')
            first = 0 if  doc_lines[0] else 1
            if doc_lines[first+1]=='':
                section_title = doc_lines[0]
                doc = '\n'.join(doc_lines[first+2:])

        # see if this is a subsection by checking the name of the calling function
        back2 = back.f_back
        self.prev_name = inspect.getframeinfo(back2).function
        
        # is this a section?
        if self.prev_name!=self.section_name:
            # no: initiize for a new section
            self.section_name=name  
            self.section_number +=1
            self.subsection_number=0
            hchars ='##'
            hnumber=f'{self.section_number:}'
            
            # create variable dictionary: predefined, symbol table from calling function, kwargs
            vars = self.predefined.copy()
            vars.update(locs)
            vars.update(kwargs)
            self._saved_symbols = vars
        else: 
            # yes: this name is the saved section name
            self.subsection_number +=1
            hchars = '###'
            hnumber=f'{self.section_number:}.{self.subsection_number}'
            
            # add the locals and kwargs to section symbol list
            vars = self._saved_symbols.copy()
            vars.update(locs)
            vars.update(kwargs)
 
        # run the object replacer
        self.object_replacer(vars)
  
        # Now use the helper function to the formatting, replace {xx} if xx is recognized
        md_data = doc_formatter(  doc,   vars,  )
        
        # prepend section or subsection header if requested
        if section_title:
            header = f'\n\n{hchars} {hnumber}. {section_title}\n\n'                
            md_data = header + md_data
            
        # send it off
        self._publish(md_data)
       
    def clear(self):
        self.data=jupydoc_css
        self._fignum=self.section_number=self.subsection_number=0
        self.section_name='' 
        self.class_name=self.__class__.__name__


    def __call__(self, start=None, stop=None, 
                 display_only:'set to only use the display'=False):
        """assemble and save the document if docpath is set
        Choose a range of sections to display in the notebook
        """
        assert hasattr(self, 'section_names') and len(self.section_names)>0,\
            'Must be a least one section in section_names'
        
        def run(start, stop=None):

            if start and start<0: start+=len(self.section_names)
            if stop is None:
                stop=start
            elif stop<0: stop+=len(self.section_names)

            # assemble the document by calling all the section functions, displaying the selected subset
            # close, and save it if self.docpath is set
            self.clear()
            self.display_on=False

            for i,function in enumerate(self.section_functions):
                if i==start:
                    self.display_on=True
                function()
                if i==stop: self.display_on=False

        if type(start)==str:
            start=start.strip()
            if start=='all':
                run(start=0,stop=-1) # display all
            else:
                names = self.section_names
                assert start in names, f'Name {start} not in lins of section names, {names}'
                run(names.index(start))
        else:
            if start is None:start=stop=len(self.section_names) #display none
            run(start,stop=stop)

        if not display_only:
            self.save()
    
    def save(self):
        """ Create Web document
        """
        if not self.docpath: 
            self.markdown("""
            ---
            Document not saved.""")
            return
        title = self.title_info.get('title', '(untitled)')

        source_text = self.info.get('filename', '')

        self.markdown(f"""
            ---
            Document "{title}", created using [jupydoc](http://github.com/tburnett/jupydoc)<br> 
            created by class <samp>{self.__class__.__name__}</samp> {source_text}<br>
            saved to <samp>{self.docpath}</samp>
            """)
        
        os.makedirs(os.path.join(self.docpath), exist_ok=True)
        md_to_html(self.data, os.path.join(self.docpath,'index.html'), title) 
         
        print(f'\n------\nsaved to  "{self.docpath}"')
        
     
    def image(self, filename, 
              caption=None, 
              width=None,height=None, 
              browser_subfolder:'The subfolder in the HTML location'='images',
              image_extensions=['.png', '.jpg', '.gif', '.jpeg'],
              fig_style='jupydoc_fig',
             )->'a JupydocImage object that generates HTML':
        error=''
        filename = os.path.expandvars(filename)
        if not os.path.isfile(filename):
            error = f'File {filename} not found'
        else:
            _, ext = os.path.splitext(filename)
            if not ext in image_extensions:
                error = f'File {filename} not an image? "{ext}" not in {image_extensions}' 

        class JupydocImage(object):
            def __init__(self):
                self.error = error
                if self.error: 
                    return
                _, self.name=os.path.split(filename) 
                self.browser_subfolder = browser_subfolder

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
                    return f'<p class="errorText"> {self.error}</p'
                h = '' if not height else f'height={height}'
                w  = '' if not width  else f'width={width}'
                browser_fn = self.browser_subfolder+'/'+self.name
                return f'<div class="{fig_style}"><figure> <img src="{browser_fn}" {h} {w}'\
                    f'  alt="Image {self.name} at {browser_fn}">'\
                    f' \n  <figcaption>{caption}</figcaption>'\
                    '\n</figure></div>\n'
        return JupydocImage()        
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