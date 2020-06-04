import os, yaml
import inspect
import numpy as np

# generated from https://divtable.com/table-styler/
table_class = 'greyGridTable'
doc_head="""\
<html> 
<head> <title>Document list</title> 
<style type="text/css">
body, th, td {	font-family:verdana,arial,sans-serif;
font-size:10pt;
margin:50px;
background-color:white;
}
table.greyGridTable {
  border: 2px solid #FFFFFF;
  width: 80%;
  text-align: left;
  border-collapse: collapse;
}
table.greyGridTable td, table.greyGridTable th {
  border: 1px solid #FFFFFF;
  padding: 3px 4px;
}
table.greyGridTable tbody td {
  font-size: 13px;
}
table.greyGridTable td:nth-child(even) {
  background: #EBEBEB;
}
table.greyGridTable thead {
  background: #FFFFFF;
  border-bottom: 4px solid #333333;
}
table.greyGridTable thead th {
  font-size: 15px;
  font-weight: bold;
  color: #333333;
  text-align: left;
  border-left: 2px solid #333333;
}
table.greyGridTable thead th:first-child {
  border-left: none;
}

table.greyGridTable tfoot td {
  font-size: 14px;
}
</style> 
</head>
"""
doc_body_head="""
<h3>Documents</h3>
List of documents maintained here
"""
class DocIndex(dict ):

    def __init__(self, document):
        assert os.path.isdir(document), f'Expect a document folder, not {document}'
        self.docspath, _ = os.path.split(document)
        self.index_file = os.path.join(self.docspath, 'index.yaml')
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as stream:
                    id =  yaml.safe_load(stream)
                    self.update(id)
            except Exception as msg:
                raise Exception(f'Failed to parse {self.index_file}:\n{msg}')
    
    def as_dict(self):
        out = {}
        out.update(self)
        return out 
        
    def __str__(self):
        return str(self.as_dict())
     
    def save(self):
        # back it up first
        import shutil
        if os.path.exists(self.index_file):
            shutil.copyfile(self.index_file, self.index_file+'.bak')
        
        out = self.as_dict()
        with open(self.index_file, 'w') as stream:
            yaml.dump(out, stream)
            
    def to_html(self, filename=None,
                heads='name date title'.split(), 
                classname=table_class):
        
        if filename is None: 
            inspect.stack()[0].filename
            filename = os.path.join(self.docspath, 'index.html')
        doc = doc_head 
        doc+=f"""<h2>Jupydoc Documents</h2>
        List of documents at {docspath}<br><br>
        """
        doc+= f'<table class="{classname}">\n<thead>\n <tr>\n'
        for head in heads:
            doc+=f'  <th>{head}</th>\n'
        doc+=f' </tr>\n</thead>\n<tbody>\n'
        
        # sort dates
        keys = [ k for k in self.keys() if k and self[k]]
        dates = [self[x].get('date','0000-00-00 00:00') for x in keys ]
        sortedkeys = np.array(keys)[np.flipud(np.argsort(dates))]
        
        for name in sortedkeys:
            value = self[name]
            if value is None or type(value)!=dict :
                continue
            doc +=f' <tr>\n  <td><a href="{name}/index.html?skipDecoration">{name}</a></td>\n'
            for key in heads[1:]:
                 doc +=f'  <td>{value[key]}</td>\n'
            doc +=f' </tr>\n'
        doc += f'</tbody></table>\n</body>'
        with open(filename, 'w') as out:
            out.write(doc)
        print(f'Wrote file {filename}')
        return
######################################################################    
# globals
docspath=''
module_name = '' # must be set from module
submodule_names = [] # set to a list of submodule names exported by package
submodule_info ={}

#print('indexer reloaded!')

def set_paths(path:'', module=None, submodules=None):
    """ Set globals: the  module variable for use by Indexer 
    """
    import importlib
    global docspath, module_name, submodule_names, submodule_info
    
    # set default docspath
    docspath = os.path.realpath(path)
    if module is None: return

    module_name = module
    submodule_names = submodules
    
    # import each submodule as a check, get each declared docpath if any 
    for submodule_name in submodule_names:
        submodule = importlib.import_module('.'+submodule_name, package=module_name)
        if hasattr(submodule, 'docspath'):
            submodule_docspath = submodule.docspath   
            if not os.path.isdir(submodule_docspath):
                print(f'Warning: Did not find a folder {subdocspath} from {submodule_name}')
        else:
            submudule_docspath = docspath
            
        if not hasattr(submodule, '__all__') or not submodule.__all__:
            print(f'submodule {submodule_name} did not declare any exported classes with "__all__"')
            continue
        export_names = submodule.__all__
        assert type(export_names[0])==str, '__all__ not a list of strings?'
        submodule_info[submodule_name]=dict(docspath=os.path.abspath(submodule_docspath),
                                           export_names=export_names,)
        
    return  


def get_info():
    return submodule_info

def get_path(docname:'submodule_name.class_name')->'folder name to store document':
    submodule,classname = docname.split('.')
    info = submodule_info[submodule]
    assert classname in info['export_names']
    return submodule_info[submodule]['docspath']+'/'+docname

def get_module_name():
    return module_name
    
# function that will return any document class by name
def get_doc(name:'module.class'='', 
           )->'the document class':
    import os, importlib
    global docspath,  submodule_docspath
    
    #module_name,submodule_names = get_module_names()
    submodule_names = get_info().keys()
    if not name:
        print(f'submodules: {submodule_names} ')
        for sname in submodule_names:
            db = submodule_docspath.get(sname, docspath)
            print(f'{sname} {db}')
        return
    sname = name.split('.')
    submodule_name, class_name = (sname[0],'') if len(sname)<2 else sname
    
    info = get_info()
    submodule_name, class_name = name.split('.')
    
    # import the module, get its declared docpath if any
    module = importlib.import_module('.'+submodule_name, package=get_module_name())
    
    subdocspath = get_path(name)
    #print(f'Found {submodule_name}.docspath: {subdocspath}')
    
    export_names = module.__all__
    assert type(export_names[0])==str, '__all__ not a list of strings?'
    if not class_name:
        print(f'submodule {submodule_name} has document classes {export_names}')
        return      
    assert class_name in export_names, f'class name "{class_name}" not found in {export_names}'
    r =  eval('module'+'.'+class_name)
    return r