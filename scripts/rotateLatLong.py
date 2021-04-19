#!/usr/bin/env python3

import json

with open("in.json", "r") as f:
    data = json.loads(f.read())

def rotateWorker(x):
    if isinstance(x[0], list):
        for el in x:
            rotateWorker(el)
    else:
        first = x[0]
        x[0] = x[1]
        x[1] = first

rotateWorker(data)

with open("out.json", "w") as f:
    f.write(json.dumps(data))
