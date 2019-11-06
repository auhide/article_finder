# Article Finder

Package that finds article's TITLE and BODY, automatically

## Getting Started
### Install required packages
```
pip install -r requirements.txt
```

### How to use it

```python
from find_article import ArticleFinder

article_finder = ArticleFinder(html=your_html)
article = article_finder.find()
 
print(article)
```

Parameters:
```
`html`          - String - the HTML source code *Mandatory*
`skip_tags`     - List - tags to be skipped while counting the symbols inside the tags in the whole HTML
`clean_tags`    - List - tags to be cleaned as a final filter (as an argument in Cleaner())
`only_body`     - Boolean - True if you want to only get the BODY; default value - False
`anchor_text`   - Boolean - False if you want to get the text WITH the anchor tag; default value - True
`init_clean`    - Boolean - False for when you don't want to use the Cleaner before the Finder; default value - True
```

Attributes:
```
article_object.dct - Dictionary - dictionary with keys representing the tags, and values representing 
the corresponding count of symbols for each tag
```
