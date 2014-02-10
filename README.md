RapidStuffSearch
================

Python script to extract data from a RSS-Feed and do a basic ranking based on your search terms.

Install:
--------

Having python (2.7++) is mandatory! get it via macports or homebrew.
For organizing python packages I recommend installing 'easy_install'
as well.

Dependencies:
-------------

feedparser (sudo easy_install feedparser)
requests: (sudo easy_install requests)
BeautifulSoup: (sudo easy_install beautifulsoup4)

Usage:
------

Create your own config file. Look at the template config to have
a rough guide for search terms.

python filter.py <path/to/your/config.yaml>


Have fun! :-)


