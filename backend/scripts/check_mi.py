import json
from sys import exit

result = input()
result = json.loads(result)
for _, metric in result.items():
    if metric["mi"] < 65:
        exit(1)
