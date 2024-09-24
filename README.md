[![Support me](https://iacoposk8.github.io/img/buymepizza.png)](https://buymeacoffee.com/iacoposk8)

# Md and requirements generator
Script to generate .md files for use on github and the requirements.txt file to make it easy to update the project.

Usage:
Open the file you want to create documentation for.  For each function or method you have to insert the description of the various parameters with a json in a comment, for example the following function:

    def __init__(self, timeout = 5)
Becomes:

    '''
    	__init__: {
    		"description": "This method is for...",
    		"timeout": "After X seconds it will happen that…"
    	}
    '''
    def __init__(self, timeout = 5)
When you are ready you can generate the README.md file with:

    python md_generator.py path_class_file.py

md_generator.py it will look for all the public "def" (for now it only works with python) and it will warn you in case the description of a method or an attribute is missing. It will also look for the imports to create the requirements.txt file and warn you if any unused libraries have been called in your code.

The library is not always installed with the same name with which it is imported. For example PIL is installed with pip install Pillow. In this case we have to write in our file:

    '''
    requirements:{
    	"PIL": "Pillow",
    }
    '''
While if we don't want that library to appear in our requirements.txt file we write:

    '''
    requirements:{
    	"PIL": "Nome",
    }
    '''
