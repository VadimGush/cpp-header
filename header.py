#!/bin/python3
# I know this script is a little bit horrible and needs refactoring,
# but for now at least it does its job perfectly (in my case).
import os
import re
import sys

# Parse arguments
license_path = ""
for i in range(1, len(sys.argv)):
    if ("--license" == sys.argv[i]) & (i != len(sys.argv) - 1):
        license_path = sys.argv[i+1]

source_path = ""
if len(sys.argv) > 1:
    # path to source directory is always the last argument
    source_path = sys.argv[len(sys.argv)-1]
else:
    print("ERROR: Path to source directory is not provided")
    sys.exit(1)
  

# First we will collect list of all headers from source files and parse them.
headers = []

dependency_pattern = re.compile(r"#include \"(.*)\"")
include_pattern = re.compile(r"#include <.*>")
pragma_pattern = re.compile(r"#pragma once")

# list of global includes (#include <>)
# we don't want to duplicate those (because every header has one),
# so we will collect them into one collection and just insert them separately
global_includes = set()
# list of parsed headers
parsed_headers = []

for subdir, dirs, files in os.walk(source_path):
    for file in files:
        if file.endswith(".h") or file.endswith(".hpp"):
            filepath = os.path.join(subdir, file)
            # Open this header file
            f = open(filepath)
            src_lines = f.readlines()

            # Every header file might depend on another header file in our project.
            # This information is very important in order to create a valid single header.
            # this is the list of dependencies for every header
            deps = []
            # Source code lines that we will include into resulting header without any changes
            lines = []

            for line in src_lines:
                # Collect dependencies (includes) fot that file and remove them
                ds = dependency_pattern.match(line)
                if ds:
                    for dep in ds.groups():
                        deps.append(dep.split("/")[-1])
                    continue
                # Remove any pragma directives
                if pragma_pattern.match(line):
                    continue
                # Remove any global includes and remember it
                if include_pattern.match(line):
                    global_includes.add(line.replace("\n", "").replace(" ", ""))
                    continue
                lines.append(line)

            # Store parsed header
            parsed_headers.append({
                "name": filepath.split("/")[-1],
                "lines": lines,
                "deps": deps,
            })
            f.close()

# And now we're going to the construction of the header

# Add licence at the begging of the header (if presented)
if license_path:
    license = open(license_path)
    print("/*")
    for line in license.readlines():
        print(line.replace("\n", ""))
    print("*/\n")
    license.close()

print("#pragma once")
# Insert global includes
for include in global_includes:
    print(include)

# We will keep the list of already included files
included = []
skipped = 0
# And go through all headers until they gone
while len(parsed_headers) > 0:

    # Check for the edge case when we skipped all header files
    # and we still can't satisfy anyone's dependencies
    if skipped == len(parsed_headers):
        print("Error: can't satisfy dependencies!", file=sys.stderr)
        exit(1)

    # Take the first header from the stack
    file = parsed_headers.pop(0)

    # Check if dependencies of this header are satisfied
    satisfied = True
    for dep in file["deps"]:
        if dep not in included:
            satisfied = False
            break

    # If satisfied, we are including this header
    if satisfied:
        skipped = 0
        included.append(file["name"])
        for line in file['lines']:
            print(line, end="")
    else:
        # If not, we will push that header at the end of the stack
        skipped += 1
        parsed_headers.append(file)

