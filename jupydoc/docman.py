
import os, sys, glob
import importlib 

# make instance available via module
docman_instance = None
def instance():
    return docman_instance

# local globals    
verbose = False
packagepath= rootpath= ''
packages = modules = None

class Modules(dict):
    # manage list of modules, python files 
    def __init__(self):
        pass

    def check(self, path, m):
        # if this file is a module, and it has a __docs__, add to package list
        name, ext = os.path.splitext(m)
        if not ext =='.py': return 
  
        ll = len(rootpath)+1
        # make package name from file path
        p = path[ll:].replace('/', '.')
        try:
            mdl = import_module(name, package=p)
        except Exception as e:
            print(f'Failed to create {p}.{name}: {e.__repr__()}')
            return 
        # ok, now check for __docs__ in the compiled module
        docs = getattr(mdl, '__docs__', [])
        if docs:
            self[mdl.__name__] = docs            
            return True
        
    def __str__(self):
        r = f'{"Modules":30s}  Classes'
        ll = len(rootpath)+1
        for name, docs in self.items():
            r += f'\n {name:30s} {docs}'
        return r
    def __repr__(self): return str(self)
    
    
    
class Packages(dict):
    # manage a set of packages, folders containing an __init__.py 
    def __init__(self):
        pass
 
    def check(self, path):
        ok = os.path.isfile(path+'/__init__.py')
        rploc =  len(rootpath)
        if ok:
            p, m = os.path.split(path[rploc+1:])
            if not p: 
                return True # first time

            if verbose: print(f'create new package {p}.{m} ?')
            try:
                pk = import_module(m, package=p)
            except Exception as e:
                raise
                print(f'Failed to create {p}.{m}: {e.__repr__()}')
                return False
            self.add_entry(pk)
        return ok 

    def add_entry(self, package):
        if not package: return
        docspath = getattr(package, 'docspath', '')
        if docspath[0]!='/':
            docspath = os.path.join(packagepath, docspath)
        self[package.__name__] = docspath
        return True 

    def __str__(self):
        r = f'Packages:'
        for p in self:
            r +=f'\n   {p}'
        return r
    def __repr__(self): return str(self)
    

def import_module(name, package=None):
    # return a module object, creating if package specified, which must be the name
    # of an existing module
    if verbose: print(f'Try to import {name}, {package}')
    if not package:
        # already a module: get it and try to relaod      
        module  = importlib.import_module(name)

        try:
            importlib.reload(module)
            return module
        except Exception as e:
            # compilation error, maybe
            ename, args,tb = e.__class__.__name__, e.args, e.__traceback__
            print(f'\n {ename} at {srcmodule_name}.py:{tb.tb_lasti} {args[0]} ')
            return None
    # create new module
    if verbose: print(f'')
    try:
        return importlib.import_module('.'+name, package=package)
    except Exception as e:
        print(f'Failed to create {package}.{name}: {e.__repr__()}')
        raise
    
   
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
    
    def __init__(self, rootname, docspath='', set_verbose=False):
        
        # set globals for helper classes
        global verbose, packagepath, rootpath, packages, modules
        docman_instance = None 
        packages = Packages()
        modules = Modules()
        self.lookup_module={}
        
        verbose =set_verbose
        
        if docspath:
            self.docspath = docspath if docspath[0]=='/' else \
                os.path.join(packagepath, docspath) 
        
        # import the root package, check it
        rootpackage= import_module(rootname)
        
        # is it a file?
        if not hasattr(rootpackage, '__path__'):
            rootpath, _ = os.path.split(rootpackage.__file__)
            docspath = docspath or rootpath
            self.docspath = docspath if docspath[0]=='/' \
                    else os.path.join(rootpath, docspath)
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
                print(f'Warning: root package {rootname}'\
                  f' did not declare "docspath" and it was not set with an arg')
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

    @property
    def doc_classes(self):
        return list(self.lookup_module.keys())
    @property
    def packages(self):
        return dict(packages)

    def __str__(self):
        return str(modules)
    def __repr__(self): return str(self)
   

    def __call__(self, classname:'name of a document classs'=None, 
                    **kwargs:' arguments for class'):

        if not classname:
            print(f'List of document classes:\n {self.doc_classes}')
            return
        package_name = self.lookup_module.get(classname, None)
        if not package_name:
            print(f'{classname} not found in {self.doc_classes}')

        # get the module containing the class declaration
        module = import_module(package_name)
        docspath = packages.get(package_name, self.docspath )

        try:
            # call the class constructor, setting the docspath for it
            obj = eval(f'module.{classname}')(docspath=docspath, **kwargs)
        except Exception as e:
            print(f'{e.__class__.__name__}: {e.args}')
            return None
        return obj
   