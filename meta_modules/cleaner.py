import os
import sys
import re

import requests

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from meta_modules.constants import *



class Cleaner:

    # Not removing these tags because they are parents of every tag
    tags_not_to_remove = ["body", "head", "html"]


    def __init__(self, src):
        self.init_src = src


        # Creating the BeautifulSoup Object
        self.soup = BeautifulSoup(self.init_src, PARSER)

        # Creating the variable self.tags
        self.__get_tags()

        # Creating the variable self.csv_tags
        self.__csv_tags_stats()

        # Creating the variable self.common_tags
        self.__common_tags()



    def __get_tags(self):
        '''
        Creates a list with unique values - tags of the source code 
        '''

        self.tags = []

        for tag in self.soup.find_all():

            if tag.name not in self.tags_not_to_remove:
                self.tags.append(tag.name)

        # Filtering only unique tags
        self.tags = list(set(self.tags))




    def __csv_tags_stats(self):
        '''
        Creates a DataFrame out of the Excel file in the data/ directory.
        Then filters out tags that will NOT be removed, by the percentage regarding each tag. 
        '''

        # Filtering the tags by percentage
        # Ordering the tags from the CSV file in descending order
        df = pd.read_csv(CSV_PATH, error_bad_lines=False)
        df = df[df["Percent"] > PERCENTAGE_LIMIT].sort_values(by=["Percent"], 
                                                              ascending=False)

        # Making a list out of all remaining tags
        np.asarray(df)
        df = np.transpose(df["Tag"])
        
        self.csv_tags = list(df)



    def __clean_comments(self):
        '''
        Removes the comments off the HTML
        '''

        re_comments = r"<!\-\-[^~]+?\-\->";

        curr_html = str(self.soup)

        new_html = re.sub(pattern=re_comments,
                          repl='',
                          string=curr_html,
                          flags=re.MULTILINE)

        self.soup = BeautifulSoup(new_html, PARSER)



    def __clean_empty_tags(self):
        '''
        Removes empty tag, recursively, not in the sense of actually using recursion,
        but as a way of solution design.
        '''

        curr_string = str(self.soup)

        re_empty_tags = r"<([^>]+)(?:[^>]+)?>[\W]*?<\/\1>"

        prev_string = ''

        while prev_string != curr_string:
            prev_string = curr_string
            
            curr_string = re.sub(pattern=re_empty_tags,
                                 repl='',
                                 string=curr_string,
                                 flags=re.MULTILINE)
        

        self.soup = BeautifulSoup(curr_string, PARSER)



    def __common_tags(self):
        '''
        Gets the common tags between the chosen Excel tags - __csv_tags_stats() and
        the tags in the html source code - __get_tags()
        '''
        
        self.common_tags = []

        for tag in self.tags:

            if tag in self.csv_tags:
                self.common_tags.append(tag)



    def __clean_additional(self, tags):
        '''
        Cleans tags that are not in the list of the ones to be deleted.
        '''

        for tag in tags:

            for curr_tag in self.soup.find_all(tag):
                self.deleted_tags.add(curr_tag.name)
                curr_tag.decompose()



    def save_source(self, filename="source", ext="html"):
        '''
        Saves the result of the cleaning in the data/ folder.
        '''

        with open(f"{filename}.{ext}", "w", encoding="utf-8") as f:
            soup_str = str(self.soup)
            f.write(soup_str)



    def clean(self, additional_tags=None, skip_tags=[]):
        '''
        Removes all unneeded tags.
        '''

        self.deleted_tags = set()

        for tag in self.tags:

            if tag not in skip_tags:

                if tag not in self.common_tags:
                    
                    for curr_tag in self.soup.find_all(tag):
                        self.deleted_tags.add(curr_tag.name)
                        curr_tag.decompose()
            
        if additional_tags:
            self.__clean_additional(additional_tags)
        
        self.__clean_comments()
        
        self.__clean_empty_tags()


        return self

  

    def minify(self):
        '''
        Creates a variable self.minified which is the source code
        without whitespace between tags.
        '''
        
        pattern = r">\s*<"

        self.minified = re.sub(pattern=pattern,
                               repl="><",
                               string=str(self.soup),
                               flags=re.MULTILINE)

        return self



    def get_removed_tags(self):
        '''
        Returns a list of all deleted tags.
        '''
        
        return self.deleted_tags



    def __str__(self):

        return str(self.soup)


if __name__ == "__main__":

    # Getting the first argument off the console
    url = sys.argv[1]

    # Getting the HTML source
    resp = requests.get(url)
    src = resp.text

    cleaner = Cleaner(src)

    cleaner.clean(additional_tags=['a'], skip_tags=['figure', 'figcaption'])

    cleaner.minify()

    cleaner.save_source()
    