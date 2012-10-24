# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
# Common utility code for commands

def print_table(table):
    """
    Takes a list of arrays and prints them neatly so the columns line up in preformatted text.
    The first line should be the headings, a row of underlines will automatically be added.
    See commands/pendingpackages.py for example of usage.
    """
    def _str(line):
        return [str(x) for x in line]

    # turn table of strings + objects into one only of strings
    strtable = [_str(line) for line in table]

    # calculate the column widths
    colwidth = [0 for x in table[0]]
    SPACE=2
    for line in strtable:
        i = 0
        for col in line:
            mylen = len(col)
            mylen += (SPACE-mylen%4)
            mylen += SPACE
            if colwidth[i] < mylen:
                colwidth[i] = mylen
            i += 1
    
    fmtstr = "".join(["%%-%ss" % cw for cw in colwidth])
    maxlen = sum(colwidth)
    
    print fmtstr % tuple(strtable[0])
    print "_" * maxlen
    
    for line in strtable[1:]:
        print fmtstr % tuple(line)
        
# eof
