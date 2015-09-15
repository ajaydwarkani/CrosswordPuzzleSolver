#!/usr/bin/env python
#--------------------------------------------------------------------
#
#   @author Ajay Kumar <ajaydwarkani@gmail.com
#   
#   @version 1.00
#
#   @copyright 2015
#
#--------------------------------------------------------------------

import sys
import re
import os
import urllib
import urllib2
import urlparse

# Checking for OrderedDict functionality.
try:
	from collections import OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict
    except ImportError:
    	sys.exit('module "OrderedDict" is missing. Please install it by running "pip install ordereddict"')

# Checking for PIL module existence.
try:
	from bs4 import BeautifulSoup
except ImportError:
   	sys.exit('ERROR: module "BeautifulSoup4" is missing. Please install it by running "pip install BeautifulSoup4".')



class WebPageScraping:
	"""Parse through provided URL to find Crossword images, clues and their
		Answers
	"""

	def __init__(self, url):
		self.url = url
		self.host = self.__getUrlHost()
		self.__soup = None
		self.__clues = OrderedDict()
		self.__ACROSS = "Across"
		self.__DOWN = "Down"
		self.__crosswordImage = None

	
	def __printInfo(self, show, wordType):
		"""Prints Clues """
		if show:
			if (wordType == self.__ACROSS.lower() or wordType == "both"):
				print "\n%s\tClues" % self.__ACROSS
				for c, l in (self.__clues[self.__ACROSS].items()):
					print "%s\t%s" % (c, l)
			
			if (wordType == self.__DOWN.lower() or wordType == "both"):
				print "\n%s\tClues" % self.__DOWN
				for c, l in (self.__clues[self.__DOWN].items()):
					print "%s\t%s" % (c, l)


	def __readUrlPage(self, url, **urlData):
		data = None
		if len(urlData) > 0:
			data = urllib.urlencode(urlData)
		try:
			fileObj = urllib2.urlopen(url, data)
		except urllib2.HTTPError, e:
			sys.exit('ERROR: %s - Webpage not reachable, verify the url "%s" provided.' % (str(e.code), url))
		except urllib2.URLError, e:
			sys.exit('ERROR: URLError = %s' % str(e.reason))
		except httplib.HTTPException, e:
			sys.exit('ERROR: HTTPException = %s' % str(e.reason))
		except Exception:
			import traceback
			sys.exit('ERROR: generic exception: %s' % traceback.format_exc())
		
		#urlRedirected = fileObj.geturl()
		#urlInfo = fileObj.info()
		
		return fileObj.read()


	def __getUrlHost(self):
		parseResult = urlparse.urlparse(self.url)
		
		return "%s://%s" % (parseResult.scheme, parseResult.hostname)
	
	
	def __downloadFileFromUrl(self, url):
		#path, ext = os.path.splitext(url)
		#outputFileName = os.path.join(os.path.abspath(os.path.dirname(__file__)), "crossword_puzzle" + ext)
		self.__readUrlPage(url)		# Validate the URL link
		result = urllib.urlretrieve(url)
		
		return result[0] # Return downloaded local file path.
	

	def __getCrosswordCluesAndImage(self):
		"""This private method will read the contents of webpage and will extract
			Crossword clues and image from it.
		"""
		
		if self.__soup == None:
			self.__soup = BeautifulSoup(self.__readUrlPage(self.url), "html.parser")

		
		if len(self.__clues) == 2:
			return self.__clues
		
		crosswordTableId = 'printable_puzzle'
		tableTag = self.__soup.find('table', id = crosswordTableId)
		if tableTag == None:
			sys.exit('ERROR: Couldn\'t find the crossword clues. Either URL is incorrect or script needs to be updated to accomodate webpage changes.')

		imageTag = tableTag.find("img")
		if imageTag == None:
			sys.exit('ERROR: Couldn\'t find the crossword image. Either URL is incorrect or script needs to be updated to accomodate webpage changes.')
		
		imagePath = re.sub(r"\?.+", "", imageTag.get('src'))
		crosswordImageUrl = urlparse.urljoin(self.host, imagePath)
		self.__crosswordImage = self.__downloadFileFromUrl(crosswordImageUrl)
		
		clueTypes = [self.__ACROSS, self.__DOWN]
		
		for clueType in (clueTypes):
			tdTag = tableTag.find(string = clueType).parent.parent
			if tdTag == None:
				sys.exit('ERROR: Couldn\'t find "%s" clues. Either URL provided is not a valid crossword URL or script needs to be updated to accomodate webpage changes.' % clueTypes)
			isClueFound = False
			for index, string in enumerate(tdTag.stripped_strings):
				if index == 0 and clueType == string:
					self.__clues[clueType] = {}
					isClueFound = True
					continue
				if isClueFound and string.isdigit():
					Number = string
					continue
				if isClueFound:
					self.__clues[clueType][Number] = string.lstrip('. ').rstrip(' ')
					
		# Sorting
		self.__clues[self.__ACROSS] = OrderedDict(sorted(self.__clues[self.__ACROSS].items(), key = lambda(k,v):(int(k),v)))
		self.__clues[self.__DOWN] = OrderedDict(sorted(self.__clues[self.__DOWN].items(), key = lambda(k,v):(int(k),v)))
	
	
	def getClues(self, wordType = "both", show = False):
		"""Get the Crossword clues. Both across and down.
		
		Args:
			wordType (Optional[str]): Value can be either "across" or "down" or none
			show (Optional[bool]): Prints the clue list on console.
		Returns:
			OrderedDict: Dictionary of all the Crossword clues.
		"""
		
		if (len(self.__clues) == 0):
			self.__getCrosswordCluesAndImage()
			
		wordType= wordType.lower()
		if (wordType == "across"):
			self.__printInfo(show, wordType)
			return self.__clues[self.__ACROSS]
		elif (wordType == "down"):
			self.__printInfo(show, wordType)
			return self.__clues[self.__DOWN]
		else:
			self.__printInfo(show, wordType)
			return self.__clues


	def getCrosswordImage(self):
		"""Download crossword image from provided URL and returns local path.
		"""
		
		if len(self.__clues) == 0:
			self.__getCrosswordCluesAndImage()
		
		return self.__crosswordImage


	def getClueAnswers(self, clueQ, clueLength):
		"""Get the answer(s) for the clue from the provide URL
		
		Args:
			clueQ (string): Clue for which you need to find the answer
			show (string): Length or hint for the clue.
		Returns:
			List: List of all possible answers.
		"""

		Answers = []
		page = self.__readUrlPage(self.url, clue=clueQ, answer=clueLength)
		self.__soup = BeautifulSoup(page, "html.parser")
		
		
		def isWords(href):
			return href and re.compile("/words/").search(href)
		
		hrefResultSet = self.__soup.find_all(href=isWords)
		
		if len(hrefResultSet) > 0:
			for aElement in hrefResultSet:
				text = aElement.get_text()
				if len(text) == len(clueLength):
					Answers.append(text)
		
		return Answers

