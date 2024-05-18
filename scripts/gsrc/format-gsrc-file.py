# import glob
# import json
# import os
# files = glob.glob("./goal_src/jak1/**/*.gc", recursive=True)
# json_data = []
# for file in files:
#     json_data.append({'path': os.path.abspath(file), 'status': 'not-formatted'})

# with open("./scripts/gsrc/format-jak1.json", "w") as f:
#     f.write(json.dumps(json_data, indent=2))

import json
import subprocess
import sys

apply_status = None
if len(sys.argv) > 1:
    apply_status = sys.argv[1]

with open("./scripts/gsrc/format-jak1.json", "r") as f:
    formatting_progress = json.load(f)

# find the next file
curr_file = None
curr_file_index = 0
go_to_next = False
open_file_in_vscode = False
if apply_status == "next":
    go_to_next = True
    open_file_in_vscode = True

for index, file in enumerate(formatting_progress):
    if file['status'] == 'not-formatted':
        if go_to_next:
            print(f"Marking {file['path']} as formatted")
            formatting_progress[index]['status'] = 'formatted'
            go_to_next = False
        else:
            curr_file = file['path']
            curr_file_index = index
            if open_file_in_vscode:
                subprocess.run(["C:\\Users\\xtvas\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd", file['path']]) 
            break

# format it
print(f"Formatting {curr_file}")
subprocess.run(["./out/build/Debug/bin/formatter", "--write", "--file", curr_file]) 

# save status
if apply_status is not None and (apply_status == "skip" or apply_status == "next"):
    # TODO - add skip support back if i ever want to use it
    with open("./scripts/gsrc/format-jak1.json", "w") as f:
        f.write(json.dumps(formatting_progress, indent=2))

subprocess.run(["git", "diff", "--shortstat", "origin/master"]) 