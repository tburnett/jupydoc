import os, sys, importlib, glob

# make instance available via module
docman_instance = None
def instance():
    return docman_instance

class DocMan(dict):
    
    def __init__(self, 
                 package_name:'Name of a document package',
                 verbose=False,
                ):

        self.verbose=verbose
        self.load(package_name)
        
    def load(self, package_name):
        global docman_instance
        verbose=self.verbose
        docman_instance = None

        info = self.setup(package_name)
        if info:
            self.update(info)
            docman_instance = self


        
    def setup(self, package_name):
        verbose = self.verbose
        
        def make_module(package_name):
            try:
                package = importlib.import_module(package_name)
            except Exception as e:
                print(f'Could not import {package_name}: {e.__class__.__name__}{e.args}')
                return None
            docspath = getattr(package, 'docspath', '')
            if not docspath:
                print(f'Primary module must define docspath')
                return None
            package_path = package.__path__[0]
            if docspath[0]!='/':
                docspath = os.path.join(package_path, docspath)
            self.package_name = package_name
            self.docpaths=dict(package=docspath)
            return package
        
        def get_subfolders(package_path):
            # return a list the folders under the source module
            subfolders=[]
            for p in glob.glob( self.package_path +'/*'):
                _, folder = os.path.split(p)
                if not os.path.isdir(p) or folder in ['__pycache__',]: continue
                subfolders.append(folder)
            return subfolders
        
        def make_submodule(doc_folder):
            # make a  submodule from the submodule_path
            submodule = importlib.import_module(f'.{doc_folder}', package=package_name)
            docspath =  getattr(submodule, 'docspath', '')
            if docspath:
                self.docpaths[doc_folder] = docspath
            return submodule.__path__[0]

        def get_srcfiles(submodule_path):
            # get list of source files in this submodule
            srcfiles=[]
            for file in glob.glob(submodule_path+'/*'):
                if not os.path.isfile(file): continue
                if not os.path.splitext(file)[1]=='.py': continue
                if file.find('__')>0: continue
                srcfiles.append( file)
            return srcfiles
        
        def get_doc_classes(submodule_path, srcfiles):
            # import each source file and find its docs
            # return a dict
            _, spath =os.path.split(submodule_path)
            srcinfo = {}
            old_path, sys.path[0] = sys.path[0], submodule_path
            submodule_name = '.'.join(submodule_path.split('/')[-2:])
            for srcfile in srcfiles:
                _,file = os.path.split(srcfile)
                name, _ = os.path.splitext(file)
                module_name = f'{submodule_name}.{name}'
                try:
                    if verbose: print(f'   {submodule_name}: importing, ', end='')
                    src_module = importlib.import_module(module_name)
                except Exception as e:
                    ename, args,tb = e.__class__.__name__, e.args, e.__traceback__
                    _,subpath = os.path.split(submodule_path) 
                    print(f'\n {ename} at {subpath}.{name}.py:{tb.tb_lasti} {args}')
                    continue
                try:
                    if verbose: print(f'reloading, ', end='')
                    importlib.reload(src_module)
                    doclist = getattr(src_module, '__docs__', [])
                    if verbose: print(f'docs: {doclist}')
                    srcinfo[name] = doclist
                except Exception as e:
                    print(f'\nException:{e.__class__.__name__} {e.vars}')

            sys.path[0]=old_path
            return srcinfo
        #--------------------------
        package = make_module(package_name)
        if not package: return None
        self.package_path = package.__path__[0]
        doc_info = {}
        subfolders = get_subfolders(self.package_path)
        if verbose: print(f'Procssing list of subfolders: {subfolders}')
        
        for subfolder in subfolders:
            if verbose: print(f'  {subfolder}/:')
            submodule_path = make_submodule(subfolder)
            srcfiles = get_srcfiles(submodule_path)
            doc_info[subfolder]  = src_info= get_doc_classes(submodule_path, srcfiles)
            if verbose:
                for key, value in src_info.items():
                    print(f'    {key+".py":20s}: {value}')
        return doc_info
    
    def __str__(self):
        ret = f'{self.package_name}/  --> {self.docpaths["package"]}\n'
        for key, value in self.items():
            tofolder = self.docpaths.get(key, '')
            txt = f'--> {tofolder}' if tofolder else '' 
            ret+= f'  {key}/  {txt}\n'
            for subkey, subvalue in value.items():
                ret+= f'    {subkey+".py":20s} {subvalue}\n'
        return ret
    
    def __call__(self, name='', **kwargs):
        if not docman_instance:
            print('Initialization error')
            return
        if not name:
            print(str(self))
            return
        t = name.split('.')
        if len(t)>1:
            module_name,class_name = t 
        else:
            module_name, class_name = None,  t[0]
           
        #is the name of the submodules
        if not class_name and self.get(module_name, ''):
            print(f'docs available: {self[module_name]}')
            return 
        # look for a class
        found = None
        for key, value in self.items():
            if not type(value)==dict: continue
            for subkey, class_list in value.items():
                if class_name in class_list:
                    found = f'{key}.{subkey}.{class_name}'
                    break
            if found: break
        if not found:
            print( f'Did not find {name}: here is a list:\n{str(self)}')
            return None
     
        submodule_name,srcmodule_name, class_name = found.split('.')
        # construct compound module name
        module_name = '.'.join([self.package_name,submodule_name, srcmodule_name]) 
        assert module_name in sys.modules, f'{module_name} not a module?'
        
        if self.verbose: print(f'try to return {module_name}()')
        module = importlib.import_module(module_name)
        if module is None:
            print(f'module {module_name} not found?')
            return None
        if self.verbose:
            print(f'reloading module {module.__name__}')
        try:
            importlib.reload(module)
        except Exception as e:
            print(f'Fail reload {module_name}: {e.__class__}, {e.args}')
        
        docspath = self.docpaths.get(submodule_name, self.docpaths['package'])
        if self.verbose: print(f'module {submodule_name}, docspath={docspath}')
        try:
            obj = eval(f'module.{class_name}')(docspath=docspath, **kwargs)
        except Exception as e:
            print(f'{e.__class__.__name__}: {e.args}')
            return None
 
        return obj
        

