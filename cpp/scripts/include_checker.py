# Copyright (c) 2019, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function
import sys
import re
import os
import subprocess
import argparse


IncludeRegex = re.compile(r"\s*#include\s*(\S+)")


def parseArgs():
    argparser = argparse.ArgumentParser(
        "Checks for a consistent '#include' syntax")
    argparser.add_argument("-regex", type=str,
                           default=r"[.](cu|cuh|h|hpp|cpp)$",
                           help="Regex string to filter in sources")
    argparser.add_argument("dirs", type=str, nargs="*",
                           help="List of dirs where to find sources")
    args = argparser.parse_args()
    args.regexCompiled = re.compile(args.regex)
    return args


def listAllSourceFiles(fileRegex, srcdirs):
    allFiles = []
    for srcdir in srcdirs:
        for root, dirs, files in os.walk(srcdir):
            for f in files:
                if re.search(fileRegex, f):
                    src = os.path.join(root, f)
                    allFiles.append(src)
    return allFiles


def checkIncludesIn(src):
    errs = []
    fp = open(src, "r")
    dir = os.path.dirname(src)
    lNum = 0
    for line in fp.readlines():
        match = IncludeRegex.search(line)
        lNum += 1
        if match is None:
            continue
        val = match.group(1)
        incFile = val[1:-1]  # strip out " or <
        if val[0] == "\"" and not os.path.exists(os.path.join(dir, incFile)):
            errs.append("Line:%d use #include <...>" % lNum)
        elif val[0] == "<" and os.path.exists(os.path.join(dir, incFile)):
            errs.append("Line:%d use #include \"...\"" % lNum)
    fp.close()
    return errs


def main():
    args = parseArgs()
    allFiles = listAllSourceFiles(args.regexCompiled, args.dirs)
    allErrs = {}
    for f in allFiles:
        errs = checkIncludesIn(f)
        if len(errs) > 0:
            allErrs[f] = errs
    if len(allErrs) == 0:
        print("include-check PASSED")
    else:
        print("include-check FAILED! See below for errors...")
        for f, errs in allErrs.items():
            print("File: %s" % f)
            for e in errs:
                print("  %s" % e)
        sys.exit(-1)
    return


if __name__ == "__main__":
    main()
