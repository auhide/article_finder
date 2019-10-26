'''
Cleaner configuration settings
'''
import os

HOME_PATH = os.path.dirname(os.path.abspath(__file__))

PARSER = 'lxml'
PERCENTAGE_LIMIT = 50.0

# Creating the Absolute Paths
CSV_PATH = os.path.join('data', 'tags_percent.csv')
CSV_PATH = os.path.join(HOME_PATH, CSV_PATH)

LOG_DIR = os.path.join('output', 'log.log')
LOG_DIR = os.path.join(HOME_PATH, LOG_DIR)

FORMATTING_TAGS = (
        'b',
        'strong',
        'i',
        'em',
        'mark',
        'small',
        'del',
        'ins',
        'sub',
        'sup',
)

DF_REM_TAGS = (
        'script',
        'a',
        'style',
)