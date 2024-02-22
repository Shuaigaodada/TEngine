import os
from TEngine import Resource

__basePath = os.path.dirname(os.path.abspath(__file__))
srcPath = os.path.join(__basePath, 'src')

__all__ = ["resource"]
resource = Resource(srcPath)
