import os, yaml,  datetime, glob
import inspect
import numpy as np





doc_head="""\
<html> 
<head> <title>Document list</title> 
<style type="text/css">
.rendered_html_table {
  margin-left: 10px;
  margin-right: auto;
  border: none;
  border-collapse: collapse;
  border-spacing: 0;
  color: black;
  font-size: 12px;
  table-layout: fixed;
}
.rendered_html tr,
.rendered_html th,
.rendered_html td {
  text-align: right;
  vertical-align: top;
  padding: 0.5em 0.5em;
  line-height: normal;
  white-space: normal;
  max-width: none;
  border: none;
  }
  </style>
</head>
"""


class DocIndexer(dict ):

    def __init__(self, doc:'A jupydoc.DocPublisher object',
               verbose=False):
        
        if not hasattr(doc, 'docpath') or not hasattr(doc, 'doc_info'):
            raise Exception('Expected a DocPublisher object')

        # set up index entry with info from the doc
        self.docspath = doc.docpath
        self.verbose=verbose
        self.index_file = os.path.join(self.docspath, 'index.yaml')
        
        # load the current index yaml file, if it exists
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as stream:
                    id =  yaml.safe_load(stream)
                    self.update(id)
            except Exception as msg:
                raise Exception(f'Failed to parse {self.index_file}:\n{msg}')
        
            # remove entries with no corresponding document
            subdirs = list(filter(lambda d: os.path.isdir(d), glob.glob(self.docspath+'/*'))); 
            docnames=list(map(lambda d: os.path.split(d)[1], subdirs))
            toremove = list(filter(lambda t: t not in docnames, self.keys()))
            for key in toremove:
                print(f'DocIndexer is removing entry for missing document {key}')
                self.pop(key)
        
        # get current doc info as dict
        info = doc.doc_info
        t ={}
        if doc.docname != 'Index' and doc.docname != 'DocIndex':
            # make, or update an entry if it isn't an index

            t[doc.docname] = dict(
                        title=info.get('title','').split('\n')[0] ,
                        date= info.get('date', str(datetime.datetime.now())[:16]), 
                        author=info.get('author', '').split('\n')[0],
                        info=getattr(doc, 'info', {}),
            )
            self.update(t)
        else:
            # this is an "Index" document
            self.index_doc = info

    def _repr_html_(self, heads='name date title abstract'.split(), header=False ):
        # doc = doc_style 
        # doc+=f"""<h2>Jupydoc Documents</h2>
        # List of documents at {self.docspath}<br><br>
        # """
        doc=''
        doc+= f'<table order="1" style="margin-left: 10px; text-align: left; vertical-align: text-top;">\n'
        if header:
            doc += '\n<thead>\n<tr>'
            for head in heads:
                doc+=f'  <th>{head}</th>\n'
            doc+=f' </tr>\n</thead>\n'
        doc += '<tbody>\n'
        
        # sort dates
        keys = [ k for k in self.keys() if k and self[k]]
        dates = [self[x].get('date','0000-00-00 00:00') for x in keys ]
        sortedkeys = np.array(keys)[np.flipud(np.argsort(dates))]
        ta = '"text-align: left;"'
        for name in sortedkeys:
            value = self[name]
            if value is None or type(value)!=dict :
                continue
            info = value.get('info', {})

            doc += f' <tr>\n  <td {ta}><a href="{name}/index.html?skipDecoration">{name}</a></td>\n'
            # date
            doc += f'<td {ta}>{value["date"]}</td>\n'
            # title, then abstract in last cell

            doc += f'  <td {ta}>{value["title"]}<br style="line-height:5x"/>\n'
            abstract = info.get('abstract', '')
            doc += '<p>'+abstract+'</p>\n' if abstract else ''
            doc += '  </td>\n'
            doc += ' </tr>\n'
        doc += f'</tbody></table>\n'
        return doc
      
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
                indexdoc:'dict that may nave title, author, abstract'={},
                heads='name date title'.split(), 
                ):
        
        if filename is None: 
            inspect.stack()[0].filename
            filename = os.path.join(self.docspath, 'index.html')
        doc = doc_head 
        parent_path, folder_name = os.path.split(self.docspath)
        _, parent = os.path.split(parent_path)
        parent_ref = '../index.html' if os.path.isfile(os.path.join(parent_path,'index.html')) else '../'
        
        doc+='<h2>' + indexdoc.get('title', f'Documents in folder "{folder_name}"') + '</h2>\n'
        
        doc+=f'<p style="text-align: right;"><a href="{parent_ref}"> Back to {parent}</a></p>\n'
        
        abstract=indexdoc.get('abstract', '').format(**self.__dict__)
        doc+=f'<p> {abstract} </p>'

        doc+= f'<table ">\n<thead>\n <tr>\n'
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
        doc += f'</tbody></table>\n'
        
        doc += '</body>'
        with open(filename, 'w') as out:
            out.write(doc)
        if self.verbose: print(f'Wrote file {filename}')
        return

    def __call__(self, indexdoc):
        if indexdoc:
            doc = yaml.safe_load(indexdoc)
            self.to_html(indexdoc=doc)
        else:
            self.to_html()
        self.save()        
      