import os
import sys
from glob import glob
from subprocess import call

LOG_INFO = 0
LOG_WARN = 1
LOG_FATAL = 2
LOG_SUCCESS = 3


def log(_msg: str, level=LOG_INFO, quiet=False, color=True) -> None:
    """
    Print message to output with [PYMAKE] prefix, end with ANSI reset code.
    """
    # Don't log if quiet is set
    if quiet and level < LOG_FATAL:
        return

    # Color output
    if not color:
        pass
    elif level == LOG_INFO:
        pass  # default output
    elif level == LOG_WARN:
        print("\u001b[33m", end="")  # orange output
    elif level == LOG_FATAL:
        print("\u001b[31m", end="")  # red output
    elif level == LOG_SUCCESS:
        print("\u001b[32m", end="")  # green output

    print("[CRAFT] " + _msg)
    if color:
        print("\u001b[0m", end="")


def fail_if(_exit: bool, _msg: str) -> None:
    "Do sys.exit() if _exit is true"
    if _exit is True:
        log(_msg, level=LOG_FATAL)
        log("Exiting...", level=LOG_FATAL)
        sys.exit(1)


def success():
    log("Success!", level=LOG_SUCCESS)


def validate_config(_cfg: dict[str, str]) -> None:
    """
    Fail if any invalid options are set in the given config
    """
    fail_if(not os.path.exists(_cfg["bin_path"]),
            "Provided 'bin_path' does not exist!")
    fail_if(
        not os.path.exists(_cfg["source_path"]
                           ), "Provided 'src_path' does not exist!"
    )
    for opt in ["exe_name", "compiler", "source_path", "bin_path"]:
        fail_if(_cfg[opt] == "", f"Provided '{opt}' is an empty string!")


def get_config() -> dict[str, str]:
    """
    Return a dict with the selected config,
    or the default config if none is provided
    """
    if len(argv) <= 1:
        log("Using config profile: DEFAULT")
        validate_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    # Command line argument provided
    argv1 = argv[1]
    ini_file = ConfigParser()
    config_exists = False
    for c in CONFIG_FILES:
        if os.path.exists(c):
            config_exists = True
            ini_file.read(c)
            log("Local config file found")
            break
    fail_if(not config_exists, "Profile given but no recipe found!")
    fail_if(
        not ini_file.has_section(
            argv1), f"Cannot find profile {argv1} in config file!"
    )
    _ret = DEFAULT_CONFIG | dict(ini_file[argv1])
    validate_config(_ret)
    return _ret


def shell(_cmd: str) -> int:
    "Run _cmd as a shell command"
    if "-quiet" not in flags:
        log(_cmd)
    return call(_cmd, shell=True)
