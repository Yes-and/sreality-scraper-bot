# sreality-scraper-bot

* You need to put chromedriver in the /driver/ folder
* Required libraries : selenium (also pandas, time, math, re and random, but those are standard)

This is a scraper bot that can be used for sreality.cz
Usage : a scraper object is created and a url is passed. Important information (Link, ID, price etc.) are stored in a pandas dataframe object, which can be returned. If the bot fails at any time, every listing until the very last one is saved.

This is just a proof of concept, it shouldn't be used without asking for permission from sreality. Stealing data is illegal.
