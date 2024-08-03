# Simple script that compares every file in `out/game/obj` with a base directory
# This is useful for when you expect your compilation output to be identical, ie. when you've just made formatting only changes
# If every file matches...you should be able to be confident that you have broken nothing!

import os
import hashlib
import argparse

parser = argparse.ArgumentParser("compare-compilation-outputs")
parser.add_argument("--base", help="The base branch directories", type=str)
parser.add_argument("--compare", help="The potentially modified directories to compare", type=str)
parser.add_argument("--markdown", help="The format to output results as a markdown file './comp-diff-report.md'", action="store_true")
args = parser.parse_args()

to_markdown_file = False
if args.markdown:
    to_markdown_file = True

# Usage example
base_directory = args.base
compare_directory = args.compare

markdown_lines = []

def hash_file(filepath):
    """Returns the MD5 hash of the file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def compare_directories(base_dir, compare_dir):
    """Compares files in two directories based on their MD5 hash."""
    mismatched_files = []
    missing_files = []

    # Iterate through files in the base directory
    total_files = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file is ".gitignore":
                continue
            total_files = total_files + 1

            base_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(base_file_path, base_dir)
            compare_file_path = os.path.join(compare_dir, relative_path)

            if os.path.exists(compare_file_path):
                base_file_hash = hash_file(base_file_path)
                compare_file_hash = hash_file(compare_file_path)
                if base_file_hash != compare_file_hash:
                    mismatched_files.append(relative_path)
            else:
                missing_files.append(relative_path)

    # Report results
    print(f'Comparing {base_directory} with {compare_directory}')
    markdown_lines.append(f'### Comparing `{base_directory}` with `{compare_directory}`')
    if not mismatched_files and not missing_files:
        print("All files matched successfully.")
        markdown_lines.append(f'All `{total_files}` files matched successfully ✅')
        return 0
    else:
        markdown_lines.append(f'### Comparing `{base_directory}` with `{compare_directory}`')
        markdown_lines.append(f'Found potential problems ❌')
        markdown_lines.append(f'- {len(mismatched_files)} different files:')
        markdown_lines.append(f'- {len(missing_files)} missing files:')
        markdown_lines.append("| file | result |")
        markdown_lines.append("|------|--------|")
        if mismatched_files:
            print("Mismatched files:")
            markdown_printed_already = 0
            for file in mismatched_files:
                print(f" - {file}")
                if markdown_printed_already < 25:
                    markdown_lines.append(f"| {file} | different |")
                    markdown_printed_already = markdown_printed_already + 1
            if len(mismatched_files) > 25:
                markdown_lines.append(f"| ...and {len(mismatched_files) - 25} other files | different |")
        if missing_files:
            print("Missing files:")
            markdown_printed_already = 0
            for file in missing_files:
                print(f" - {file}")
                if markdown_printed_already < 25:
                    markdown_lines.append(f"| {file} | missing |")
                    markdown_printed_already = markdown_printed_already + 1
            if len(missing_files) > 25:
                markdown_lines.append(f"| ...and {len(missing_files) - 25} other files | missing |")
        return 1


result = compare_directories(base_directory, compare_directory)

if to_markdown_file:
    with open('./comp-diff-report.md', 'w') as md_file:
        md_file.writelines(markdown_lines)
        print("Wrote results to ./comp-diff-report.md")

exit(result)