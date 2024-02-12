from multipledispatch import dispatch

@dispatch(int)
def add(a: int):
    return a + 2

@dispatch(str)
def add(a: str):
    return int(a) + 2

print(add(12), add('12'))
