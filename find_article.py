'''
Module that finds the article TITLE and BODY
'''

import datetime
import re
import requests as req
from bs4 import BeautifulSoup

from meta_modules.tag_symb_finder import Finder
from meta_modules.find_body_tag import BodyTagFinder

from meta_modules.cleaner import Cleaner
from meta_modules.constants import PARSER


class ArticleFinder(Finder):
    '''
    Class that automatically finds the TITLE and BODY of an article.

    `html`          - String - the HTML source code\n
    `skip_tags`     - List -tags to be skipped while counting the symbols inside the tags in the whole HTML\n
    `clean_tags`    - List - tags to be cleaned as a final filter (as an argument in Cleaner())\n
    `anchor_text`   - Boolean - False if you want to get the text WITH the anchor tag; default value - True\n
    `init_clean`    - Boolean - False for when you don't want to use the Cleaner before the Finder; default value - True
    '''

    def __init__(self, html, skip_tags=[], clean_tags=[], only_body=False, anchor_text=True, init_clean=True):
        super().__init__(html)

        self.skip_tags = skip_tags
        self.symbols_dct = None
        self.clean_tags = clean_tags
        self.anchor_text = anchor_text
        self.init_clean = init_clean


    def find(self):
        '''
        Returns a dictionary.

        Finds the full article, with its TITLE, BODY and the TIME
        of it being published.
        '''
        self.dct = {}

        # Getting the TITLE
        title = TitleFinder(self.html).find()
        
        # Getting the DATE
        date = DateFinder(self.html).find()

        # Initial use of the Cleaner
        if self.init_clean:
            cleaner = Cleaner(self.html)
            self.html = str(cleaner.clean())

        # Getting the BODY
        body_finder = BodyFinder(html=self.html, skip_tags=self.skip_tags)
        body = body_finder.find()


        self.symbols_dct = body_finder.get_tags_dct()

        try:
            self.dct['title'] = title
            self.dct['body'] = body
            self.dct['date'] = date
            self.__clean_article(clean_tags=self.clean_tags)

            return self.dct

        except TypeError:
            return "Article BODY or TITLE wasn't found"


    def __clean_article(self, clean_tags=[]):
        '''
        Removes the <a> tag, while leaving the text in it.
        Uses the meta_modules/cleaner.py module to clean it afterwards.
        '''

        # Removing the <a> tag, but leaving out the text in it
        if self.anchor_text:
            self.dct['body'] = re.sub(pattern='(?:<a[^<]+>)|(?:<\s*\/a\s*>)',
                                  repl='',
                                  string=self.dct['body'])

        self.dct['body'] = re.sub(pattern='\n',
                                  repl='',
                                  string=self.dct['body'])

        cleaner = Cleaner(self.dct['body'])
        self.dct['body'] = str(cleaner.clean(additional_tags=clean_tags))


class DateFinder(Finder):

    def __init__(self, html):
        super().__init__(html)


    def __re_search(self, pttrn):
        date = None
        match = re.search(pattern=pttrn,
                          string=self.html)

        if match:
            date = match.group(1)

        return date


    def find(self):
        date = None

        # Checking in the <meta> tags
        date = self.__re_search(r'[\'\"][^\'\"]+published_time[\'\"][^>]*content\s*=\s*[\'\"](.+?)[\'\"]')
        if date:
            return date

        # Checking in the <script> tags
        date = self.__re_search(r'[\'\"]datePublished[\'\"]:[\'\"](.+?)[\'\"]')
        if date:
            return date

        # Checking in the whole of the source code
        now = datetime.datetime.now()
        current_year = now.year
        date_pattern = f'((?:{current_year}[\-:\/]\d{{1,2}}[\-\/]\d{{1,2}})|(?:\d{{2}}[\-:\/]\d{{2}}[\-\/]{current_year}))'

        date = self.__re_search(date_pattern)

        return date



class TitleFinder(Finder):

    def __init__(self, html):
        super().__init__(html)


    def find(self):
        '''
        Finds the title using the meta tags in HTML
        '''

        meta_tag = 'meta'
        title = 'title'
        property = 'og:title'
        content = 'content'


        soup = BeautifulSoup(self.html, PARSER)

        try:
            try:
                # Finding the <meta> tag containing the title
                meta_found = soup.find(meta_tag, property=property)
                # Return the title from the <meta> tag 
                return f'<h1 class="auto-title">{meta_found[content]}</h1>'

            # If the title is not in a <meta> tag with the property='og:title'
            except TypeError:
                meta_found = soup.find(title)
                return f'<h1 class="auto-title">{meta_found.text}</h1>'
        except TypeError:
            print("The title has not been found!")


        return None


class BodyFinder(BodyTagFinder):
    '''
    Finds the parent tag that holds the body of an article

    `formatting_tags_to_skip`   - List - DO NOT skip counting the symbols inside of formatting tags such as - <i>, etc...\n
    `skip_tags`                 - List - tags to be skipped while counting the symbols inside the tags in the whole HTML\n
    '''

    def __init__(self, html, formatting_tags_to_skip=None, skip_tags=[]):
        super().__init__(html, formatting_tags_to_skip, skip_tags)
        self.tag = self.find_body_tag()
        print(f"TAG::: {self.tag}\n\n")

        self.soup = BeautifulSoup(html, PARSER)


    def find(self):
        '''
        Returns a string of the closest parent tag that has the whole body of the article
        '''

        article_tag = self.__find_best_parent()

        # Searching for siblings of the already found article_tag.
        # If the upper siblings of the article tags have the tag with the most symbols
        # and he has the most symbols in the scope of the previously refered sibling
        # the article_tag becomes the parent tag of all of them. 
        try:

            if article_tag.previous_sibling.previous_sibling:
                prev_sibl_children_dct = self.__get_child_symbs_dct(article_tag.previous_sibling.previous_sibling)

                if self.tag in prev_sibl_children_dct.keys():

                    if prev_sibl_children_dct[self.tag] == max(prev_sibl_children_dct.values()):
                        article_tag = article_tag.previous_sibling.parent
 
        # For when article_tag.previous_sibling is NoneType
        except (AttributeError, TypeError):
            pass

        body_string = f"{str(article_tag)}"

        return body_string

    def __find_best_parent(self):
        '''
        Find sthe the `self.tag` that is having the most symbols within the scope of the parent tag.

        This loops through the whole html, it finds the `self.tag` with maximum symbols, overall.
        Returns the parent tag.
        '''

        max_len = 0;
        article_tag = ""

        curr_max = 0

        for tag in self.soup.find_all(self.tag):
            curr_dct = self.__get_child_symbs_dct(tag.parent)

            if curr_dct[tag.name] == max(curr_dct.values()):
                if curr_dct[tag.name] > curr_max:
                    curr_max = curr_dct[tag.name]
                    article_tag = tag.parent

        return article_tag


    def __get_tags(self, parent_soup):
        '''
        Returns a set of all tags inside of `parent_soup`
        '''
        
        tag_set = set()

        for tag in parent_soup.find_all():
            tag_set.add(tag.name)

        return tag_set


    def __get_child_symbs_dct(self, parent_soup):
        '''
        Returns a dictionary - child of `parent_soup` => symbols

        Surrounding whitespace is not counted as symbols.
        '''

        tags = self.__get_tags(parent_soup)

        child_symbs_dct = {}

        for tag in tags:
            curr_tags = parent_soup.find_all(tag)
            symb_count = 0

            for curr_tag in curr_tags:
                try:
                    curr_string = curr_tag.text.strip()
                    symb_count += len(curr_string)

                except(AttributeError, TypeError):
                    pass

            child_symbs_dct[tag] = symb_count

        return child_symbs_dct



if __name__ == "__main__":

    url = 'https://www.campograndenews.com.br/economia/petrobras-anuncia-fracasso-na-venda-de-usina-de-fertilizantes-em-ms'

    resp = req.get(url)
    html = resp.text

    article_finder = ArticleFinder(html=html, 
                                   skip_tags=[], 
                                   clean_tags=[],
                                   anchor_text=True, 
                                   init_clean=True)
    dct = article_finder.find()
    title = dct['title']
    body = dct['body']
    date = dct['date']

    print(f"TITLE: {title}\n\nBODY: {body}\n\nDATE: {date}");