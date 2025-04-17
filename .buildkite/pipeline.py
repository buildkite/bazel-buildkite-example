from utils import run, filter_dirs, get_paths, get_package_step, to_json

# By default, do nothing.
steps = []

# Get a list of directories changed in the most recent commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"])
changed_dirs = filter_dirs(changed_paths)

# Query the Bazel workspace for a list of all packages (libraries, binaries, etc.).
all_packages = run(["bazel", "query", "'/...'"])

# Using both lists, figure out which packages need to be built.
changed_packages = [p for p in changed_dirs if p in get_paths(all_packages)]

# For each changed Bazel package, assemble a pipeline step programmatically to
# build and test all of its targets. For Python libraries, add a follow-up step
# to be run later that builds and tests their reverse dependencies as well.
for pkg in changed_packages:

    # Make a step that runs `bazel build` and `bazel test` for this package.
    package_step = get_package_step(pkg)

    # Use Bazel to query the package for any Python libraries.
    libraries = run(["bazel", "query", f"kind(py_library, '//{pkg}/...')"])

    for lib in libraries:

        # Find the library's reverse dependencies.
        reverse_deps = run(["bazel", "query", f"rdeps(//..., //{pkg}/...)"])

        # Filter this list to exclude any package that's already set to be built. 
        reverse_deps_to_build = [
            p for p in get_paths(reverse_deps, pkg) if p not in changed_packages
        ]

        for dep in reverse_deps_to_build:
            rdep_step = get_package_step(dep)

            # Add a command to the library's command list to generate and append
            # a build step (at runtime) for the dependent package as well.
            package_step["commands"].extend([
                f"echo 'Generating and uploading a follow-up step to build {dep}...'",
                f"python3 .buildkite/step.py {dep} | buildkite-agent pipeline upload"
            ])

    # Add this package step to the pipeline.
    steps.append(package_step)

# Emit the pipeline as JSON to be uploaded to Buildkite.
print(to_json({"steps": steps}, 4))
