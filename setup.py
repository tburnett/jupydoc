import os
from setuptools import find_packages, setup


HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, "README.md"), encoding="utf8") as f:
    readme = f.read()

setup(
    author="Toby Burnett",
    author_email="tburnett@uw.edu",
    version="0.0.1",
    description="Generate documents using Jupyter and nbconvert",
    install_requires=["nbconvert", "IPython",],
    keywords="jupyter ",
    license="BSD3",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="ju_doc",
    packages=find_packages(),
    python_requires=">=3.7",
    url="https://github.com/tburnett/ju-doc",
    entry_points={},
)
