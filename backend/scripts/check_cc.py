import json
from sys import exit

result = input()
result = json.loads(result)
for _, declaration in result.items():
    if declaration["type"] == "function" and declaration["complexity"] > 9:
        exit(1)
