# DomainDuplicate

This tool detect duplicates over web pages of a domain to control crawling process.

It serializes the hash (title, text and domain) in a Mongo database (using SerializableDict from DataStructureTools) and store, for each hash, the url. So you can have different urls for on the same domain and the method isDuplicate answer True if the current title, text, domain are duplicates according to a threshold.

It is useful when you crawl urls (using Selenium) and you want to know if a html page is the same as others in the same web site (sometimes you get "refuse" page but you don't know it) so you can control the crawling process.

The structure of the SerializableDict is:

	{
		hash(title1, text1, domain1): [url1, url2...],
		hash(title2, text2, domain1): [url1, url2...],
		...
	}

## Install

	git clone git@github.com:hayj/DomainDuplicate.git
	pip install ./DomainDuplicate/wm-dist/*.tar.gz

## Usage

Call the init:

	dd = DomainDuplicate\
	(
		user=None, password=None, host="localhost", # mongo auth
		maxDuplicates=10, # Set the threshold
	)

See SerializableDict in from DataStructureTools for more information about the mongodb storage.

And call the `isDuplicate` method:

	dd.isDuplicate("The title", "<html>...", "http://test.com/2")

The method will convert the html in text and the url in domain name (for the hash key), then it will add the url in the right hash. It will return True if there are too much urls already stored for this hash (according to the threshold).