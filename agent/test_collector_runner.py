from collector_runner import run_collectors


collectors = [
    "cpu",
    "memory",
    "disk",
    "temperature",
    "gpu"
]


print()
print("=" * 65)
print("              COLLECTOR RUNNER TEST")
print("=" * 65)


data = run_collectors(collectors)


print()
print("=" * 65)
print("              COLLECTED DATA")
print("=" * 65)


for name, value in data.items():

    print()
    print(f"[{name.upper()}]")

    print(value)


print()
print("=" * 65)