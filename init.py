if __name__ == "__main__":
    import os
    import sys
    from configparser import ConfigParser
    from glob import glob

    import tools

    # Command line arg handling
    argv = sys.argv
    argv.pop(0)
    flags = []
    inputs = []
    for v in argv:
        if v[0] == "-":
            flags.append(v)
        else:
            inputs.append(v)

    DEFAULT_CONFIG = {
        "exe_name": "Program",
        "compiler": "g++",
        "compiler_flags": "-g -Wall -Wextra",
        "linker_flags": "",
        "source_path": "./src/",
        "bin_path": "./bin/",
    }

    CONFIG_FILE = "recipe.ini"

    if "-write" in flags:
        with open(CONFIG_FILE, "w", encoding="utf-8") as config:
            config.write("[DEFAULT]\n")
            keys = list(DEFAULT_CONFIG.keys())
            vals = list(DEFAULT_CONFIG.keys())
            for i in range(len(keys)):
                config.write(f"{keys[i]} = {vals[i]}\n")
            tools.success()

    # Grab profile
    tools.fail_if(len(inputs) == 0, "No input profile given!")
    tools.fail_if(len(inputs) > 1, "Too many input profiles!")
    profile_name = inputs[0]
    ini_file = ConfigParser()
    tools.fail_if(not os.path.exists(CONFIG_FILE), "No config file found!")
    ini_file.read(CONFIG_FILE)
    tools.fail_if(
        not ini_file.has_section(profile_name),
        f"Cannot find profile {profile_name} in config file!",
    )
    profile = DEFAULT_CONFIG | dict(ini_file[profile_name])

    # Check profile validity
    tools.fail_if(
        not os.path.exists(profile["bin_path"]
                           ), "Provided 'bin_path' does not exist!"
    )
    tools.fail_if(
        not os.path.exists(profile["source_path"]),
        "Provided 'src_path' does not exist!",
    )
    for opt in ["exe_name", "compiler", "source_path", "bin_path"]:
        tools.fail_if(profile[opt] == "",
                      f"Provided '{opt}' is an empty string!")

    # Compilation phase
    src_files = []
    for filetype in [".c", "cpp"]:
        src_files.append(glob(profile["source_path"] + "*" + filetype))
