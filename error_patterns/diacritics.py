# -*- coding: utf-8 -*-
"""
Functions for identifying and extracting diacritics. Also used in conjunction
with PhonoErrorPatterns to add diacritics from the analysis data to
diacritic_definitions.yml

Usage with panphon / error_patterns.py:
1. Copy all IPA actual transcriptions to be used. Must be copied from a single
   column of a spreadsheet.
2. Execute update_panphon_diacritics()

Created on Tue Aug  4 17:09:45 2020
@author: Philip Combiths
@modified: 2023-06-30

To Do:
- Make edits directly to src/panphon yml within PhonoErrorPatterns
"""

import csv
import os
from tokenize import StringPrefix
from typing import List

import pandas.io.clipboard as pyperclip
import regex as re

# from regex_find_generator import regex_find_generator


def reDiac(diacritic_key="Phon", to_clipboard=False):
    """
    Generate regex pattern to locate diacritics.

    Args:
        diacritic_key : str in ['Phon', 'unicode_blocks', 'all'] to specify key type
            for generation of diacritic regex pattern. Default='Phon'
        to_clipboard (bool, optional): Copy resultant pattern as string to
        clipboard. Defaults to False.

    Requires:
        regex module as re

    Returns:
        compiled regex pattern

    *Revised from PhonDPA\auxiliary.py
    """

    # For UnicodeBlocks
    unicodeBlockList = [
        r"\p{InCombining_Diacritical_Marks_for_Symbols}",
        r"\p{InSuperscripts_and_Subscripts}",
        r"\p{InCombining_Diacritical_Marks}",
        r"\p{InSpacing_Modifier_Letters}",
        r"\p{InCombining_Diacritical_Marks_Extended}"
        r"\p{InCombining_Diacritical_Marks_Supplement}",
    ]
    additionalChars = [r"ᴸ", r"ᵇ", r":", r"<", r"←", r"=", r"'", r"‚", r"ᵊ"]

    # For Phon
    regex_special_chars = [
        "*",
        "+",
        "^",
        "$",
        ".",
        "|",  #'\\',
        "?",
        "{",
        "}",
        "[",
        "]",
        "(",
        ")",
    ]
    with open(
        os.path.join("error_patterns", "phon_diacritics.csv"),
        mode="r",
        encoding="utf-8",
    ) as f:
        file = csv.reader(f)
        phon_diacritics = [x[0] for x in file]

    phon_diacritics = [
        "\\" + x if x in regex_special_chars else x for x in phon_diacritics
    ]

    # Apply specified diacritics key
    if diacritic_key == "Phon":
        pattern = r"(" + r"|".join(phon_diacritics) + r")"
    if diacritic_key == "unicode_blocks":
        pattern = r"(" + r"|".join(unicodeBlockList + additionalChars) + r")"
    if diacritic_key == "all":
        pattern = (
            r"("
            + r"|".join(phon_diacritics + unicodeBlockList + additionalChars)
            + r")"
        )
    pattern_compiled = re.compile(pattern)
    # Copy uncompiled regex search string to clipboard
    if to_clipboard:
        pyperclip.copy(pattern)
    # Return compiled regex search
    return pattern_compiled


def import_csv_as_list(csv_file):
    """
    Imports a CSV file with a single column and returns the contents as a list.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        list: List of column data.

    Raises:
        AssertionError: If the CSV file contains more than one column.
    """
    column_data = []
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            assert len(row) == 1, "CSV contains more than one column"
            column_data.append(
                row[0]
            )  # Assuming single column, so we access the first (index 0) element

    return column_data


def extract_diacritics(
    join: bool = True,
    from_clipboard: bool = True,
    to_clipboard: bool = True,
    input_file: str = None,
) -> List[str]:
    """
    Extracts unique diacritics from a pasted column of IPA transcriptions.

    Args:
        join (bool): Specifies joining of diacritics in the same transcription. Default is True.
        from_clipboard (bool): Specifies whether to extract transcriptions from the clipboard. Default is True.
        to_clipboard (bool): Specifies whether to copy the extracted diacritics to the clipboard. Default is True.
        input_file (str): Path to the input CSV file. Required if from_clipboard is False.

    Returns:
        list: List of unique diacritics extracted from the transcriptions.
    """
    res = []
    if from_clipboard:
        trans_col = pyperclip.paste().strip("(").strip(")")
        trans_col_list = list(set(trans_col.split("\n")))
    else:
        assert os.path.isfile(input_file) or isinstance(
            input_file, io.IOBase
        ), "Invalid input_file"
        assert input_file.lower().endswith(".csv"), "Input file is not a CSV file"
        trans_col_list = list(set(import_csv_as_list(input_file)))
    for transcription in trans_col_list:
        diacritics = re.findall(reDiac(), transcription)
        if len(diacritics) == 0:
            continue
        else:
            if join:
                res.append(("".join(diacritics), "[name]", "[position]"))
            else:
                for d in diacritics:
                    res.append((d, "[name]", "[position]"))
    extracted_diacritics_list = list(set(res))
    if to_clipboard:
        pyperclip.copy("\t".join(extracted_diacritics_list))
    # print(extracted_diacritics_list)
    return extracted_diacritics_list


def import_diacritics(input_file):
    """
    Imports diacritics data from a CSV file and returns separate lists for pre-diacritics and post-diacritics.

    Args:
        input_file (str): The path to the input CSV file.
        output_file (str): The path to the output file.

    Returns:
        tuple: A tuple containing two lists - pre_diacritics_list and post_diacritics_list.

    Raises:
        FileNotFoundError: If the input_file is not found.

    """
    pre_diacritics_list = []
    post_diacritics_list = []

    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if it exists

        for row in reader:
            pre_diacritics_list.append((row[0], "[name]", "pre"))
            post_diacritics_list.append((row[1], "[name]", "post"))
    return pre_diacritics_list, post_diacritics_list


def file_search(filename, root_dir="C:/", ext=True, single_result=False):
    """Search by filename in a specified root directory.

    Args:
        filename (str): Filename as string
        root_dir (str, optional): Specificy root directory to search. Defaults to "C:/".
        ext (bool, optional): Filename given with or without extension.
        Defaults to True.

    Returns:
        list or str: List of file paths found or str of path if only one
    """
    file_list = []
    for root, dir, files in os.walk(os.getcwd()):  # from os.walk(root_dir)
        # Remove file extension if ext==False
        if not ext:
            files = [os.path.splitext(i[0]) for i in files]
        if filename in files:
            file_list.append(os.path.normpath(os.path.join(root, filename)))
    print(f"{len(file_list)} files found")
    for i in file_list:
        print(i)
    if single_result and len(file_list) == 1:
        return file_list[0]
    else:
        return file_list


def update_panphon_diacritics(
    from_clipboard: bool = False,
    to_clipboard: bool = False,
    input_file: str = None,
    input_option: int = 1,
    update_original: bool = False,
) -> None:
    """
    Generate a YAML string and optionally save it to a new YAML file.

    Args:
        from_clipboard (bool, optional): Specifies whether to extract input from the clipboard. Defaults to False.
        to_clipboard (bool, optional): Specifies whether to copy the new YAML string to the clipboard. Defaults to False.
        input_file (str, optional): Path to the input file. Required if from_clipboard is True. Defaults to None.
        output_file (str, optional): Path to the output YAML file. Required if output_file is specified and to_clipboard is False. Defaults to None.

    Returns:
        str: The generated YAML string.

    Raises:
        FileNotFoundError: If the diacritic definitions file is not found.
    """
    # Locate current diacritic_definitions.yml for reference

    cur_panphon_defs = "diacritic_definitions.yml"
    file_results = file_search(
        cur_panphon_defs,
        root_dir=os.path.join(os.path.expanduser("~"), "src"),
        ext=True,
    )
    # Uses the file instance in the panphon data directory within CWD
    for i in file_results:
        if r"panphon\panphon\data\diacritic_definitions.yml" in i:
            diacritic_definitions_location = i
    with open(diacritic_definitions_location, encoding="utf-8") as file:
        yaml_txt = file.read()
        print(f"Referencing: {diacritic_definitions_location}")

    if input_option == 1:
        new_diacritics = [
            x
            for x in extract_diacritics(
                from_clipboard=from_clipboard,
                to_clipboard=to_clipboard,
                input_file=input_file,
            )
            if x[0]
            not in yaml_txt  # Only extracts new diacritics not in current panphon
        ]
    if input_option == 2:
        pre_diacritics, post_diacritics = import_diacritics(input_file)
        # pre_diacritics = [
        #     x
        #     for x in pre_diacritics
        #     if x[0] not in yaml_txt  # Only extracts new diacritics not in current panphon
        #     count +=1
        # ]
        # post_diacritics = [
        #     x
        #     for x in post_diacritics
        #     if x[0] not in yaml_txt  # Only extracts new diacritics not in current panphon
        #     count +=1
        # ]
        # new_diacritics = [
        #     x
        #     for x in import_diacritics(input_file)
        #     if x[0] not in yaml_txt  # Only extracts new diacritics not in current panphon
        # ]

        new_diacritics = [
            x
            for sublist in import_diacritics(input_file)
            for x in sublist
            if x[0]
            not in yaml_txt  # Only extracts new diacritics not in current panphon
        ]
    print(f"{len(new_diacritics)} new diacritics extracted.")

    yaml_template = """
  - marker: [symbol] # Added
    name: "[name]"
    position: [position]
    conditions:
      - syl: "+"
      - syl: "-"
    content: {}
"""

    # Could add: exclude
    new_yaml_all = ""
    new_yaml_count = 0
    for i in new_diacritics:
        replacements = {"[symbol]": i[0], "[name]": i[1], "[position]": i[2]}
        new_yaml = yaml_template
        for key, replacement in replacements.items():
            new_yaml = new_yaml.replace(key, replacement)
        new_yaml_all += new_yaml
        new_yaml_count += 1
    print(f"{new_yaml_count} new YAML diacritics created.")

    # Add newlines and heading
    new_yaml_all = "\n# Added Diacritics\n" + new_yaml_all + "\n"

    if update_original:
        with open(diacritic_definitions_location, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Insert the new text at the third line
        lines.insert(2, new_yaml_all)

        with open(diacritic_definitions_location, "w", encoding="utf-8") as file:
            file.writelines(lines)
            print(
                "New diacritics written into ",
                os.path.abspath(diacritic_definitions_location),
            )
    elif not update_original:
        with open("new_diacritics_yaml.yml", "w", encoding="utf-8") as file:
            file.write(new_yaml_all)
            print(
                "New diacritics written to ",
                os.path.abspath("new_diacritics_yaml.yml"),
            )
    if to_clipboard:
        pyperclip.copy(new_yaml_all)
    return new_yaml_all


# 1. copy column of IPA actual transcriptions to clipboard
# 2. Run "update_panphon_diacritics()". This also runs extract_diacritics()
# 3. See PhonoErrorPatterns for instructions to update panphon diacritic definitions.

if __name__ == "__main__":
    update_panphon_diacritics(
        input_file=r"C:\Users\Philip\Documents\github\PhonoErrorPatterns\error_patterns\diacritics_key.csv",
        input_option=2,
        update_original=True,
    )
