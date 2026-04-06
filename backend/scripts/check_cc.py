import json
from sys import exit

result = input()
result = json.loads(result)
for filename, decls in result.items():
    for decl in decls:
        if decl["type"] == "function" and decl["complexity"] > 9:
            print(f"Exceeded CC limit in {filename}:{decl["name"]} on line {decl["lineno"]}")
            exit(1)
