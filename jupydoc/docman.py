"""Document management for jupydoc 

"""
import os, sys, glob
import importlib 

from .indexer import DocIndex

# local globals    
verbose = False
packagepath= rootpath= ''
packages = modules = None

class Modules(dict):
    # manage list of modules, python files 
    def __init__(self):
        self.nsys = len(sys.modules)

    def user_modules(self):
        return list(sys.modules.keys())[self.nsys-1:]
        
    def check(self, path, m):
        # if this file is a module, and it has a __docs__, add to package list
        name, ext = os.path.splitext(m)
        if not ext =='.py': return 
  
        ll = len(rootpath)+1
        # make package name from file path
        p = path[ll:].replace('/', '.')
        mdl = import_module(name, package=p)
        if not mdl:  return 
        
        # ok, now check for __docs__ in the compiled module
        docs = getattr(mdl, '__docs__', [])
        if docs:
            self[mdl.__name__] = docs            
            return True
        
    def __str__(self):
        r = f' {"Modules":26}{"Classes"}\n'
        tab=' '*2
        current = ['']*5
        for name, docs in dict(self).items():
            fields = name.split('.'); n=len(fields)
            for i, field in enumerate(fields[:-1]):
                if field != current[i]:
                    current[i]=field
                    r+= tab*(i+1) + field+'.\n'
            r+= f'{tab*(n)+ fields[-1]:24s}'+ tab*2+ f'{docs}\n'
        return r
    def __repr__(self): return str(self)
    
    
class Packages(dict):
    # manage a set of packages, folders containing an __init__.py 
    def __init__(self):
        pass
 
    def check(self, path):
        ok = os.path.isfile(path+'/__init__.py')
        rploc =  len(rootpath)
        if not ok: return
        p, m = os.path.split(path[rploc+1:])
        if not p: 
            return True # first time

        if verbose: print(f'create new package {p}.{m} ?')
        pk = import_module(m, package=p)
        if not pk: return
        self.add_entry(pk)
        return ok 

    def add_entry(self, package):
        if not package: return
        docspath = getattr(package, 'docspath', '')
        if not docspath: return
        if docspath[0]!='/':
            docspath = os.path.abspath(os.path.join(packagepath, docspath))
        if verbose: print(f'Added docspath {docspath}')
        self[package.__name__] = docspath
        return True 

    def __str__(self):
        r = f'Packages:'
        for p in self:
            r +=f'\n   {p}'
        return r
    def __repr__(self): return str(self)
    
def traceback_message(e, limit=None, skip=0, ):
    import traceback
    tb = e.__traceback__
    traceback.print_last(limit)
    #for i in range(skip): tb = tb.tb_next
    #traceback.print_tb(tb, limit)
    
def import_module(name, package=None):
    # return a module object, creating if package specified, which must be the name
    # of an existing module
    if verbose: print(f'Try to import {name}, {package}')
    if not package:
        # already a module: get it and try to reload
        try:
            module  = importlib.import_module(name)
        except Exception as e:
            print(f'Failed to import existing module "{name}"', file=sys.stderr)
            return
        try:
            importlib.reload(module)
            return module
        except Exception as e:
            # compilation error, maybe
            print(f'Failed to reload module "{name}": ', file=sys.stderr)
            traceback_message(e, limit=-2)
            return None
    # create new module
    if verbose: print(f'')
    try:
        # maybe don't need this? Doesn't seem to hurt.
        #importlib.reload(sys.modules[package]) # since already exists, reload
        return importlib.import_module('.'+name, package=package)
    except Exception as e:
        print(f'Failed trying to create new module adding ".{name}" '\
              f'to existing module "{package}":\n {e}', file=sys.stderr)
        # compilation error, maybe
        #traceback_message(e, limit=-1)
        return None

def find_modules( path):
    if verbose: print(f'check package {path} for subpackages and modules:')

    flist = list(filter( lambda f: f.find('__')<0, glob.glob(path+'/*')))
    dirs = [ os.path.split(f)[-1] for f in flist if os.path.isdir(f)]
    ismod = lambda f: os.path.isfile(f) and  os.path.splitext(f)[1]=='.py'
    mods = [ os.path.split(f)[-1] for f in flist if ismod(f)]
    if verbose:
        print(f'{path}:\n\t {dirs}\n\t {mods}')
    for m in mods:
        modules.check(path, m)
    for d in dirs:
        newpath = path+'/'+d
        if packages.check(newpath):
            find_modules(newpath)

class DocMan(object):
    
    def __init__(self, rootname:'Package to index for document classes',
                     docspath:'folder to hold output'='', 
                     set_verbose=False):
        
        # set globals for helper classes
        global verbose, packagepath, rootpath, packages, modules
        docman_instance = None 
        packages = Packages()
        modules = Modules()
        self.lookup_module={}
        
        verbose =set_verbose
        
        self.docspath = docspath
        
        # import the root package, check it
        rootpackage= import_module(rootname)
        if not rootpackage:
            print(f'A package {rootname} was not found.')
            return
        
        # is it a file?
        if not hasattr(rootpackage, '__path__'):
            # yes: very simple
            rootpath, _ = os.path.split(rootpackage.__file__)
            # docspath = docspath or rootpath
            # self.docspath = docspath if docspath[0]=='/' \
                    # else os.path.join(rootpath, docspath)
            self.setup_file(rootpackage)
            return
        
        if verbose: print(f'setting up package {rootpackage}')
        packagepath = rootpackage.__path__[0]
        rootpath, _ = os.path.split(packagepath)
        if verbose: print(f'found packagepath {packagepath}, rootpath {rootpath}')
        
        # start traversing the tree
        packages.add_entry(rootpackage)
        if docspath:
            self.docspath = docspath
        if not docspath:
            self.docspath = packages.get(rootname, '')
            if not self.docspath:
                print(f'No HTML output: set the parameter "docspath" '
                      f'in "{rootname}.__init__.py" or with an arg to DocMan.')
        find_modules(packagepath)   

        # generate lookup table for class names from the result
        for md, cl in modules.items():
            for  c in cl:
                self.lookup_module[c]=md  
                
    def setup_file(self, module):
        packages[module.__name__] = self.docspath
        docs = getattr(module, '__docs__',['(nothing?)'])
        for doc in docs:
            self.lookup_module[doc] = module.__name__
        modules[module.__name__] = docs

    def user_modules(self):
        return modules.user_modules()
                    
    @property
    def doc_classes(self):
        return list(self.lookup_module.keys())
    @property
    def packages(self):
        return dict(packages)

    def __str__(self):
        return str(modules) +  (f'\ndocspath: {self.docspath}' if self.docspath else '')
    def __repr__(self): return str(self)
   
    def __call__(self, 
                docname:'name | name[.version] where name is a doc class'='', 
                as_client:'set True for client mode'=False,
                **kwargs:' arguments for class'
                ):

        if not docname:
            print(f'List of document classes:\n {self.doc_classes}')
            return

        # split off version after first period if any
        t = docname.split('.')
        classname, version = (t[0], '.'.join(t[1:])) if len(t)>1 else (docname, '')

        package_name = self.lookup_module.get(classname, None)
        if not package_name:
            print(f'{classname} not found in {self.doc_classes}')
            return

        # get the module containing the class declaration
        module = import_module(package_name)
        if module is None:
            return
        docspath = packages.get(package_name, self.docspath )

        try:
            # call the class constructor, setting a default, parhaps
            #  docspath for it; pass in version
            toeval = f'module.{classname}'
            obj = eval(toeval)(docpath=docspath, docname=docname, 
                    client_mode=as_client,**kwargs)
  
        except Exception as e:
            print(f'Error evaluating "{toeval}": {e.__class__.__name__}')
            traceback_message(e, skip=1, )
            return None
        # finally set for it to be able to call back
        obj.docman = self
        if as_client:
            link = f'{docname}/index.html'
            rlink = '../'+link
            alink = os.path.join(self.docspath,link)
            if not os.path.isfile(alink):
                print(f'*** File {alink} not found')
            self.link = rlink

        return obj

    def update(self, obj):
        """Update the index info for given doc class object
        """
        indexer = DocIndex(obj)
        indexer()
        return indexer

    # def linkto(self, docname):
    #     """create a doc, execute it, return it and a relative link"""
    #     try:
    #         obj = self(docname)
    #         obj(client_mode=True)
    #     except Exception as e:
    #         print(f'Fail to load {docname}: {e}')
    #         raise
    #     link = f'../{docname}/index.html'
    #     if not os.path.isfile(link):
    #         print(f'Relative link {link} not found')
    #     return obj
