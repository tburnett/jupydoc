"""Generate documents for Jupyterlab display 
"""

import os, inspect, datetime

from .helpers import doc_formatter, md_to_html
from .replacer import ObjectReplacer

class Publisher(object):
    """
    Base class for generating a document in Jupyter/IPython.
    A subclass must run `super().__init__()`. Then any member function that calls self.publishme()
    will have its docstring processed.
    """

    def __init__(self, 
             title_info:'Title, author,..'={'title':'Untitled'},
             doc_folder:'if set, save() will write the accumulated output to an HTML document file'='', 
             no_display:'set True to avoid Jupyter display output'=False,
             previous_fignumber:'to start at other than fig1'=0,
            ):
        """

        """
        self.title_info=title_info
        self.doc_folder = doc_folder 
        self._no_display = no_display
        self.display_on = not no_display # user can set
        self.predefined= dict(
                margin_left='<p style="margin-left: 5%">',  
                indent='<p style="margin-left: 5%">',
                endp='</p>',
            )
        self.date=str(datetime.datetime.now())[:16]
        self.clear()
        
        #  always saving figures locally, also to document destination if set
        fig_folders = ['.']
        if self.doc_folder:   
            fig_folders.append(self.doc_folder)
             
        # instantiate the object replacer: set "fig_folder" for the Figure processing, and set the first figure number
        rp =self.object_replacer = ObjectReplacer(previous_fignumber=previous_fignumber)
        assert 'Figure' in rp, 'Expected the replacement object to support plt.Figure'
        #upate the qwargs for the Figure processing
        rp['Figure'][1].update(fig_folders = fig_folders)
    
    def __repr__(self):
        return f'jupydoc.Publisher subclass "{self.__class__.__name__}", title "{self.title_info["title"]}"'

    def _publish(self, text):
        """ add text to the document, display with IPython if set"""        
        import IPython.display as display #only dependence on IPython
        self.data = self.data + '\n\n' + text
        
        if self.display_on: 
            # perhaps not generating display for this section
            display.display(display.Markdown(text)) 
        
    def title_page(self, text:'additional text'='', **kwargs):
        """
        {title_line}
        {date_line} 
        {subtitle_line}
        {author_line}
        {abstract_text}
        {text}
        """
        if self.title_info:
            ti = self.title_info
            title=ti.get('title', 'untitled?')
            subtitle=ti.get('subtitle', '')
            author=ti.get('author', '').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')
            abstract=ti.get('abstract', '')
            abstract_text=f'<p style="margint: 0% 10%" >ABSTRACT: {abstact}</p>' if abstract else ''
            author_line=f'<p style="text-align: center;" >{author}</p>' if author else ''
            title_line=f'<H1>{title}</H1>' if title else '*no title*' 
            subtitle_line=f'<p> {subtitle}</p>' if subtitle else '' 
        else:
            # No info: only date and text
            title_line=date_line=subtitle_line=abstract_text=''
            
        date_line=f'<p style="text-align: right;">{self.date}</p>'
        self.publishme(**kwargs)
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

    def newfignum(self) -> "a new figure number":
        self._fignum+=1
        return self._fignum
    
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
        self.data=''
        self._fignum=self.section_number=self.subsection_number=0
        self.section_name='' 
        self.class_name=self.__class__.__name__

    def save(self):
        """ Create Web document
        """
        if not self.doc_folder: 
            self.markdown("""
            ---
            Document not saved.""")
            return
        title = self.title_info.get('title', '(untitled)')
        self.markdown(f"""
            ---
            Document "{title}", created using [jupydoc](http://github.com/tburnett/jupydoc), saved to "{self.doc_folder}"'
            """)
        
        os.makedirs(os.path.join(self.doc_folder), exist_ok=True)
        md_to_html(self.data, os.path.join(self.doc_folder,'index.html'), title) 
        print(f'"{title}" saved to "{self.doc_folder}"')
        
             
    #-----------------------------------------------------------
    # Extra convenience functions to generate markdown

        
    def monospace(self, text:'Either a string, or an object', 
                  indent='5%')->str:

        text = str(text).replace('\n', '<br>')
        return f'<p style="margin-left: {indent}"><samp>{text}</samp></p>'
    