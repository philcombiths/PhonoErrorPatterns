# Author
Philip Combiths

# Date
7/30/2020

# phono_error_patterns
Identifies error patterns from phonological transcriptions.

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
 
