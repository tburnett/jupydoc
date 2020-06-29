"""
jupydoc helper class DocInfo, functions doc_formatter and md_to_html

"""
import string, pprint , collections
from nbconvert.exporters import  HTMLExporter

class DocInfo(collections.OrderedDict):
    """Manage the Jupydoc document structure

        From the docstring info, have the following:
        * title page: title, author, abstraact
        * sections and subsections:  
            dict keys: section names
                values: list of subsection names

        Provides a service as an iterator, returning the document sequence 
                (section number, subsection number, function name)

    """

    def __init__(self,
        doc_dict:'dict created by yaml from docstring',
        title_page_name='title_page',
        verify_list:'list of acceptable function names'=[]):
 
        for key in 'title author abstract'.split():
            self[key] = doc_dict.get(key, '')
        self['sections']= {title_page_name: []}

        if 'subsections' in doc_dict:
            # convert older format
            ss = doc_dict.get('sections','').split(); 
            sbs = doc_dict.get('subsections')
            d = self['sections']
            for s in ss:
                d[s] = sbs[s].split() if s in sbs else {} 
        else:
            # newer format: more readable, a bit more code
            section_string = doc_dict.get('sections', '')
            self.parse_section_string(section_string)
       
        self.__dict__.update(self)

    def __iter__(self):
        # set up iterator
        self.current_index = [0,0]
        self.section_names = list(self.sections.keys()) 
        return self

    def __next__(self):
        # set up next index
        # will return section id, function name, selection status
        i,j =  self.current_index
        if i==len(self.section_names):
            # a last link?
            raise StopIteration
        k = self.section_names[i] 
        f =  k if j==0 else self.sections[k][j-1]
        sid = i+j/10
        ret = (sid, f, self.is_selected(sid, f)) 

        # set section header containing anchor, perhaps link to top
        hdr=''
        if j==0:
            # New section: link to top unless at the top, set anchor with function name
            hdr = f'<a id="{f}"></a>'
        self.section_header = hdr
        self.section_trailer = '' if f=='title_page' else\
             '<p style="text-align: right;"><a href="#top">top</a></p>\n\n'
        
        # increment either index
        m = len(self.sections[k])
        i, j =  (i, j+1) if j<m else (i+1, 0 )
        self.current_index=[i,j]

        return ret            
    
    def parse_section_string(self, section_string):
        # remove commas, make sure [] will be tokens
        t = section_string.replace(',', ' ').replace('[', ' [ ').replace(']', ' ] ')
        tokens = t.split()
        subs = False
        for token in tokens:
            if   token=='[': 
                if subs:
                    raise Exception('Found unexpected "[" in section specification:'
                         'only one  level of subsections is supported')
                subs = True
            elif token==']': 
                if not subs:
                    raise Exception('Found unexpected "]" in section specification')
                subs = False 
            elif not subs  : current_section = self['sections'][token] = []
            else:            current_section.append(token)
    @property
    def names(self):
        nm = []
        for sect, subs in self['sections'].items():
            nm.append(sect)
            nm += subs
        return nm

    def set_selection(self, select:'"all" | name of function | section number | subsection number'):
        self._selection = select

    def is_selected(self, sid:'section id', name:'function name'):
        import numbers
        
        sel = getattr(self, '_selection', None)
        if sel=='all': return True
        if not sel:
            return False
        if isinstance(sel, numbers.Real):
            select_section = round(sel*10) % 10 ==0
            if select_section:
                n =len(self.section_names)
                return sel==int(sid) or sel>=n and int(sid)==n-1
            # a subsection: either exact, of get last if too big
            i = int(sel); j = int(10*sel-i)
            m = len(self.sections[self.section_names[i]] )
            t = i+m/10 #max sub number
            return  sid==sel or sel>t and sid==t 
        else:
            return name==sel

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pformat(self)

#-----------------------------------------------------------

def doc_formatter(
        text:'text string to process',
        vars:'variable dict', 
    )->str:
    
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
                return f'Docstring formatting failed: {msg.args[0]}'
        def get_value(self, key, args, kwargs):
            return kwargs.get(key, Formatter.Unformatted(key))

        def format_field(self, value, format_spec):
            if isinstance(value, Formatter.Unformatted):
                return value.format(format_spec)
            #print(f'\tformatting {value} with spec {format_spec}') #', object of class {eval(value).__class__}')
            return format(value, format_spec)
               
    docx = Formatter().vformat(text+'\n', vars)       
    # enhances this: docx = text.format(**vars)

    return docx

def md_to_html(output, filename, title='jupydoc'):
    """write nbconverted markdown to a file 
    
    parameters
    ----------
    output : string | IPython.utils.capture.CapturedIO object
        if not a string extract the markdown from each of the outputs list 
    """

       
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
def test_formatter():
    
    text="""
        input text: "{text}"
        
        resulting text: The value of x is: {x} 
        """
    vars  = dict(text=text,  x=99,)

    print(f'input to doc_display is the text:\n{text}')
    r = doc_formatter(text, vars)    
    print(f'Resulting string:\n "{r}"'  ) 
    
def parse_fields(string):
    # helper function to deal with blank line delimiters in a string
    lines = string.split('\n')
    slines = [x.strip() for x in lines]
    if len(slines[0])>0:
                slines = ['']+slines
    delim = []
    for i, x in enumerate(slines):
        if len(x)==0:
            delim.append(i)
    a = delim[0]
    fields = []
    for b in delim[1:]:
        fields.append('\n'.join(slines[a+1:b]))
        a=b
    return fields