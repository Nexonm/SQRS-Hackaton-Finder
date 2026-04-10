import json
from sys import exit

result = input()
result = json.loads(result)

if not result:
    print("No MI data received")
    exit(1)

average_mi = sum(metric["mi"] for metric in result.values()) / len(result)
print(f"Average MI: {average_mi:.2f}")

if average_mi < 65:
    print("Average MI is below required threshold")
    exit(1)
