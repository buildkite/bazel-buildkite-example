import json, os, subprocess

# Runs an OS command, returning stdout as a list of lines.
def run(command):
    return (
        subprocess.run(command, capture_output=True, text=True, check=True)
        .stdout.strip()
        .splitlines()
    )

# Converts a list of file paths into a list of directories, omitting those that aren't.
def filter_dirs(paths):
    return list(filter(lambda p: os.path.isdir(p), paths))

# Converts a list of Bazel targets into a unique list of top-level paths. For example, 
# turns this:
#   //app:main              
#   //app:test_main         
#   //library:hello
#   //library:test_hello                 
#                          
# into this:
#   app
#   library                         
def to_paths(targets, exclude=None):
    groups = set()

    for target in targets:
        directory, _, _ = target.rpartition(":")
        groups.add(directory.lstrip("/"))

    if exclude:
        groups.discard(exclude)

    return list(groups)


# Returns a Buildkite `command` step (as a Python dictionary to be serialized as
# JSON later) given a key, emoji, label, list of commands, and optional list of
# dependencies and plugins. See the Buildkite docs for additional options.
# https://buildkite.com/docs/pipelines/configure/defining-steps
def command_step(key, emoji, label, commands=[], plugins=[], depends_on=None):
    step = {"key": key, "label": f":{emoji}: {label}", "commands": commands}

    if len(plugins) > 0:
        step["plugins"] = plugins

    if depends_on is not None:
        step["depends_on"] = depends_on

    return step


# Returns a Buildkite `command` step that builds, tests, and annotates (using
# the official Bazel-annotation plugin) a given Bazel package.
def make_pipeline_step(package, depends_on=None):
    return command_step(
        package,
        "bazel",
        f"Build and test //{package}/...",
        [
            f"bazel test //{package}/...",
            f"bazel build //{package}/... --build_event_json_file=bazel-events.json",
        ],
        [
            {
                # https://github.com/buildkite-plugins/bazel-annotate-buildkite-plugin
                "bazel-annotate#v0.1.0": {
                    "bep_file": f"bazel-events.json",
                }
            }
        ],
        depends_on,
    )


# Converts a Python dictionary into a JSON string, with optional pretty-printing.
def to_json(data, indent=None):
    return json.dumps(data, indent=indent)
