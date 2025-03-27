import json, os, subprocess

# Runs an OS command and returns a list of the lines comprising the result.
def run(command):
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().splitlines()

# Converts a list of file paths into a list of directories (omitting those that aren't).
def dirs(paths):
    return list(filter(lambda p: os.path.isdir(p), paths))

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
def command_step(key, emoji, label, commands=[], plugins=[], depends_on=None):
    step = {"key": key, "label": f":{emoji}: {label}", "commands": commands}
    
    if len(plugins) > 0:
        step["plugins"] = plugins
    
    if depends_on is not None:
        step["depends_on"] = depends_on
    
    return step

# Defines a command test that builds, tests, and annotates a given Bazel package.
def build_test_and_annotate(package, depends_on=None):
    return command_step(package, "bazel", f"Build and test //{package}/...", [
        f"bazel test //{package}/...",
        f"bazel build //{package}/... --build_event_json_file=bazel-events-{package}.json",
    ], [{
        "buildkite-plugins/bazel-annotate#v0.1.0": {
            "bep_file": f"bazel-events-{package}.json",
            "skip_if_no_bep": True,
        }
    }], depends_on)

# Converts a Python dictionary into a JSON string.
def to_json(data, indent=None):
    return json.dumps(data, indent=indent)

