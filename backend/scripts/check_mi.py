import json
from sys import exit

result = input()
result = json.loads(result)

flag = False
for filename, metric in result.items():
    if metric["mi"] < 65:
        print(f"MI is below required for { filename }")
        flag = True

if flag:
    exit(1)
