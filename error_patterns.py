# -*- coding: utf-8 -*-
"""
error_patterns version 0.1

Created on Tue Jul 28 14:58:21 2020
@author: Philip Combiths

From IPA target and actual transcriptions, generates error pattern labels with
error_pattern() for a single pair of transcriptions or error_pattern_table()
for a dataset of transcription pairs. 

error_pattern_resolver() takes a second pass through transcriptions with a more
sophisticated algorithm to resolve patterns labelled with "_other". This may be
a better algorithm to replace error_pattern() in future update. Currently only
works as expected for CC substitution and epenthesis patterns.

error_quantifier() may be used to convert error pattern str labels to numeric 
values.

error_patterns_table uses these functions in sequence and exports result to 
csv.

Note: Check function docstrings for valid phonological types.
Note: This script uses panphon package.

Panphon Setup Procedures:
1. Install or verify installation of panphon in the current python environment:
    e.g., 'pip install -e git+https://github.com/dmort27/panphon.git#egg=panphon'
2. Use extract_diacritics() to derive list of unique diacritics in dataset.
    - Requires transcriptions in a single column.
3. Update diacritic_definitions.yml in panphon/data with any diacritics
    not already in definitions.
4. Run command line from panphon directory to update definitions:
    'python bin/generate_ipa_all.py data/ipa_bases.csv -d data/diacritic_definitions.yml -s data/sort_order.yml data/ipa_all.csv'
5. Copy 'ipa_all.csv' and paste into the panphon/data directory in the
    current python environment 
    (e.g., 'C:/Users/Philip/Anaconda3/Lib/site-packages/panphon/data')

    David R. Mortensen, Patrick Littell, Akash Bharadwaj, Kartik Goyal, 
        Chris Dyer, Lori Levin (2016). "PanPhon: A Resource for Mapping IPA 
        Segments to Articulatory Feature Vectors." Proceedings of COLING 2016, 
        the 26th International Conference on Computational Linguistics: 
        Technical Papers, pages 3475–3484, Osaka, Japan, December 11-17 2016.
    
# Example use case:
result = error_patterns_table("...microdata_c.csv")

# Debug Testing
test_cases = import_test_cases()
test_result = debug_testing(test_cases)

"""

import pandas as pd
import numpy as np
import io
from diacritics import reDiac, extract_diacritics
from ph_element import ph_element, ph_segment, ph_cluster
import panphon
ft = panphon.FeatureTable()
    

def error_pattern(target, actual, debug=False):    
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
    *May replace this function with error_pattern_resolver()
    
    TO DO: fix issue: multiple actual segments whose smallest distance indicates
        substitution with the same target consonant.
    TO DO: Could determine instances that still count as "present" instead of 
        substitution: e.g., "kʴ" for "kr".
    TO DO: Specify vocalization substitution pattern
        
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
    
    # Generate segments and features from panphon
    t_segs = ft.ipa_segs(target)
    t_fts = ft.word_fts(target)
    a_segs = ft.ipa_segs(actual)
    a_fts = ft.word_fts(actual)
    a_pairs = list(zip(a_segs, a_fts))                    
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
    if 2 <= len(target) <= 3 :        
        # Epenthesis
        for seg in a_pairs:       
            if ('syl', 1) in seg[1].items() and len(a_pairs) > 2:
                # Contains a vowel
                error = 'epenthesis'                    
        # Cluster Reduction
        if len(a_segs) < len(t_segs):
            error = "reduction"
        # Substitution
        if len(a_segs) == len(t_segs):
             error = 'substitution'
        # By-Segment Errors
        if error in ['epenthesis', 'reduction', 'substitution']:
            for seg in a_pairs:
                # Skip vowels
                if ('syl', 1) in seg[1].items() and len(a_pairs) > 2:
                    continue   
                
                if seg[0] in t_segs:
                    # If segment re-occurs in cluster (MAY NOT NEED THIS IF STATEMENT)
                    if a_segs.count(seg[0]) > 1:
                        if t_segs.index(seg[0]) == 0: # and 'C1' not in error:
                            error = error+'-C1pres'
                        if t_segs.index(seg[0]) == 1: # and 'C2' not in error:
                            error = error+'-C2pres'
                        if t_segs.index(seg[0]) == 2: # and 'C3' not in error:
                            error = error+'-C3pres'
                    # All other cases
                    else:
                        if t_segs.index(seg[0]) == 0:
                            error = error+'-C1pres'
                        if t_segs.index(seg[0]) == 1:
                            error = error+'-C2pres'
                        if t_segs.index(seg[0]) == 2:
                            error = error+'-C3pres'                                                        
                else:
                    index = 0
                    smallest_dist = (index, 1)
                    for t_ft in t_fts:                        
                        dist = t_ft-seg[1]                            
                        # doesn't count equal segments in distance
                        if 0 < dist < smallest_dist[1]:
                            smallest_dist = (index, dist)
                        index += 1
                    if smallest_dist[0] == 0: # and 'C1' not in error:
                        error = error+'-C1sub'
                    if smallest_dist[0] == 1:# and 'C2' not in error:
                        error = error+'-C2sub' 
                    if smallest_dist[0] == 2:# and 'C3' not in error:
                        error = error+'-C3sub'           
            # Label attempts to make multiple assignments to a single segment
            # with "other". These will be analyzed by error_pattern_resolver()
            for i in range(len(t_segs)):
                if error.count(f'C{i+1}') > 1:
                    # DEBUG
                    if debug:
                        error = 'OTHER_'+error
                    else:
                        error = error.split('-')[0]+'_other'
                    return error
            # Add deletions for segments not identified above
            if error == 'substitution_other':
                pass
            else:
                for i in range(len(t_segs)):
                    if f'C{i+1}' not in error:
                        error = error+f'-C{i+1}del'
                   
            error = error.split('-')[0]+'-'+'-'.join(sorted(error.split('-')[1:]))           
            return error
        
        # All other errors
        else:
            error = "other"
            return error
                        
        return error        
                
    if len(target) > 3:
        structure = "CCC+"
        print("Only C, CC, CCC are valid targets. CCC+ targets skipped")
        


def error_pattern_resolver(target, actual, pattern):
    """
    A revised version of error_pattern() with a more sophisticated algorithm
    using ph_segment and ph_cluster classes and creating a matrix of distances
    to determine phonological error patterns. Current usage is only for CC
    epenthesis and substitution patterns already identified as "_other" by
    error_pattern()
    
    Args:
        target : str of consonant or consonant sequence
        actual : str of consonant or consonant sequence
        pattern : str of error pattern produced by error_pattern()
    
    Returns: tuple (str [error pattern], list[alignment]/None)
    
    Note: Future updates may replace error_pattern() with 
        error_pattern_resolver()
    """
    t = ph_element(target, 'target').convert_type()
    a = ph_element(actual, 'actual').convert_type()
    
    # Does not analyze singletons, reduction patterns, or CC+ clusters        
    error = ''
    if pattern == 'reduction_other':
        error = 'reduction_other'
        return error, None    
    if len(t) !=2:
        return error, None    
    if pattern =='epenthesis_other':
        error = 'epenthesis'
        if len(a) > 2:
            a_epenthesized = a[1]
        a_cons_only = []
        for seg in a:
            if ('syl', 1) in seg.fts.items():
                continue
            else:
                a_cons_only.append(seg)
        a = a_cons_only
        if len(a) > 2:
            return error+'_other', None
    else:
        if len(a) > 2:
            error = 'insertion_other'
            return error, None       
    if pattern == 'substitution_other' and len(t)==2 and len(a)==2:
        error = 'substitution'

    # Create target-actual feature distance matrix
    index = pd.Series([x for x in a])
    cols = pd.Series([x for x in t])        
    dist_matrix = pd.DataFrame(index.apply(
            lambda x: cols.apply(lambda y: x.fts-y.fts)))
    dist_matrix.index = index
    dist_matrix.columns = cols
    # When target and actual are same length, give a bonus to scores that
    # match relative position in the cluster
    position_match_bonus = -0.1
    if len(t) == len(a):
        for i in range(len(t)):
            dist_matrix.iloc[i,i] += position_match_bonus
            if dist_matrix.iloc[i,i] < 0:
                dist_matrix.iloc[i,i] = 0
    # For each row in first dist_matrix column (T1) iterate over possible
    # valid alignment combinations.
    col1 = dist_matrix.iloc[:,0]
    options = []
    for a1, dist1 in enumerate(col1):
        option = []
        t1 = (dist1, a1)
        option.append(t1)
        for i in range(1, len(t)):
            for a_i, dist in enumerate(dist_matrix.iloc[:,i]):
                if a_i == a1:
                    continue
                else:
                    t_i = (dist, a_i)
                    option.append(t_i)
        options.append(option)           
    # Compare options to ensure non-overlap in positions.
    for i_op in range(1, len(options)):  
        for i_seg in range(len(options[0])):    
            if options[0][i_seg][1] == options[i_op][i_seg][1]:
                print(f"{t}, {a}, {pattern}")
                raise Exception
    # Determine best segment alignment pairings
    distances = [sum([x[0] for x in option]) for option in options]
    distance_array = np.array(distances)
    best_dist = (min(distances), distances.index(min(distances)))
    if len(np.where(distance_array == best_dist[0])[0]) > 1:
        raise Exception("multiple ideal alignments found")        
    best_option = options[best_dist[1]]
    alignment = []
    for i, seg in enumerate(best_option):
        col_index = i
        row_index = seg[1]
        value = dist_matrix.iloc[row_index, col_index]
        targ = dist_matrix.iloc[:,col_index].name
        act = dist_matrix.iloc[row_index].name
        pair = (targ, act, value)            
        alignment.append(pair)            
    # Assign segment-by-segment patterns to error string
    for i, seg in enumerate(alignment):
        if seg[2] > 0:
            error += f"-C{i+1}sub"
        elif seg[2] == 0:
            # Check if IPA segments are equal in addition to 0 distance
            if seg[0].ipa != seg[1].ipa or seg[0].string != seg[1].string:
                # Distance = 0, but segments are different. Review these.
                error +=f"-C{i+1}sub[CHECK]"
            else:
                error += f"-C{i+1}pres"
    return error, alignment


def error_quantifier(x, full_correct_value=1, full_deletion_value=0, 
                     full_substitution_value=0.6, correct_seg_value=1, 
                     substitution_seg_value=0.6, epenthesis_penalty=-0.3):
    """
    Generates a float value quantifying phonological error patterns
        generated by error_patterns(). Currently used for C and CC clusters, 
        but can be modified for use with C or CC+.
        
    Args:
        x : str error pattern input in format "pattern"+*"-C#pattern",
            generated by error_pattern()
        correct_seg_value: float score added for a correct segment in a cluster. Default =
            0.5
        substitution_seg_value : float score added for a substituted segment.
            Default = 0.
        epenthesis_penalty : float negative value added to an epenthesized
            segment. Default = -0.3
    
    Returns float error pattern score.
    """
    if x == None:
        x = ''
    x_list = [x.split('-')[0], x.split('-')[1:]]
    x_len = len(x_list[1])
    score = 0
    if x_len == 0:
        x_len = 1
    # Accurate singleton or cluster
    if x == 'accurate':
        score = full_correct_value
        return score
    # Deleted singleton or cluster
    if x == 'deletion':
        score = full_deletion_value
        return full_deletion_value
    # Epenthesis in a cluster
    if x_list[0] == 'epenthesis':
        score += epenthesis_penalty
    # Substituted singleton
    if x == 'substitution' :
        score += full_substitution_value
        return score
    # Miscellaneous cluster substitution
    if x == 'substitution_other':
        score += full_substitution_value
        return score
    # Miscellaneous epenthesis
    if x == 'epenthesis_other':
        score += full_correct_value+epenthesis_penalty
        return score
    # For consonant clusters, allocate points per segment   
    for seg in x_list[1]:
        if 'pres' in seg:
            score += correct_seg_value/(x_len*correct_seg_value)
        if 'sub' in seg:
            score += substitution_seg_value/(x_len*correct_seg_value)
    return score


def error_patterns_table(input_filename, score_column=True, resolver=True):
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
    if resolver:
        resolved_error_list = []
        counter = 0
        for index, target, actual, pattern in error_patterns_df[['IPA Target', 'IPA Actual', 'error_pattern']].itertuples():            
            if "other" in pattern:
                resolved_error_list.append(error_pattern_resolver(target, actual, pattern)[0])
            else:
                resolved_error_list.append('')
            counter+=1
            if counter % 1000 == 0:
                print(f"Resolved {counter} out of {length}")
        error_patterns_df['resolved_error'] = resolved_error_list
        error_patterns_df['error_pattern'].loc[error_patterns_df['resolved_error'] != ''] = error_patterns_df['resolved_error']
    if score_column:
        error_patterns_df['error_score'] = error_patterns_df['error_pattern'].apply(error_quantifier)
        
    error_patterns_df.to_csv(output_filename, encoding='utf-8', index=False, na_rep='')
    print(f"Error patterns saved to {output_filename}")
    return error_patterns_df


def import_test_cases(test_cases='test_cases.txt'):
    """From txt file, import list of test cases for use with debug_testing()"""
    
    test_cases = []
    with io.open('test_cases.txt', encoding='utf-8', mode="r") as f:
        txt = f.readlines()    
    txt = [line.strip() for line in txt]
    txt = [line for line in txt if line]
    epenthesis_other = txt[txt.index('epenthesis_other:')+1:txt.index('other:')]
    epenthesis_other = [x.split('	') for x in epenthesis_other]
    test_cases.append(['epenthesis_other', epenthesis_other])
    
    other = txt[txt.index('other:')+1:txt.index('reduction_other:')]
    other = [x.split('	') for x in other]
    test_cases.append(['other', other])
    
    reduction_other = txt[txt.index('reduction_other:')+1:txt.index('substitution_other:')]
    reduction_other = [x.split('	') for x in reduction_other]
    test_cases.append(['reduction_other', reduction_other])

    substitution_other = txt[txt.index('substitution_other:')+1:]
    substitution_other = [x.split('	') for x in substitution_other]
    test_cases.append(['substitution_other', substitution_other])
    
    return test_cases
    

def debug_testing(test_cases_list):
    """from result of import_text_case() get error_pattern() results."""
    for group in test_cases_list:
        group.append([])
        for item in group[1]:
            group[2].append(error_pattern(item[0], item[1], debug=True))
            result_list = [[x[0], x[1]] for x in zip(group[1], group[2])]
        group.append(result_list)
    return test_cases_list