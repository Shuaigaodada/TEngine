import os
import sys



__base__ = \
    os.path.join(
        os.path.dirname(
            os.path.abspath(
                __file__
            )
        ),
        "afa", "src"
    )
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                __base__
            )
        )
    )
)
from TEngine.Components.resource import Resource

Resource( __base__ )
resource = Resource()
print(resource)
print(resource.srcpath)

