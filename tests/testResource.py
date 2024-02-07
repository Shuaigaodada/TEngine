import env
from TEngine.resource import Resource

resource = Resource("tests/src")

string = resource.Load("testFile/test.txt", existOk=True).AsString()

print(string)
