import subprocess
import sys
import os

os.chdir('..')
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short']
)
sys.exit(result.returncode)
