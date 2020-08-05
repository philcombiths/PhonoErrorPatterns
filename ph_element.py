# -*- coding: utf-8 -*-
"""
Customized classes drawing on FeaturesTable() functionality in panphon.

Created on Tue Aug  4 15:33:25 2020
@author: Philip Combiths
"""

import regex as re
import panphon
ft = panphon.FeatureTable()
from diacritics import reDiac

class ph_element(object):
    """Represents a phonological unit of analysis"""
    def __init__(self, string, tier='actual', parent=None, position=None):
        """Instantiates a ph_element object"""
        self.tier = tier
        self.string = string
        if isinstance(self, ph_segment):
            self.type = "segment"
        if isinstance(self, ph_cluster):
            self.type = "cluster"
        if type(self) == ph_element:
            self.type = "unspecified"        
        self.features = ft.word_fts(string)
        self.ipa = ft.ipa_segs(string)
        self.base = re.sub(reDiac(), '', string)
        self.diacritics = re.findall(reDiac(), string)
        self.parent = parent 
        self.position = position

    def convert_type(self):
        """Copies element as subtype based on length of object"""
        if len(self.ipa) == 1:
            self = ph_segment(self.string, self.tier)
        if len(self.ipa) > 1:
            self = ph_cluster(self.string, self.tier)
        return self
    
    def get_type(self):
        return self.type
        
    def get_ipa(self):
        return self.ipa
    
    def get_str(self):
        return self.string
    
    def get_base(self):
        """Get str of base segments"""
        return self.base
    
    def get_diacritics_list(self):
        return self.diacritics
    
    def get_diacritics(self):
        """Get str of diacritics"""
        return ''.join(self.diacritics)
    
    def get_features(self):
        return self.features
        
    def get_features_list(self):
        fts_list = [seg.items() for seg in self.features]
        return fts_list
    
    def __repr__(self):
        return f"{self.string}: {self.type}, parent={self.parent}, index={self.position}"
    def __str__(self):        
        return self.string


class ph_segment(ph_element):
    """Represents a phonological segment"""
    def __init__(self, string, tier='actual', parent=None, position=None):
        assert len(ft.ipa_segs(string)) == 1, "ph_segment object must be a single segment"
        ph_element.__init__(self, string, tier, parent, position)
        if any([('cons', 1),('syl', -1)]) in self.features[0].items():
            self.type = "consonant"
        elif ('syl', 1) in self.features[0].items():
            self.type = "vowel"     
    
    def fts(self):
        """get panphon "Segment" object with segment features"""
        return self.features[0]
            
    def __len__(self):
        return len(self.ipa)    


class ph_cluster(ph_element):
    """Represents a phonological cluster"""
    def __init__(self, string, tier='actual', parent=None, position=None):
        assert len(ft.ipa_segs(string)) > 1, "ph_cluster object must be multiple segments"
        ph_element.__init__(self, string, tier)        
        self.constituents = []        
        for i, seg in enumerate(ft.ipa_segs(string)):
           self.constituents.append(ph_segment(seg, self.tier, parent=self, position=i))
           
    def get_constituents(self):
        return self.constituents
    
    def __setitem__(self, index, value):
        self.constituents[index] = value
        
    def __getitem__(self, index):
        return self.constituents[index] 
    
    def __len__(self):
        return len(self.constituents)

