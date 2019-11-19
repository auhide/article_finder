'''
Module with which we try to scrape the text off an article automatically
'''


from meta_modules.tag_symb_finder import TagSymbFinder

import requests as req
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from meta_modules.constants import DF_REM_TAGS


class BodyTagFinder(TagSymbFinder):
    '''
    An object of this class finds the ARTICLE BODY tag.
    You can get the tag with the find_body_tag() method.
    '''

    def __init__(self, html, formatting_tags_to_skip=None, skip_tags=[]):

        super().__init__(html)
        self.skip_tags = skip_tags

        self.dct = self.get_tags_counter(formatting_tags_to_skip)
        self.df = self.__dct_to_df()


    def find_body_tag(self):
        '''
        Returns a string representing the tag with the highest amount of symbols.

        Uses padnas.DataFrame object to remove tags like <style>, <a>, <script>, <div> from the dictionary.
        Then gets the tag with the most characters and returns it as a stripped string.
        '''

        self.__df_rem_tags()

        max_row = self.df[self.df['Symbols'] == self.df['Symbols'].max()]
        tag = max_row['Tag'].to_string(index=False)

        return tag.strip()

    
    def __df_rem_tags(self):
        '''
        Takes a list of tags(`tags_to_rem`) and removes them from the DataFrame of the object
        '''
        

        for tag in DF_REM_TAGS + self.skip_tags:
            try:
                self.df = self.df[self.df['Tag'] != tag]
            except:
                print(f"There was no <{tag}> in this DataFrame");



    def __dct_to_df(self):
        '''Converts dictionary to pandas.DataFrame'''

        df = pd.DataFrame(list(self.dct.items()))
        df.columns = ['Tag', 'Symbols']

        # print(df)

        return df

    
    def get_tags_dct(self):

        return self.dct
    



if __name__ == "__main__":

    url = 'https://www.zf.ro/zf-20-de-ani/zf-la-20-de-ani-evenimentul-anului-2012-proiectul-autostrazii-bechtel-un-esec-de-1-4-mld-euro-infrastructura-azi-in-romania-un-esec-de-zeci-de-miliarde-de-euro-anual-17622664'

    resp = req.get(url)
    html = resp.text

    scraper = BodyTagFinder(html)

    print(scraper.find_body_tag())