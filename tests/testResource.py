import env
from TEngine import Resource

resource = Resource("tests/src")

string = resource.Load("testFile/test.txt", existOk=True).AsString()

print(string)

import os
import time
logFile = os.path.join(os.getcwd(), "logs", time.strftime("%Y-%m-%d %H:%M:%S") + ".log")
Resource(os.path.dirname(logFile)).Load(logFile.split(os.sep)[-1], True)
