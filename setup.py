import setuptools


with open("README.md", 'r') as fn:
    long_description = fn.read()

setuptools.setup(
    name="jupydoc-tburnett",
    author="Toby Burnett",
    author_email="tburnett@uw.edu",
    version="0.0.1",
    description="Generate documents using Jupyter and nbconvert",
    install_requires=["nbconvert", "jupyter",],
    keywords="jupyter ",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    url="https://github.com/tburnett/jupydoc",
   
)
