"""jupydoc module 
"""

from setuptools import setup, find_packages

from .publisher import Publisher
from .document import Document
from .doc_publisher import DocPublisher

from .indexer import get_doc, set_docs_info, get_docs_info

