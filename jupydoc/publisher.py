"""Generate documents for Jupyterlab display 
"""

import os, inspect, datetime
import yaml

from .helpers import doc_formatter, md_to_html, DocInfo
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
             docpath:'if set, save() will write the accumulated output to an HTML document index.html in this folder'='', 
             no_display:'set True to disable IPython display output'=False,
             **kwargs
            ):
        """
        """
    
        docstring = self.__doc__ 
        try:
            doc_dict = yaml.safe_load(docstring) 
        except Exception as e:
            print(f'yaml error: {e.__class__.__name__}: {e.args}\n{docstring}')
            return
        
        self.doc_info = DocInfo(doc_dict)
        # parse_docstring( doc_dict)



        # output, display stuff
        self.docpath = docpath
        self.doc_folders = [docpath] if docpath else []

        self._no_display = no_display
        self.display_on = not no_display # user can set
        
        self.object_replacer = ObjectReplacer()
        
        # predefind symbols for convenience
        self.predefined= dict(
                margin_left='<p style="margin-left: 5%">',  
                indent='<p style="margin-left: 5%">',
                endp='</p>',
                linkto_top = '<a href="top">top</a>'
            )
        # add anchor links to section
        # for i,name in enumerate(self._section_names):
        #     self.predefined[f'linkto_{name}'] = '<a href="#{name}">Section {i}</a>'

        self.date=str(datetime.datetime.now())[:16]
        self.clear()
    
    def __repr__(self):
        return f'jupydoc.Publisher subclass "{self.__class__.__name__}", title "{self._title_info["title"]}"'

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
        <a id="title_page"> <h1>{title}</h1> </a>
        <h2>{subtitle}</h2>
        {date_line} 
        {author_line}
        {abstract_text}
        </header>
        """

        #ti = self._title_info
        ti = self.doc_info # has title, etc.
        ts=self.doc_info['title'].split('\n')
        title=ts[0]
        subtitle = '' if len(ts)==1 else ' '.join(ts[1:])
        author=  ti.get('author', '').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')
        abstract=ti.get('abstract', '')
        abstract_text=f'<p style="margint: 0% 10%" >{abstract}</p>' if abstract else ''
        author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
        title_line=f'<h1 text-align:center;>{title}</h1>' if title else '*no title*' 
        subtitle_line=f'<H2> {subtitle}</H2>' if subtitle else '' 

        date_line=f'<p style="text-align: right;">{self.date}</p>'
        self.publishme()

    def publishme(self,  **kwargs:'additional variable definitions',
                 )->None:
        """
        """
        import inspect
        self.section_number, self.subsection_number = self._current_index
    
        # use inspect to get caller frame, the function name, locals dict, and doc
        back =inspect.currentframe().f_back
        name= self.name = inspect.getframeinfo(back).function
        locs = inspect.getargvalues(back).locals
        doc = inspect.getdoc(eval(f'self.{name}'))
        
        # For sections, check for first non-blank line follwoed by a blank line to define title
        if self.section_number>0:
            doc_lines = doc.split('\n')
            if len(doc_lines)==0: 
                print(f'Warning: section {name} has no docstring')
                return
            first = 0 if  doc_lines[0] else 1
            section_title = doc_lines[0]
            if len(doc_lines)>1:            
                doc = '\n'.join(doc_lines[first+2:])
        else: self.section_title = ''

        
        # symbol table starts with these
        vars = self.predefined.copy()

        if self.section_number==0:
            # flag for title page
            section_title = ''
        
        elif  self.subsection_number==0:
            # a new non-title section
            hchars ='##'
            hnumber=f'{self.section_number:}'
               
            # for subsections, if any
            self._saved_symbols = vars
        else: 
            # a subsection
            hchars = '###'
            # maybe make numbering optional?
            hnumber=f'{self.section_number:}.{self.subsection_number}'
             # add the locals and kwargs to section symbol list
            vars.update(self._saved_symbols)

        # finally add local symbols and kwargs    
        vars.update(locs)
        vars.update(kwargs)

        # run the object replacer
        self.object_replacer(vars)

        # Now use the helper function to the formatting, replace {xx} if xx is recognized
        md_data = doc_formatter(  doc,   vars,  )
        
        # prepend section or subsection header if requested and not title
        if section_title:
            # save to index dict, put in section title, anchor for thise section
            # add header id, the name of this section
            header = f'\n\n{hchars} {hnumber} {section_title}\n\n'    
                      
            md_data = self.doc_info.section_header + header + md_data 
            
        # send it off
        self._publish(md_data)

    def clear(self):
        self.data=jupydoc_css + '<a id="top"></a>'
        self._fignum=self.section_number=self.subsection_number=0
        self.section_name='' 
        self.class_name=self.__class__.__name__

    def __call__(self, examine=None, 
                 display_only:'set to only use the display'=False,
                 ):
        """assemble and save the document if docpath is set
        Choose a range of sections to display in the notebook
        """
        self.doc_info.set_selection(examine)
        self.clear()
        for sid, function, selected in self.doc_info:
            #print(f'{selected:5} {sid},{f}')
            if not hasattr(self, function):
                raise Exception(f'Function {function} not defined')
            self._current_index = [int(sid), int(sid*10%10)]
            self.display_on = selected
            try:
                eval(f'self.{function}()')
            except Exception as e:
                print(f'Function {function} Failed: {e}')
            

 
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
        title = self.doc_info.get('title', '(untitled)')

        source_text = self.info.get('filename', '')

        self.markdown(
            f'<hr class="thick">\nDocument "{title}", created using [jupydoc](http://github.com/tburnett/jupydoc)<br>'\
            f'\nCreated by class <samp>{self.__class__.__name__}</samp> {source_text}<br>'\
            f'\nSaved to <samp>{self.docpath}</samp>'
            )
        
        os.makedirs(os.path.join(self.docpath), exist_ok=True)
        md_to_html(self.data, os.path.join(self.docpath,'index.html'), title) 
         
        print(f'\n------\nsaved to  "{self.docpath}"')
             
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