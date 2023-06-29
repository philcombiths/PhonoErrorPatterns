"""
Generate regex string for searching for a list of strings by adding "OR" syntax

Usage:
    1. Copy desired search terms from a column of a spreadsheet
    2. Execute regex_find_generator

Example:
regex_find_generator(input=None, from_clipboard=True, input_format='column',
    to_clipboard=True)

@author: Philip Combiths
Created 2022-09-24
"""
import pandas.io.clipboard as pyperclip
import regex as re


# May need to fix the "None" input.
def regex_find_generator(
    input=None, from_clipboard=True, input_format="column", to_clipboard=True
):
    """Generate regex string for list items in string input.

    Args:
        input (str, optional): Raw text to parse for regex search. Defaults to
        None.
        from_clipboard (bool, optional): Get input from clipboard. Defaults to
        True.
        input_format (str, optional): Format of input item separators of
        ['column', 'comma-separated', 'tab-separated']. Defaults to 'column'.
        to_clipboard (bool, optional): Copy resultant pattern as string to
        clipboard. Defaults to True.

    Returns:
        compiled regex pattern: Compiled regex pattern generated from input to
        function.
    """

    # Get input
    if input:
        raw_items = input
    else:
        if from_clipboard:
            raw_items = pyperclip.paste().strip()
        else:
            raw_items = input("Paste input: ")

    # Separate items per specified input format
    if input_format == "column":
        item_list = raw_items.split("\r\n")
    if input_format == "comma-separated":
        item_list = raw_items.split(",")
    if input_format == "tab-separated":
        item_list = raw_items.split("\t")

    # Special characters will need to be escaped for use in regex
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

    # escape special characters
    item_list = ["\\" + x if x in regex_special_chars else x for x in item_list]

    pattern = r"(" + r"|".join(item_list) + r")"
    pattern_compiled = re.compile(pattern)
    # Copy uncompiled regex search string to clipboard
    if to_clipboard:
        pyperclip.copy(pattern)
    print(pattern)
    # Return compiled regex search
    return pattern_compiled


regex_find_generator(input_format="tab-separated")
