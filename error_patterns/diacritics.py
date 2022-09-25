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
@author: Philip
"""

import csv
from tokenize import StringPrefix
import regex as re
import os
import pandas.io.clipboard as pyperclip
from regex_find_generator import regex_find_generator


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
    unicodeBlockList = [r'\p{InCombining_Diacritical_Marks_for_Symbols}',
                        r'\p{InSuperscripts_and_Subscripts}',
                        r'\p{InCombining_Diacritical_Marks}',
                        r'\p{InSpacing_Modifier_Letters}',
                        r'\p{InCombining_Diacritical_Marks_Extended}'
                        r'\p{InCombining_Diacritical_Marks_Supplement}']
    additionalChars = [r'ᴸ', r'ᵇ', r':', r'<', r'←', r'=', r"'", r"‚", r"ᵊ"]
    
    # For Phon
    regex_special_chars = ['*', '+', '^','$', '.','|', #'\\',
                           '?', '{', '}', '[', ']', '(', ')'] 
    with open("phon_diacritics.csv", mode="r", encoding='utf-8') as f:
        file = csv.reader(f)
        phon_diacritics = [x[0] for x in file]
        
    phon_diacritics = ["\\"+x if x in regex_special_chars else x for x in phon_diacritics]
    
    # Apply specified diacritics key
    if diacritic_key == "Phon":
        pattern = r'(' + r'|'.join(phon_diacritics) + r')'
    if diacritic_key == "unicode_blocks":
        pattern = r'(' + r'|'.join(unicodeBlockList+additionalChars) + r')'
    if diacritic_key == "all":
        pattern = r'(' + r'|'.join(phon_diacritics+unicodeBlockList+additionalChars) + r')'
    pattern_compiled = re.compile(pattern)
    # Copy uncompiled regex search string to clipboard
    if to_clipboard:
        pyperclip.copy(pattern)
    # Return compiled regex search  
    return pattern_compiled


def extract_diacritics(join=True, from_clipboard=True, to_clipboard=True):
    """
    Extracts unique diacritics from a pasted column of IPA transcriptions.
    
    Args:
        join : specifies joining of diacritics in the same transcription.
            Default True.
    
    Requires: 
        regex module as re
        reDiac()
    
    Returns list of unique str diacritics.
    """    
    res = []
    if from_clipboard:
        trans_col = pyperclip.paste().strip('(').strip(')')
    else:
        trans_col = input('Paste column of entries:')
    trans_col_list = trans_col.split("\n")
    for transcription in trans_col_list:
        # Find all diacritics using Phon reference list
        diacritics = re.findall(reDiac(), transcription)
        if len(diacritics) == 0:
            continue
        else:
            if join==True:
                # Join multiple diacritics in a transcription
                res.append(''.join(diacritics))
            if join==False:
                for d in diacritics:
                    res.append(d)
    extracted_diacritics_list = (set(res))
    if to_clipboard:
        pyperclip.copy('\t'.join(extracted_diacritics_list))
    print(extracted_diacritics_list)
    return extracted_diacritics_list


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
    for root, dir, files in os.walk(root_dir):
        # Remove file extension if ext==False
        if not ext:
            files = [os.path.splitext(i[0]) for i in files]
        if filename in files:
            file_list.append(os.path.normpath(os.path.join(root, filename) ) )
    print(f"{len(file_list)} files found")
    for i in file_list:
        print(i)
    if single_result and len(file_list)==1:
        return file_list[0]
    else:
        return file_list


def update_panphon_diacritics(to_clipboard=True):
    """Generate a string to paste into panphon diacritic_definitions document.

    Args:
        to_clipboard (bool, optional): Defaults to True.

    Returns:
        str: Text to paste into diacritic_definitions.yml
    """  
    filename='diacritic_definitions.yml'
    file_results = file_search(filename, root_dir="C:/src", ext=True)
    for i in file_results:
        if r"panphon\panphon\data\diacritic_definitions.yml" in i:
            diacritic_definitions_location = i
    with open(diacritic_definitions_location, encoding="utf-8") as file:
        yaml_txt = file.read()
    new_diacritics = [x for x in extract_diacritics(to_clipboard=False) 
                        if x not in yaml_txt]
    print(diacritic_definitions_location)

    yaml_template="""
    - marker: [symbol] # Added
        name: "[name]"
        position: [position]
        conditions:
        - syl: "+"
        - syl: "-"
        content: {}
    """
    new_yaml = ""
    for i in new_diacritics:
        new_yaml += yaml_template.replace('[symbol]', i)
    print(new_yaml)
    if to_clipboard:
        pyperclip.copy(new_yaml)
    return new_yaml
    
# 1. copy column of IPA actual transcriptions to clipboard
# 2. Run "update_panphon_diacritics()". This also runs extract_diacritics()
update_panphon_diacritics()