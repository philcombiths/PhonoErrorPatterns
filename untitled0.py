# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 10:51:22 2020

@author: Philip
"""

import panphon
ft = panphon.FeatureTable()

def error_pattern(target, actual):    
    """
    Return the phonological error pattern from a target/actual pair of
    consonants or consonant sequences.
    """    
    error = None   
    # Generate segments and features with panphon
    t_segs = ft.ipa_segs(target)
    t_fts = ft.word_fts(target)
    a_segs = ft.ipa_segs(actual)
    a_fts = ft.word_fts(actual)
    t_dict = OrderedDict(zip(t_segs, t_fts))
    a_dict = OrderedDict(zip(a_segs, a_fts))
    return error

def error_patterns_table(target, actual):
    error_patterns = []
    for pair in zip(target, actual):
        error = error_pattern(pair[0], pair[1])
        error_patterns.append(error)
    return error_patterns

target_list = ['bj', 'bj', 'bj', 'bj', 'bj', 'bj', 'bj', 'bj', 'bj']
actual_list = ['b', 'b', 'b', 'fj', 'w', 'b', 'b', 'v', 'b']

res = error_patterns_table(target_list, actual_list)