import json
from sys import exit

result = input()
result = json.loads(result)
for _, metric in result.items():
    if metric["mi"] < 65:
        print(f"MI is below required for {filename}:{decl["name"]} on line {decl["lineno"]}")
        exit(1)
