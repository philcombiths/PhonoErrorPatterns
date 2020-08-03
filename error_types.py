# -*- coding: utf-8 -*-
"""
From IPA target and actual transcriptions, generates error pattern labels with
error_pattern() for a single pair of transcriptions or error_pattern_table()
for a dataset of transcription pairs. error_quantifier() may be used to convert
error pattern str labels to numeric values.

Note: Check function docstrings for valid phonological types.

Setup Procedures:
1. Install or verify installation of panphon in the current python environment:
    e.g., 'pip install -e git+https://github.com/dmort27/panphon.git#egg=panphon'
2. Use extract_diacritics() to derive list of unique diacritics in dataset.
    - Requires transcriptions in a single column.
3. Update diacritic_definitions.yml in pandata/data with any diacritics
    not already in definitions.
4. Run command line from panphon directory to update definitions:
    'python bin/generate_ipa_all.py data/ipa_bases.csv -d data/diacritic_definitions.yml -s data/sort_order.yml data/ipa_all.csv'
5. Copy 'ipa_all.csv' and paste into the panphon/data directory in the
    current python environment 
    (e.g., 'C:/Users/Philip/Anaconda3/Lib/site-packages/panphon/data')
    
Example use case:
result = error_patterns_table("G:\My Drive\Phonological Typologies Lab\Projects\Spanish SSD Tx\Data\Processed\ICPLA 2020_2021\SpTxR\microdata_b.csv")            
    
Created on Tue Jul 28 14:58:21 2020
@author: Philip Combiths
"""

import pandas as pd
from collections import OrderedDict
import regex as re
import panphon
ft = panphon.FeatureTable()

def reDiac(): 
    """   
    Generate regex pattern to locate diacritics.
    
    Requires:
        regex module as re
    
    Returns:
        compiled regex pattern
    
    *Borrowed from PhonDPA\auxiliary.py
    """   
    unicodeBlockList = [r'\p{InCombining_Diacritical_Marks_for_Symbols}',
                        r'\p{InSuperscripts_and_Subscripts}',
                        r'\p{InCombining_Diacritical_Marks}',
                        r'\p{InSpacing_Modifier_Letters}',
                        r'\p{InCombining_Diacritical_Marks_Extended}'
                        r'\p{InCombining_Diacritical_Marks_Supplement}']

    additionalChars = [r'ᴸ', r'ᵇ', r':', r'<', r'←', r'=', r"'", r"‚", r"ᵊ"]

    pattern = r'(' + r'|'.join(unicodeBlockList+additionalChars) + r')'
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
    

def error_pattern(target, actual):    
    """
    Return the phonological error pattern from a target/actual pair of
    consonants or consonant sequences.
    
    Args:
        target : str of consonant or consonant sequence
        actual : str of consonant or consonant sequence
    
    Returns:
        error_pattern : str of error type label
    
    *Currently only tested for reliability with C and CC clusters.
    *CCC cluster epenthesis requires revision.
    """   
    error = None
    ############# 
    # Workarounds    
    # Sub ᵊ with ə for easier epenthesis ID
    if 'ᵊ' in actual:
        actual = actual.replace('ᵊ', 'ə')
    
    # Recognize ∅ as empty / deletion error
    if actual == '∅':
        error = "deletion"
        return error
    
    # Recognize 'nan' as empty / deletion error
    if actual == 'nan':
        error = "deletion"
        return error
    #############       
    # Generate segments and features with panphon
    t_segs = ft.ipa_segs(target)
    t_fts = ft.word_fts(target)
    a_segs = ft.ipa_segs(actual)
    a_fts = ft.word_fts(actual)
    t_dict = OrderedDict(zip(t_segs, t_fts))
    a_dict = OrderedDict(zip(a_segs, a_fts))
                    
    # Deletion
    if a_segs == ['∅'] or len(a_segs) == 0:
        error = 'deletion'
        return error
    
    # Accurate
    if t_segs == a_segs:
        error = 'accurate'
        return error
    
    # Errors by target structure type
    assert len(target) > 0, "target must be len>0"
    # assert no vowels
    if len(target) == 1:
        structure = "C"
        
        # Substitution
        if len(t_segs) == len(a_segs):
            error = "substitution"
            return error
        
        # All other errors
        else:
            error = "other"
            return error
               
    if len(target) == 2:
        structure = "CC"
   
        # Epenthesis
        for seg in a_dict:       
            if ('syl', 1) in a_dict[seg].items() and len(a_dict) > 2:
                # Contains a vowel
                error = 'epenthesis'            
                for seg in a_segs:
                    if ('syl', 1) in a_dict[seg].items():
                        continue
                    else:
                        if seg in t_segs:
                            if t_segs.index(seg) == 0:
                                error = error+'-C1pres'
                            if t_segs.index(seg) == 1:
                                error = error+'-C2pres'
                            if t_segs.index(seg) == 2:
                                error = error+'-C3pres'    
                        else:        
                            index = 0
                            smallest_dist = (index, 1)
                            for t_ft in t_fts:                        
                                dist = t_ft-a_dict[seg]                            
                                if dist < smallest_dist[1]:
                                    if t_segs[index] not in a_segs:
                                        smallest_dist = (index, dist)
                                index += 1
                            if smallest_dist[0] == 0:
                                error = error+'-C1sub'
                            if smallest_dist[0] == 1:
                                error = error+'-C2sub'
                            if smallest_dist[0] == 2:
                                error = error+'-C3sub'                        
                error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))
                return error
       
        # Cluster Reduction
        if len(a_segs) == len(t_segs)-1:
            error = "reduction"
            for seg in a_segs:
                if seg in t_segs:
                    if t_segs.index(seg) == 0:
                        error = error+'-C2del'
                    if t_segs.index(seg) == 1:
                        error = error+'-C1del'
                else:
                    index = 0
                    smallest_dist = (index, 1)
                    for feat in t_fts:
                        dist = feat-a_fts[0]
                        if dist < smallest_dist[1]:
                            smallest_dist = (index, dist)
                        index += 1
                    if smallest_dist[0] == 0:
                        error = error+'-C2del-C1sub'
                    if smallest_dist[0] == 1:
                        error = error+'-C1del-C2sub'
            if 'C1' not in error:
                error = error+'-C1pres'                        
            if 'C2' not in error:
                error = error+'-C2pres'
            error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))
            return error
                        
        # Substitution
        if len(a_segs) == len(t_segs):
            error = 'substitution'
            if a_segs[0] == t_segs[0]:
                if a_segs[1] != t_segs[1]:
                    error = error+'-C2sub'
                else:
                    error = error+'-C1sub-C2sub'
            else:
                if a_segs[1] != t_segs[1]:
                    error = error+'-C1sub-C2sub'
                else:
                    error = error+'-C1sub'
            if 'C1' not in error:
                error = error+'-C1pres'                        
            if 'C2' not in error:
                error = error+'-C2pres'
            error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))
            return error
        
        # All other errors
        else:
            error = "other"
            return error
                
    if len(target) == 3:
        structure = "CCC"
        
        # Epenthesis
        for seg in a_dict:       
            if ('syl', 1) in a_dict[seg].items():
                # Contains a vowel
                error = 'epenthesis'            
                for seg in a_segs:
                    if ('syl', 1) in a_dict[seg].items():
                        continue
                    else:
                        if seg in t_segs:
                            if t_segs.index(seg) == 0:
                                error = error+'-C1pres'
                            if t_segs.index(seg) == 1:
                                error = error+'-C2pres'
                            if t_segs.index(seg) == 2:
                                error = error+'-C3pres'    
                        else:        
                            index = 0
                            smallest_dist = (index, 1)
                            for t_ft in t_fts:                        
                                dist = t_ft-a_dict[seg]                            
                                if dist < smallest_dist[1]:
                                    if t_segs[index] not in a_segs:
                                        smallest_dist = (index, dist)
                                index += 1
                            if smallest_dist[0] == 0:
                                error = error+'-C1sub'
                            if smallest_dist[0] == 1:
                                error = error+'-C2sub'
                            if smallest_dist[0] == 2:
                                error = error+'-C3sub'                        
                error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))     
        
        # Cluster Reduction
        if len(a_segs) < len(t_segs):
            error = "reduction"
            for seg in a_segs:
                if seg in t_segs:
                    if t_segs.index(seg) == 0:
                        error = error+'-C1pres'
                    if t_segs.index(seg) == 1:
                        error = error+'-C2pres'
                    if t_segs.index(seg) == 2:
                        error = error+'-C3pres'
                else:        
                    index = 0
                    smallest_dist = (index, 1)
                    for t_ft in t_fts:                        
                        dist = t_ft-a_dict[seg]                            
                        if dist < smallest_dist[1]:
                            smallest_dist = (index, dist)
                        index += 1
                    if smallest_dist[0] == 0:
                        error = error+'-C1sub'
                    if smallest_dist[0] == 1:
                        error = error+'-C2sub'
                    if smallest_dist[0] == 2:
                        error = error+'-C3sub'
            if 'C1' not in error:
                error = error+'-C1del'                        
            if 'C2' not in error:
                error = error+'-C2del'
            if 'C3' not in error:
                error = error+'-C3del'            
            error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))
            return error
        
        # Substitution
        if len(a_segs) == len(t_segs):
            error = 'substitution'
            for seg in a_segs:
                if seg in t_segs:
                    if t_segs.index(seg) == 0:
                        error = error+'-C1pres'
                    if t_segs.index(seg) == 1:
                        error = error+'-C2pres'
                    if t_segs.index(seg) == 2:
                        error = error+'-C3pres'

                else:        
                    index = 0
                    smallest_dist = (index, 1)
                    for t_ft in t_fts:                        
                        dist = t_ft-a_dict[seg]                            
                        if dist < smallest_dist[1]:
                            if t_segs[index] not in a_segs:
                                smallest_dist = (index, dist)
                        index += 1
                    if smallest_dist[0] == 0:
                        error = error+'-C1sub'
                    if smallest_dist[0] == 1:
                        error = error+'-C2sub'
                    if smallest_dist[0] == 2:
                        error = error+'-C3sub'                        
            error = error.split('-')[0]+'-'+'-'.join(sorted(set(error.split('-')[1:])))
            return error
        
        # All other errors
        else:
            error = "other"
            return error
                        
        return error        
                
    if len(target) > 3:
        structure = "CCC+"
        print("Only C, CC, CCC are valid targets. CCC+ targets skipped")

def error_quantifier(x, correct_value=0.5, substitution_value=0.3, 
                     epenthesis_penalty=-0.3):
    """
    Generates a float value quantifying phonological error patterns
        generated by error_patterns(). Currently used for C and CC clusters, 
        but can be modified for use with C or CC+.
        
    Args:
        x : str error pattern input in format "pattern"+*"-C#pattern",
            generated by error_pattern()
        correct_value: float score added for a correct segment in a cluster. Default =
            0.5
        substitution_value : float score added for a substituted segment.
            Default = 0.
        epenthesis_penalty : float negative value added to an epenthesized
            segment. Default = -0.3
    
    Returns float error pattern value.
    """
    x_list = [x.split('-')[0], x.split('-')[1:]]
    score = 0
    if len(x_list[1]) > 2:
        print(f"WARNING: {x} suggests CC+ cluster not validated with this fx")
    # Accurate singleton or cluster
    if x == 'accurate':
        score = 1
        return score
    # Deleted singleton or cluster
    if x == 'deletion':
        score = 0
        return score
    # Epenthesis in a cluster
    if x_list[0] == 'epenthesis':
        score += epenthesis_penalty
    # Substituted singleton
    if x == 'substitution' :
        score += 0.5
        return score
    # For consonant clusters, allocate points per segment   
    for seg in x_list[1]:
        if 'pres' in seg:
            score += correct_value/
        if 'sub' in seg:
            score += substitution_value
    return score

def error_patterns_table(input_filename):
    """
    Generates error patterns for a dataset of transcriptions.
    
    Requires:
        error_patterns()
        panphon
        a csv file including transcription data with "IPA Actual" and
            "IPA Target" columns in cwd
    
    Creates:
        'error_patterns.csv' in cwd
        
    Returns:
        DataFrame with IPA Actual, IPA Target, and 'error_pattern' columns
    """

    data = pd.read_csv(input_filename, low_memory=False)    
    # Columns (5,10,13,14,15,30,38,39) have mixed types.    
    data['IPA Actual'] = data['IPA Actual'].astype('str')    
    error_patterns = []
    length = len(data['IPA Target'])
    print(f"Analyzing {length} transcriptions")
    counter = 0
    for row in zip(data['IPA Target'], data['IPA Actual']):
        error = error_pattern(row[0], row[1])
        error_patterns.append(error)
        counter +=1
        if counter % 1000 == 0:
            print(f"{counter} out of {length}")
    print(f"{length} transcriptions complete")
    error_patterns_series = pd.Series(error_patterns, name='error_pattern')    
    error_patterns_df = data[['IPA Target', 'IPA Actual']]    
    output_filename = 'error_patterns.csv'
    error_patterns_df = error_patterns_df.merge(error_patterns_series, left_index=True, right_index=True)
    error_patterns_df['error_basic'] = error_patterns_df['error_pattern'].apply(lambda x: x.split('-')[0])
    error_patterns_df['error_quant'] = error_patterns_df['error_pattern'].apply(error_quantifier)
    error_patterns_df.to_csv(output_filename, encoding='utf-8', index=False, na_rep='')
    print(f"Error patterns saved to {output_filename}")
    return error_patterns_df



        


