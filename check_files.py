import os

print("Current working directory:", os.getcwd())
print("\nFiles in current directory:")
for file in os.listdir('.'):
    if file.endswith('.csv'):
        print("  -", file)

print("\nFull path of current directory:", os.path.abspath('.'))