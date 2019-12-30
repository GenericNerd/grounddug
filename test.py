from urllib import request

chunks = 0

def updateChunks(newValue):
    global chunks
    chunks = newValue

updateChunks(1)
print(chunks)