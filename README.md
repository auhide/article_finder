# Article Finder

Package that finds the article TITLE and BODY, automatically

## Getting Started
### Install required packages
```
pip install -r requirements.txt
```

### How to use it

```python
from article_finder import ArticleFinder

article_finder = ArticleFinder(html=your_html)
article = article_finder.find()
 
print(article)
```

Parameters:
```
`html`          - String - the HTML source code\n *Mandatory*
`skip_tags`     - Tuple -tags to be skipped while counting the symbols inside the tags in the whole HTML
`clean_tags`    - Tuple - tags to be cleaned as a final filter (as an argument in Cleaner())
`only_body`     - Boolean - True if you want to only get the BODY; default value - False
```

Attributes:
article_object.dct - Dictionary - dictionary with keys representing the tags, and values representing 
the corresponding count of symbols for each tag