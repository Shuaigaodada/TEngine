import os
import sys

# Add the project directory to the path
basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
projectPath = os.path.join(basePath, 'TEngine')
sys.path.append(projectPath)
