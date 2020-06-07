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
        global docman_instance
        self.verbose=verbose
        try:
            self.package= importlib.import_module(package_name)
        except Exception as msg:
            print(f'Failed to import {package_name}: {msg}')
            return
        self.package_path = self.package.__path__[0]
        self.package_name = package_name
        
        docspath = getattr(self.package, 'docspath', '')
        if not docspath:
            print(f'Document package {package_name} needs to specify "docspath"')
            return
        if docspath[0]!='/':
            docspath = os.path.join(self.package_path, docspath)
        if os.path.exists(docspath):
            if  not os.path.isdir(docspath):
                print(f'Document folder {docspath} is not a directory')
                return
        else:
            try:
                os.makedirs(docspath, exist_ok=True)
            except Exception as msg:
                print('Could not make folder {docspath}: {msg}')
                return
        
        # default docspath from parent module. Perhaps more from submodules
        self.docspath = docspath
        self.docpaths={}
        self.docpaths[package_name]=docspath
        info = self.setup()
        if info:
            self.update(info)
            docman_instance = self
        else:
            # something failed
            docman_instance = None
        
    def setup(self):
        verbose = self.verbose
        
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
            submodule = importlib.import_module(f'.{doc_folder}', package=self.package_name)
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

            for srcfile in srcfiles:
                _,file = os.path.split(srcfile)
                name, _ = os.path.splitext(file)
                try:
                    if verbose: print(f'   {name}: importing, ', end='')
                    src_module = importlib.import_module(name)
                except Exception as e:
                    ename, args,tb = e.__class__.__name__, e.args, e.__traceback__
                    _,subpath = os.path.split(submodule_path) 
                    print(f'\n {ename} at {subpath}.{name}.py:{tb.tb_lasti} {args}')
                    continue
                try:
                    newname = spath+'.'+name
                    if verbose: print(f' renaming to "{newname}"', end='\n\t\t')
                    sys.modules[newname] = src_module   
                    src_module = importlib.import_module(newname)
                except Exception as e:
                    print(f'\nException:{e.__class__.__name__} {e.vars}')

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
        ret = f'{self.package_name}/\n'
        for key, value in self.items():
            ret+= f'  {key}/\n'
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
        module_name = submodule_name+'.'+srcmodule_name
        if self.verbose: print(f'try to return {module_name}.{class_name}()')
        
        module = sys.modules.get(module_name, None)
        if module is None:
            print(f'module {module_name} not found?')
            return None
        
        docspath = self.docpaths.get(submodule_name, self.docspath)
        if self.verbose: print(f'module {submodule_name}, docspath={docspath}')
        try:
            obj = eval(f'module.{class_name}')(docspath=docspath, **kwargs)
        except Exception as e:
            print(f'{e.__class__.__name__}: {e.args}')
            return None
 
        return obj
        

