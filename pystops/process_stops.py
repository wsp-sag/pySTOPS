# ---------------  README -------------------------
# This file is intended to be used for packaging the code into a single executable and is not the entry point
# this is instended to allow for maximum portability and small changes to the existing py files
# this code will need to be changed. if there is a change to the import
# structure of the attached py files this may cause issues. If you
# doing serious development it is recomended that you create your own venv from requirements.txt
# and run main.py from there
# to build an exe move this file to the same directory as process stops.exe
# and run pyinstaller process_stops.py --one file
# %%
import pandas
import geopandas
import pathlib
import glob
import shapely
import numpy
from pathlib import Path
import os
import warnings

warnings.filterwarnings("ignore")

entry_py_file = "main"

# class ExecInNameSpace:
#     def __init__(self, code_string):
#         self.namespace = {}
#         exec(code_string, globals(), self.namespace)  # Execute code in the namespace


#     def __getattr__(self, name):
#         try:
#             return self.namespace[name]  # Access attribute from the namespace
#         except KeyError:
#             raise AttributeError(f"Attribute '{name}' not found in namespace")
class DictNamespace:
    def __init__(self, d):
        self.__dict__.update(d)


def ExecInNamespace(namespace_name, file_path):
    namespace = {}
    with open(file_path) as file:
        code_string = file.read()
        exec(code_string, globals(), namespace)
    globals()[namespace_name] = DictNamespace(namespace)  # Add namespace to globals


CWD = Path(os.getcwd())

with open((CWD / "python_scripts" / entry_py_file).with_suffix(".py")) as f:
    main_file = f.read()


python_files = {
    path.stem: path
    for path in (CWD / "python_scripts").glob("*.py")
    if path.name != entry_py_file
}

lines_to_execute = []
for line in main_file.split("\n"):
    if line[:7] == "import ":
        if " as " in line:
            module_name = line[7:].split(" as ")[0].strip()
            namespace = line[7:].split(" as ")[1].strip()
        else:
            module_name = line[7:].strip()
            namespace = module_name.strip()

        if module_name in python_files:
            print(module_name, namespace)
            ExecInNamespace(namespace, python_files[module_name])
        else:
            lines_to_execute.append(line)

    elif line[:5] == "from ":
        # if we are from ___ import ___, ___
        module_name = line[5:].split(" import ")[0]

        if module_name in python_files:
            print("importing", module_name, "globally")
            with open(python_files[module_name]) as file:
                code_string = file.read()
                # exec(code_string, globals(), namespace)

        else:
            lines_to_execute.append(line)

    else:
        lines_to_execute.append(line)

# these files need to be in the global name space
#
with open(CWD / "python_scripts" / "helper_functions.py") as file:
    code_string = file.read()
    exec(code_string)

with open(CWD / "python_scripts" / "reader.py") as file:
    code_string = file.read()
    exec(code_string)

with open(CWD / "python_scripts" / "read_16.py") as file:
    code_string = file.read()
    exec(code_string)

with open(CWD / "python_scripts" / "post_process_functions.py") as file:
    code_string = file.read()
    exec(code_string)
# %%
filtered_py = "\n".join(lines_to_execute)
exec(filtered_py)

# ExecInNamespace(
# %%
