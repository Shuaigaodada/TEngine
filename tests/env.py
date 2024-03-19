import os
import sys

# Add the project directory to the path
basePath = \
os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)   
    )
)
sys.path.append(basePath)
