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
  width: 90%;
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

    def __init__(self, document, verbose=False):
        assert os.path.isdir(document), f'Expect a document folder, not {document}'
        self.docspath, _ = os.path.split(document)
        self.verbose=verbose
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
        List of documents at {self.docspath}<br><br>
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
        if self.verbose: print(f'Wrote file {filename}')
        return
######################################################################    
# global dict with everything to preserve between calls
# set by set_docs_info

docs_info={}

def get_docs_info():
    return docs_info


def set_docs_info( module_name, path='', verbose=False):
    """ Set the global dict docs_info: for use by Indexer 
    """
    import importlib
    
    info={}

    info['module']=module_name
    info['docspath'] = os.path.realpath(path)
    module = importlib.import_module(module_name)
    submodule_names = module.__all__
    docspath = module.docspath
    if verbose: print(f'Found submodules {submodule_names}')
    subs=info['submodule'] = {}

    # import each submodule as a check, get each declared docpath if any 
    for submodule_name in submodule_names:
        if verbose: print(f'checking {submodule_name}...', end='')
        
        submodule = importlib.import_module('.'+submodule_name, package=module_name)
        importlib.reload(submodule)
        if hasattr(submodule, 'docspath'):
            submodule_docspath = submodule.docspath   
            if not os.path.isdir(submodule_docspath):
                print(f'Warning: Did not find a folder'\
                      f' {submodule_docspath} from {submodule_name}')
        else:
            submodule_docspath = docspath
            
        if not hasattr(submodule, '__all__') or not submodule.__all__:
            if verbose: print(f'submodule {submodule_name} did not declare any'\
                  f'exported classes with "__all__"')
            continue
        export_names = submodule.__all__
        assert type(export_names[0])==str, '__all__ not a list of strings?'
        if verbose: print(f'setting {submodule_name}')
        subs[submodule_name]=dict(docspath=os.path.abspath(submodule_docspath),
                                           export_names=export_names,)
    info['submodule']=subs
    info['current_module'] =None  
    
    # set the global
    global docs_info
    docs_info=info
    return  info

def lookup(name):
    t = name.split('.')
    if len(t)>1:
        module_name,class_name = t 
    else:
        module_name, class_name = None, t[0]

    info = docs_info['submodule'] #get_info()
    if module_name: 
        module_info = info.get(module_name, None)
        if not module_info: return None
        if class_name not in module_info['export_names']: return None
        return module_name, class_name, module_info.get('docspath', '')

    for module_name, v  in info.items():    
        if class_name in  v['export_names']:
            return module_name, class_name, v.get('docspath','')
    return None

def get_class(submodule_name, class_name, reload=True, verbose=False):

    # for a submodule name, and a class name that it exposes, return the class object
    # reload the module under the submodule that contains the class source if requested
    
    import sys, importlib
    submodule = sys.modules[submodule_name]
    cls = eval(f'submodule.{class_name}')
    src_module_name = cls.__module__     
    src_module = sys.modules[src_module_name] 
    
    if reload: 
        if verbose: print(f'Reloading {src_module}')
        importlib.reload(src_module)
        # new versions of src_module and the class
        src_module = sys.modules[src_module_name]
        cls = eval(f'src_module.{class_name}')
    return  cls

def get_doc(
        name:'"" or "module" or "module.class"'='', 
        noreload:'flag to not reload'=False,
        verbose=False,
        )->'the document class':
    
    import os, sys, importlib
    global docs_info
    if verbose:print(f'Called with {name}')
    
    # parse the name: '' | 'class' | submdule.class
    t = lookup(name)
    
    if not t:
        info = docs_info
        print(f'Available document classes: {info}')
        return
   
    submodule_name, class_name, docspath= t
    
    
    docs_info['docspath'] = docspath  # give access to current class's submodule spec
    module_name = docs_info['module'] 
    if verbose: print(f'Processing {module_name}.{submodule_name}.{class_name},'\
                      f'\n   docspath={docspath}')
 
    to_reload = not noreload and  docs_info['current_module']
    reloaded = '(reloaded)' if to_reload else ''
    
    # get the class object
    cls = get_class(
            module_name+'.'+submodule_name, 
            class_name, 
            reload= to_reload, verbose=verbose)
    # if called again, maybe will reload
    docs_info['current_module'] = cls.__module__
    
    if verbose: print(f'Got the class {cls}')  
    print(f'Returning  {reloaded} {cls.__module__}.{class_name}')
    
    return cls
