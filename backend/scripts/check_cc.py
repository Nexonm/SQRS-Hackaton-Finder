import json
from sys import exit

result = input()
result = json.loads(result)
for _, decls in result.items():
    for decl in decls:
        if decl["type"] == "function" and decl["complexity"] > 9:
            exit(1)
