'''
Module that finds the article body
'''

import requests as req
import re
from bs4 import BeautifulSoup

from meta_modules.tag_symb_finder import Finder
from meta_modules.find_body_tag import BodyTagFinder

from meta_modules.cleaner import Cleaner
from meta_modules.constants import PARSER



class ArticleFinder(Finder):
    '''
    Class that automatically finds the TITLE and BODY of an article.

    `html`          - the HTML source code\n
    `skip_tags`     - tags to be skipped while counting the symbols inside the tags in the whole HTML\n
    `clean_tags`    - tags to be cleaned as a final filter (as an argument in Cleaner())\n
    `only_body`     - True if you want to only get the BODY; default value - False
    '''

    def __init__(self, html, skip_tags=(), clean_tags=[], only_body=False):
        super().__init__(html)

        self.skip_tags = skip_tags
        self.dct = None
        self.only_body = only_body
        self.clean_tags = clean_tags


    def find(self):
        '''
        Returns a string.

        Finds the full article, with either its TITLE and BODY
        or only BODY.
        '''

        title = TitleFinder(self.html).find()
        
        # Initial use of the Cleaner
        cleaner = Cleaner(self.html)
        self.html = str(cleaner.clean())

        body_finder = BodyFinder(src=self.html, skip_tags=self.skip_tags)
        body = body_finder.find()
        
        self.dct = body_finder.get_tags_dct()

        try:
            if self.only_body or not title:
                self.article = body
                self.__clean_article(clean_tags=self.clean_tags)

                return self.article

            article = title + body

            self.article = article
            self.__clean_article(clean_tags=self.clean_tags)

            return self.article

        except TypeError:
            return "Article BODY or TITLE wasn't found"


    def __clean_article(self, clean_tags=[]):
        '''
        Removes the <a> tag, while leaving the text in it.
        Uses the meta_modules/cleaner.py module to clean it afterwards.
        '''

        # Removing the <a> tag, but leaving out the text in it
        self.article = re.sub(pattern='(?:<a[^<]+>)|(?:<\s*\/a\s*>)',
                              repl='',
                              string=self.article)

        cleaner = Cleaner(self.article)
        self.article = cleaner.clean(additional_tags=clean_tags)



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

        try:
            soup = BeautifulSoup(html, PARSER)

            try:
                # Finding the <meta> tag containing the title
                meta_found = soup.find(meta_tag, property=property)

                # Getting the matches of the title in the whole html
                matches = re.findall(meta_found[content], self.html)
            # If the title is not in a <meta> tag with the property='og:title'
            except TypeError:
                meta_found = soup.find(title)
                return f'<h1 class="auto-title">{meta_found.text}</h1>'

            # Removing all matches that are greater or equal to the title in <meta>
            for match in matches:
                if len(match) >= len(meta_found[content]):
                    matches.remove(match)
            
            # If the matches list is NOT empty, return the title with the most symbols
            if len(matches):
                title = max(matches)
                title = title.strip()
                title = f'<h1 class="auto-title">{title}</h1>'

                return title
            
            # Else - return the title from the <meta> tag 
            return f'<h1 class="auto-title">{meta_found[content]}</h1'

        except TypeError:
            print("This website doesn't have the title in the meta tags.")

        return None



class BodyFinder(BodyTagFinder):
    '''
    Finds the parent tag that holds the body of an article
    '''

    def __init__(self, src, formatting_tags_to_skip=None, skip_tags=()):
        super().__init__(src, formatting_tags_to_skip, skip_tags)
        self.src = src
        self.tag = self.find_body_tag()
        print("TAG:::", self.tag)

        self.soup = BeautifulSoup(src, PARSER)


    def find(self):
        '''
        Returns a string of the closest parent tag that has the whole body of the article
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

        top_body = ""

        # Getting the part of the article body that is 
        # at the top of the normal one, if it exists
        try:
            if article_tag.previous_sibling.split():
                prev_sibl_children_dct = self.__get_child_symbs_dct(article_tag.previous_sibling)
                
                if self.tag in prev_sibl_children_dct.keys():

                    if prev_sibl_children_dct[self.tag] == max(prev_sibl_children_dct.values()):
                        top_body = str(article_tag.previous_sibling)
        
        # For when article_tag.previous_sibling is NoneType
        except (AttributeError, TypeError):
            pass

        body_string = f"{top_body}{str(article_tag)}"

        return body_string


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

        Surrounding whitespace is not counter as symbols.
        '''

        tags = self.__get_tags(parent_soup)

        child_symbs_dct = {}

        for tag in tags:
            curr_tags = parent_soup.find_all(tag)
            symb_count = 0

            for curr_tag in curr_tags:
                try:
                    curr_string = curr_tag.string.strip()
                    symb_count += len(curr_string)

                except (AttributeError, TypeError):
                    pass

                # child_symbs_dct[tag] = len(curr_text)
            child_symbs_dct[tag] = symb_count

        return child_symbs_dct



if __name__ == "__main__":

    url = 'http://www.milliyet.com.tr/gundem/batmanda-servis-minibusu-devrildi-1-olu-10-yarali-6066459'

    resp = req.get(url)
    html = resp.text

    # cleaner = Cleaner(html)
    # cleaner.clean()

    article = ArticleFinder(html, skip_tags=('span', 'h3', 'h4'))
    print(article.find())
    print(article.dct)