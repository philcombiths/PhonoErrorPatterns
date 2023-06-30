===========
Phono Error Patterns
===========
Phono Error Patterns identifies error patterns from phonological transcriptions.

Specifically, from IPA target and actual transcriptions, generates error pattern 
labels with error_pattern() for a single pair of transcriptions or error_pattern_table()
for a dataset of transcription pairs. 

Note: Check function docstrings for valid phonological types.
Note: This script uses panphon package.

Usage
=========

### Example use case:
result = error_patterns_table("...microdata_c.csv")

### Debug Testing
test_cases = import_test_cases()
test_result = debug_testing(test_cases) 

Functions
=========

### error_pattern()

The `error_pattern()` function can be used to generate an error pattern label for a single pair of transcriptions. It takes two arguments: `target` (string) and `actual` (string), which represent the IPA target and actual transcriptions, respectively.

```python
from error_patterns import error_pattern

target = "kæt"
actual = "kæp"
error = error_pattern(target, actual)
print(error)  # Output: substitution-C2sub
```

### error_pattern_table()

The `error_pattern_table()` function can be used to generate error pattern labels for a dataset of transcription pairs. It takes a CSV file containing the transcription pairs as input and outputs a new CSV file with the error pattern labels appended.

```python
from error_patterns import error_pattern_table

input_file = "transcriptions.csv"
output_file = "transcriptions_with_errors.csv"
error_pattern_table(input_file, output_file)
```

### error_pattern_resolver()
The `error_pattern_resolver()` function takes a second pass throuhg the data and provides a more sophisticated algorithm for resolving error patterns labeled as "_other" by the `error_pattern()` function. It takes the same arguments as `error_pattern()` (i.e., `target` and `actual`) along with the pattern label and returns a tuple containing the resolved error pattern and an alignment list. This may be a better algorithm to replace error_pattern() in future update. Currently only works as expected for CC substitution and epenthesis patterns.

```python
from error_patterns import error_pattern_resolver

target = "plænt"
actual = "plɪmp"
pattern = "substitution_other"
resolved_pattern, alignment = error_pattern_resolver(target, actual, pattern)
print(resolved_pattern)  # Output: substitution
print(alignment)  # Output: [('æ', 'ɪ', 0.0)]
```

Dependencies
=========

The `error_patterns` package depends on the `panphon` package, which provides phonological features and segment data. Make sure to install it before using `error_patterns`.
Recommended panphon install procedures are provided. Accurate error pattern generation requires on definitions in panphon for all the base phones and diacritics that occur the input data. See documentation below and in the helper script diacritics.py for tools to update panphon definitions for your input data conventions.


Panphon Setup Procedures
=========
1. Install or verify installation of panphon in the current python environment:
    e.g., 'pip install -e git+https://github.com/dmort27/panphon.git#egg=panphon'
2. Use extract_diacritics() to derive list of unique diacritics in dataset.
3. Update diacritic_definitions.yml in panphon/data with any diacritics
    not already in definitions.
4. Run command line from panphon directory to update definitions:
    'python bin/generate_ipa_all.py data/ipa_bases.csv -d data/diacritic_definitions.yml -s data/sort_order.yml data/ipa_all.csv'

David R. Mortensen, Patrick Littell, Akash Bharadwaj, Kartik Goyal, 
	Chris Dyer, Lori Levin (2016). "PanPhon: A Resource for Mapping IPA 
	Segments to Articulatory Feature Vectors." Proceedings of COLING 2016, 
	the 26th International Conference on Computational Linguistics: 
	Technical Papers, pages 3475–3484, Osaka, Japan, December 11-17 2016.

Version
=========
0.2


License
========
Apache License 2.0
Copyright 2020 Philip Combiths
