import subprocess
import os

# Get list of files in commit 9d95bf7, excluding the bad path
p = subprocess.run(['git', 'ls-tree', '-r', '9d95bf7', '--name-only'], capture_output=True, text=True, encoding='utf-8')
all_files = [f.strip() for f in p.stdout.splitlines() if f.strip() and 'Path(os.getenv' not in f]

print(f"Files to restore: {len(all_files)}")

# Checkout each valid file individually
for filepath in all_files:
    result = subprocess.run(['git', 'checkout', '9d95bf7', '--', filepath], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"  ERROR restoring {filepath}: {result.stderr.strip()}")
    else:
        print(f"  OK: {filepath}")

print("\nDone! Now commit and push...")
