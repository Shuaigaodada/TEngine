import env
from TEngine import Resource

resource = Resource("tests/src")

string = resource.load("testFile/test.txt", existOk=True).asString()

print(string)

import os
import time
logFile = os.path.join(os.getcwd(), "logs", time.strftime("%Y-%m-%d %H:%M:%S") + ".log")
Resource(os.path.dirname(logFile)).load(logFile.split(os.sep)[-1], True)
