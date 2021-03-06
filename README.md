The following is a description from the introduction in the manual  **[document](https://tburnett.github.io/jupydoc.documents.Manual)** which was generated by [this code](jupydoc/documents.py).

---

# [Jupydoc: Generate documents with Python code](https://tburnett.github.io/Manual/index.html) 

<p style="text-align: right;">2020-06-18 17:36</p> 
<p style="text-align: center;" >Toby Burnett &lt;tburnett@uw.edu&gt;<br>University of Washington<br></p>

</header>

### What it is **not**
Jupydoc, despite the name, does not explicitly depend on Jupyterlab. 
It is not a nice way to turn 
detailed notebooks into documents: If you want that, see this 
[system](http://blog.juliusschulz.de/blog/ultimate-ipython-notebook). 

### What is it, and how does it work?
Jupydoc is not centered on a jupyterlab notebook. It is designed to make it easy to *develop* a
document with a noteboook, but the *medium* is a Python class, not a  notebook. Since it is
based on code, that implies developing the code at well&mdash;the document 
may represent the code development itself.

While designed to be used to develop documents based on code in a JupyterLab enviornment,
It does not actually require it, but depends on IPython and nbconvert.
 
Some points to illustrate the design and operation are:

* **Code and markdown cells in a Jupyterlab notebook**<br>
The origin of this package was rooted in a desire to be able to combine 
the nice formatting capability of   markdown cells, with the output from 
the computation in a code cell. By default, any matplotlib
figures created in its computation will automatically appear below the cell. 
This behavior, it turns out, can be controlled  by code executed in the cell.
The key here is that code can create markdown text,
which will be interpreted just as the text in a markdown cell. 
This includes LaTex. The markdown so created
is nicely rendered in the notebook. 
This is accomplishted by IPython. So a notebook is not actually required, 
see `nbconvert` below.
 
* **Python [inspection](https://docs.python.org/3/library/inspect.html)**
<br>The inspection capability gives access to two important elements of a function:
  * docstring&mdash; a text string immediately following the function declaration.
  * symbol table&mdash;in python terms, a "dict" with variable names as keys, 
 and where each value is a reference to the object represented by the name

* **Python string format method**<br>
Since python 2.6, text strings have had a "format" method, which interprets 
occurrences of "{{...}}",  replacing what it finds between the
curly brackets with its evaluation as an expression. 
(With python 3, this is built into special format strings.)

* **[nbconvert](https://nbconvert.readthedocs.io/en/latest/)**
<br>This separate package supports creation of an HTML document from notebook-formatted data, specifically 
interpreting Jupyterlab's version of markdown. 
It is necessary to produce an (almost) identical-looking  document to what is rendered in the notebook.

### What is it good for?

* **A document like this**<br>
This document is itself a demonstration, testing all the features it describes! 
It was generated using member functions  of the class `jupydoc.Document`, 
which inherits from `jupydoc.Publisher`.
Each such function represents a section of the document. 
The code that produced this document is in fact testing and 
describing the code that produces it.
       
* **Simple Jupyterlab-based analyses**<br>
Rather than spreading output among several cells, this encourages 
making a coherent description, including  plots, formulae, tables, etc. 
in the area below a single cell.

* **Personal notebook**<br>
Rather than cutting and pasting single plots to a personal notebook, this allows the clipping 
to include many details, with LaTex formulas perhaps. Since it is easy to produce web pages at the
same time, they could function as a notebook.

* **Presentations and analysis documents**<br>
Sharing one's analysis results with others is a small step from the personal notebook. The days of 
needing PowerPoint to make presentations seem to be over, so the document can be the presentation medium.

* **Publication?**<br>
Well, I'd not go that far, but the evolution to such should be easy, especially if relevant LaTex
formulae, plots with captions and relevant description have already been done.

---
### Installation
To try out this beta version, download it via clone or zip. The only requirement not satisfied by the JupyterLab environment is
[`yaml`](https://pyyaml.org/wiki/PyYAMLDocumentation), installed with
```
pip install pyyaml
```
I'll put it into PyPI after I, and a few others, have experience with using it for research.

### Simple hello
Here is a simple hello world, code in a Jupyter code cell:

```
from jupydoc import Publisher

class Hello(Publisher):
    
    def sayhi(self, to):
        """         
        Hello there, **{to}**!        
        See you later.
        """
        self.publishme()
h =Hello()
h.sayhi('world')
```
which displays, below the code cell, the following:

Hello there, **world**! See you later.

### Regenerate this document

The following in a cell

```
from jupydoc import DocMan
DocMan('jupydoc')('Manual')('all')
```
will display all of this manual, a test of most of the package functionality, as implemented by the class "Manual", found in this "jupydoc" package.

## An analysis code development paradigm shift:
I'm using this to fundamentally reorganize my analysis, with a focus on documenting code and results as I generate them. I'll
report on insights in the [last section](https://tburnett.github.io/jupydoc.documents.Manual#workflow) of the manual.

