import sys
from utils import get_package_step, to_json

# Read the list of packages from the command line.
pkgs = sys.argv[1:]

# Make a build step for each package.
steps = [get_package_step(pkg) for pkg in pkgs]

# Emit the list of steps as JSON.
print(to_json({"steps": steps}, 4))
