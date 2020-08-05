# -*- coding: utf-8 -*-
"""
Functions for identifying and extracting diacritics.

Created on Tue Aug  4 17:09:45 2020
@author: Philip
"""

import csv
import regex as re

def reDiac(diacritic_key="Phon"): 
    """   
    Generate regex pattern to locate diacritics.
    
    Args:
        diacritic_key : str in ['Phon', 'unicode_blocks', 'all'] to specify key type
            for generation of diacritic regex pattern. Default='Phon'
            
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
    if diacritic_key == "Phon":
        pattern = r'(' + r'|'.join(phon_diacritics) + r')'
    if diacritic_key == "unicode_blocks":
        pattern = r'(' + r'|'.join(unicodeBlockList+additionalChars) + r')'
    if diacritic_key == "all":
        pattern = r'(' + r'|'.join(phon_diacritics+unicodeBlockList+additionalChars) + r')'
    pattern = re.compile(pattern)    
    return pattern


def extract_diacritics(join=True):    
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
    trans_col = input('Paste column of entries:')
    trans_col_list = trans_col.split("\n")
    for transcription in trans_col_list:
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
    return list(set(res))