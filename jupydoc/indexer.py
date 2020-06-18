import os, yaml,  datetime
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

    def __init__(self, doc:'An jupydoc.DocPublisher object',
               verbose=False):
        
        if not hasattr(doc, 'docpath') or not hasattr(doc, 'doc_info'):
            raise Exception('Expected a DocPublisher object')

        # set up index entry with info from the doc
        self.docspath = doc.docpath
        info = doc.doc_info
        t ={}
        t[doc.docname] = dict(
                    title=info.get('title','(no title)'.split('\n')[0]) ,
                    date= info.get('date', str(datetime.datetime.now())[:16]), 
                    author=info.get('author', ''),
            )
        self.update(t)


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

    def __call__(self):
        self.to_html()
        self.save()        
      