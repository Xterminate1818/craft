#!bin/python
import os
import sys
from configparser import ConfigParser
from glob import glob
from subprocess import call

CONFIG_FILE = "recipe.ini"

DEFAULT_CONFIG = {
    "exe_name": "Program",
    "exe_dir": "./bin/",
    "compiler": "g++",
    "compiler_flags": "-g -Wall -Wextra",
    "linker_flags": "",
    "source_path": "./src/",
    "bin_path": "./bin/",
}


class LOG_LEVEL:
    INFO = 0
    WARN = 1
    FATAL = 2


def log(_msg: str, _level: int = LOG_LEVEL.INFO) -> None:
    """
    Print message to output with [PYMAKE] prefix, end with ANSI reset code.
    """
    if _level == LOG_LEVEL.INFO:
        pass  # default output
    if _level == LOG_LEVEL.WARN:
        print("\u001b[33m", end="")  # orange output
    if _level == LOG_LEVEL.FATAL:
        print("\u001b[31m", end="")  # red output
    print("[PYMAKE] " + _msg + "\u001b[0m")


def fail_if(_exit: bool, _msg: str) -> None:
    """
    Do sys.exit() if _exit is true
    """
    if _exit is True:
        log(_msg, _level=LOG_LEVEL.FATAL)
        sys.exit()


def find_files(
    _path: str, _pattern: str, _rec: bool = False, _ext: bool = False
) -> list:
    """
    Return list of file path strings inside of folder _path matching _pattern.
        _rec: recursive True/False (default False)
        _ext: include extension True/False (default False)
    """
    files = []
    for fname in glob(_path + _pattern, recursive=_rec):
        if _ext:
            files.append(fname)
        else:
            files.append(os.path.splitext(fname)[0])
    return files


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
    for opt in ["exe_name", "exe_dir", "compiler", "source_path", "bin_path"]:
        fail_if(_cfg[opt] == "", f"Provided '{opt}' is an empty string!")


def get_config() -> dict[str, str]:
    """
    Return a dict with the selected config,
    or the default config if none is provided
    """
    if len(sys.argv) <= 1:
        log("Using config profile: DEFAULT")
        return DEFAULT_CONFIG
    # Command line argument provided
    argv1 = sys.argv[1]
    ini_file = ConfigParser()
    found = ini_file.read(CONFIG_FILE)
    fail_if(len(found) == 0, f"Cannot find config file '{CONFIG_FILE}'!")
    fail_if(
        not ini_file.has_section(
            argv1), f"Cannot find profile {argv1} in config file!"
    )
    _ret = DEFAULT_CONFIG | dict(ini_file[argv1])
    validate_config(_ret)
    return _ret


def shell(_cmd: str, _silent: bool = False) -> int:
    """
    Run _cmd as a shell command, disable echo with _silent=True
    """
    if not _silent:
        log(_cmd)
    return call(_cmd, shell=True)


if __name__ == "__main__":
    cfg = get_config()

    # Cleaning step - Don't care if this errors
    log("Cleaning up...")
    shell(f"rm {cfg['bin_path']}*.o")

    # Compilation step
    EXIT_CODE = 0
    log("Compiling...")
    src_files = find_files(cfg["source_path"], "*.cpp", _rec=True)
    for f in src_files:
        EXIT_CODE = shell(
            f"{cfg['compiler']} -c {f}.cpp {cfg['compiler_flags']}")
        fail_if(EXIT_CODE != 0, "Compilation failed!")

    # Moving object files to bin directory
    O_FILES = find_files("./", "*.o")
    for f in O_FILES:
        EXIT_CODE = shell(f"mv {f}.o {cfg['bin_path']}{f}.o")
        fail_if(EXIT_CODE != 0, "Failed to move object files!")

    # Linking step
    log("Linking...")
    O_FILES = " ".join(find_files(
        cfg["bin_path"], "*.o", _rec=False, _ext=True))
    EXIT_CODE = shell(
        f"{cfg['compiler']} -o {cfg['exe_dir']}{cfg['exe_name']} {O_FILES} {cfg['linker_flags']}"
    )
    fail_if(EXIT_CODE != 0, "Linking failed!")
    log("\u001b[32mSuccess!")
