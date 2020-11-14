import os, yaml,  datetime, glob
import inspect
import numpy as np

# generated from https://divtable.com/table-styler/
table_class = 'greyGridTable'
doc_style="""\
<style type="text/css">
body, th, td {
  font-family:verdana,arial,sans-serif;font-size:10pt;margin:50px;
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
"""

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
                print(f'DocIndex is removing entry for missing document {key}')
                self.pop(key)
        
        # get current doc info as dict
        info = doc.doc_info
        t ={}
        if doc.docname != 'Index':
            # make, or update an entry if it has a name

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
                heads='name date title'.split(), 
                classname=table_class):
        
        if filename is None: 
            inspect.stack()[0].filename
            filename = os.path.join(self.docspath, 'index.html')
        doc = doc_head 
        parent_path, folder_name = os.path.split(self.docspath)
        _, parent = os.path.split(parent_path)
        parent_ref = '../index.html' if os.path.isfile(os.path.join(parent_path,'index.html')) else '../'
        doc+=f"""<h2>Documents in folder "{folder_name}"</h2>
        <p style="text-align: right;"><a href="{parent_ref}"> Back to {parent}</a></p>\n
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
        doc += f'</tbody></table>\n'
        
        doc += '</body>'
        with open(filename, 'w') as out:
            out.write(doc)
        if self.verbose: print(f'Wrote file {filename}')
        return

    def __call__(self):

        self.to_html()
        self.save()        
      