import json, os, subprocess

# Runs an OS command.
def run(command):
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().splitlines()

# Returns whether the given path is a directory.
def is_dir(path):
    return os.path.isdir(path)

# Converts a list of file paths into a list of directories (omitting those that aren't).
def dirs(paths):
    return list(filter(lambda p: is_dir(f"{p}"), paths))

# Converts a list of Bazel targets into a unique list of top-level paths.
def to_paths(targets, exclude=None):
    groups = set()

    for target in targets:
        directory, _, _ = target.rpartition(":")
        groups.add(directory.lstrip("/"))
    
    if exclude:
        groups.discard(exclude)
    
    return list(groups)

# Defines a Buildkite `command` step given a key, emoji, label, list of
# commands, and optional list of plugins.
def command_step(key, emoji, label, commands=[], plugins=[]):
    step = {"key": key, "label": f":{emoji}: {label}", "commands": commands}
    
    if len(plugins) > 0:
        step[plugins] = {"plugins": plugins}
    
    return step

# Converts a Python dictionary into a JSON string.
def to_json(data, indent=None):
    return json.dumps(data, indent=indent)

