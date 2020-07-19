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
 
        if not doc_dict: return
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
        self._newsection = j==0
        if self._newsection:
            # New section: link to top unless at the top, set anchor with function name
            hdr = f'<a id="{f}"></a>'
            if i>0: hdr +='\n<h2>{}</h2>\n\n' 
        else:
            hdr = f'<h3 id="{f}">'+ '{} </h3>\n'
        self.section_header = hdr 
        self.section_trailer = '' 
        
        # increment either index
        m = len(self.sections[k])
        i, j =  (i, j+1) if j<m else (i+1, 0 )
        self.current_index=[i,j]
        if j==0 and i>1: # end of a section
            self.section_trailer = '\n<p style="text-align: right;"><a href="#top">top</a></p>\n'

        return ret

    def annotate(self, header_text, doc):
        i, j = self.current_index
        # Can't get this to work since MD puts in <p> tags 
        # file://wsl%24/Ubuntu-20.04/home/burnett/work/jupydoc/notebooks/collapsile.css
        # hdr='' if (i>1 or j>0) else \
        #     '<link rel="stylesheet" href="../../collapsible.css">'\
        #     '\n<script src="../../collapsible.js"></script>\n'
        hdr=''
        return hdr+self.section_header.format(header_text)  +doc + self.section_trailer 
  
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

    def is_selected(self, sid:'section id', fname:'function name'):
        import numbers

        sel = getattr(self, '_selection', None)

        if sel=='all': return True
        if sel is None :
            return False
        if isinstance(sel, numbers.Real):
            select_section = round(sel*10) % 10 ==0
            if select_section:
                n =len(self.section_names)
                isid = int(sid)
                return sel==isid or (sel>=n and isid==n-1)
            # a subsection: either exact, of get last if too big
            i = int(sel); j = int(10*sel-i)
            m = len(self.sections[self.section_names[i]] )
            t = i+m/10 #max sub number
            return  sid==sel or sel>t and sid==t 
        else:
            return fname==sel

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pformat(self)

#-----------------------------------------------------------

def doc_formatter(
        text:'text string to process',
        vars:'variable dict'={}, 
        mimetype='text/markdown',
    )->'MimeBundleObject':
    # Returns an object that can be displayed by IPython, interpreted as the mimetype

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
               
    docx = Formatter().vformat(text+'\n', vars)  if vars else text     
    # enhances this: docx = text.format(**vars)

    class MimeBundleObject(object):
        def _repr_mimebundle_(self, include=None, exclude=None):
            return {mimetype: docx}

    return MimeBundleObject()

def md_to_html(output, filename, title='jupydoc'):
    """write nbconverted markdown to a file 
    
    parameters
    ----------
    output : string | tuple | IPython.utils.capture.CapturedIO object
        if not a string extract the markdown from each of the outputs list 
    """
    class Dict(dict):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.update(kwargs)
       
    if type(output)==str:
        # just a markdown string
        cells= [Dict(cell_type="markdown", 
                         metadata={}, 
                         source=output,
                        )
                   ]
   
    elif type(output)==tuple:
        # a tuple of displayable objects
        cells = []
        for obj in output:
            mimetype, text = list(obj._repr_mimebundle_().items())[0]
            assert mimetype[:5]=='text/', f'Wrong mimetype: {mimetype}'
            cells.append(
                Dict(cell_type=mimetype[5:],
                    metadata={},
                    source = text,
                )
            )

    elif hasattr(output, 'outputs'):
        # a CapturedIO object? assume all markdwon si guess (never used this)
        text=''
        for t in output.outputs:            
            text += '\n\n'+t.data['text/markdown']
        cells= [Dict(cell_type="markdown", 
                         metadata={}, 
                         source=text,
                        )
                   ]
    else:
        raise Exception(f'output not recognized: {output.__class__} not a string, tuple, or CapturedIO object?')

    nb = Dict(
            cells=cells,
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