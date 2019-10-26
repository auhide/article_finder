
'''
Module that finds all tags, each tag with its symbols counter
'''

import requests as req
import re

from bs4 import BeautifulSoup
import pandas as pd

from meta_modules.constants import FORMATTING_TAGS



class Finder:
    '''
    Base class, from which all Finder SubClasses inherit
    having an HTML attribute
    '''

    def __init__(self, html):
        self.html = html

    def find(self):
        pass



class TagSymbFinder(Finder):
    '''
    This class' purpose is to create a Dictionary with Tag: Symbols
    '''

    def __init__(self, html):
        super().__init__(html)


    def __single_tag_counter(self, html, tag):
        '''
        Returns a tuple of (tag, characters_inside_tag)

        Matches all text using Regex, for the `tag` attribute
        '''
        
        get_tag_text = f"<({tag})(?:[^>]+)?>([^<]+)<\/{tag}>"

        # List of matched tuples(1st group - TAG, 2nd group - SYMBOLS)
        tag_count = re.findall(get_tag_text, html)

        tag_counter = 0

        for _, curr_count in tag_count:
            curr_count = curr_count.strip()
            tag_counter += len(curr_count)

        return (tag, tag_counter) 


    def get_tags_counter(self, formatting_tags_to_skip=None):
        '''
        Returns a Dictionary with key:value - tag:symbols

        Goes over all tags in the HTML, then using __single_tag_counter(),
        counts the Symbols inside each one of them.
        E.g. if the symbols in ALL <a> tags are 21,
        the dictionary will have: a => 21
        '''
        
        # `FORMATTING_TAGS` is a list of formatting tags that in some cases need to be removed
        # for their text to be read properly
        formatting_tags_to_rem = FORMATTING_TAGS

        if formatting_tags_to_skip:
            # Removing specific formatting tags from the list of tags to NOT be aknowledged for symbol counting
            formatting_tags_to_rem = [tag for tag in FORMATTING_TAGS if tag not in formatting_tags_to_skip]

        soup = BeautifulSoup(self.html, 'lxml')
        new_soup = BeautifulSoup(self.html, 'lxml')
        
        tags = set()

        for tag in soup.find_all():
            tags.add(tag.name)

        tags = sorted(list(tags))
        tag_counter_dict = {}

        for i, tag in enumerate(tags):
            soup_formatted = new_soup

            if tag not in formatting_tags_to_rem:

                for f_tag in formatting_tags_to_rem:
                    
                    for curr_subtag in soup_formatted(f_tag):
                        curr_subtag.decompose()

            tag_counter = self.__single_tag_counter(str(soup_formatted), tag)
            
            # If there are characters inside the tag
            if tag_counter[1]:
                tag_counter_dict[tag_counter[0]] = tag_counter[1]

        return tag_counter_dict