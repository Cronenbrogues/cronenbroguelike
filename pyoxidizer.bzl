"""Creates a standalone binary of the game.

# To create the binary:
> pyoxidizer.run

# To generate the .tar.gz zip archive:
> tar -cvpf cronenbroguelike.tar <here>/build/x86_64-unknown-linux-gnu/debug/install/cronenbroguelike
> gzip -c cronenbroguelike.tar > cronenbroguelike.tar.gz
"""

def make_dist():
    return default_python_distribution()

def make_exe(dist):
    policy = dist.make_python_packaging_policy()
    policy.include_distribution_resources = True

    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "cronenbroguelike"

    exe = dist.to_python_executable(
        name="cronenbroguelike",
        packaging_policy=policy,
        config=python_config,
    )

    exe.add_python_resources(exe.pip_install(["-r", "requirements.txt"]))
    exe.add_python_resources(exe.pip_install([CWD]))

    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()

def make_install(exe):
    files = FileManifest()

    files.add_python_resource(".", exe)

    return files

register_target("dist", make_dist)
register_target("exe", make_exe, depends=["dist"])
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)
register_target("install", make_install, depends=["exe"], default=True)

resolve_targets()

PYOXIDIZER_VERSION = "0.10.3"
PYOXIDIZER_COMMIT = "UNKNOWN"
