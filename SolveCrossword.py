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
import os
import time
import math

# Checking for OrderedDict functionality.
try:
	from collections import OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict
    except ImportError:
    	sys.exit('module "OrderedDict" is missing. Please install it by running "pip install ordereddict"')

from WebPageScraping import *
from ProcessCrosswordImage import *



class SolveCrossword(WebPageScraping, ProcessCrosswordImage):
	"""Analyzes crossword image and calculates word length for 
		each clue for both "across" and "down" direction.
	"""

	def __init__(self, urlCrossword,
				 urlCluesSearch = "http://crosswordheaven.com/search/result",
				 noOfCells = 15):
		
		wpsCrossword = WebPageScraping(urlCrossword)
		pcm = ProcessCrosswordImage(wpsCrossword.getCrosswordImage(), noOfCells)

		self.wpsFindClueAnswers = WebPageScraping(urlCluesSearch)
		
		self.clues = wpsCrossword.getClues()
		self.cluesLength = pcm.getWordsLength()
		self.totalClues = pcm.getTotalClues()
		self.__ACROSS = "Across"
		self.__DOWN = "Down"
		self.noOfCells = noOfCells
		
		self.cellData = OrderedDict()
	
	
	def __findClueAnswers(self):
		"""Iterate through clue no.s and call __answerLookup to find the final
			answer.
		"""
		
		for cellTxt in range(1, self.totalClues):
			cellTxtStr = str(cellTxt)
			if cellTxtStr in self.cluesLength[self.__ACROSS]:
				self.__answerLookup(cellTxtStr, self.__ACROSS)
			
			if cellTxtStr in self.cluesLength[self.__DOWN]:
				self.__answerLookup(cellTxtStr, self.__DOWN)
		
		# Add missing cell no.(s) with "#" as value.
		for cellNo in range(1, self.noOfCells * self.noOfCells):
			if cellNo not in self.cellData:
				self.cellData[cellNo] = "#"
		
		# Sort
		self.cellData = OrderedDict(sorted(self.cellData.items(), key = lambda(k,v):(int(k),v)))


	def __answerLookup(self, cellTxtStr, wordType):
		"""Get the final answer for all the clues from answer array and store in
			dictionary with respective cell no.
		
		Args:
			cellTxtStr (string): Clue cell no.
			wordType (Optional[str]): Value can be either "across" or "down"
		"""
		
		length = self.cluesLength[wordType][cellTxtStr]['length']
		cellNo = self.cluesLength[wordType][cellTxtStr]['cellno']
		clue = self.clues[wordType][cellTxtStr]
		hint = ""
		for index, wordCell in enumerate(range(0, length)):
			if wordType == self.__ACROSS:
				cell_tmp = cellNo + index
			else:
				cell_tmp = cellNo + (index * self.noOfCells)
			if cell_tmp in self.cellData:
				hint +=  self.cellData[cell_tmp]
			else:
				hint += "?"
			
		answers = self.wpsFindClueAnswers.getClueAnswers(clue, hint)
		for answer in (answers):
			for index, c in enumerate(list(answer)):
				if wordType == self.__ACROSS:
					cellDataIndex = cellNo + index
				else:
					cellDataIndex = cellNo + (index * self.noOfCells)
				if (cellDataIndex in self.cellData and self.cellData[cellDataIndex] != c):
					print 'WARNING: Collision between "%s" and "%s" for clue "%s" (%s)' % (self.cellData[cellDataIndex], c, cellTxtStr, wordType)
					self.cellData[cellDataIndex] = "."
				else:
					self.cellData[cellDataIndex] = c
			break
		
		rowNumber = int(math.ceil(float(cellNo) / float(self.noOfCells)))
		if wordType == self.__ACROSS:
			wordEndMarker = cellNo + length
			endOfRowCol = self.noOfCells * rowNumber
		else:
			wordEndMarker = cellNo + (length * self.noOfCells)
			endOfRowCol = (self.noOfCells * self.noOfCells) - ((self.noOfCells * rowNumber) - cellNo)
		
		# If wordEndMarker falls outside the row/column boundry do not add "#"
		if (wordEndMarker < endOfRowCol):
			self.cellData[wordEndMarker] = "#"
	

	def printSolvedCrossword(self):
		"""Prints the formatted crossword answers to the console.
		"""
		
		if len(self.cellData) == 0:
			self.__findClueAnswers()
			
		row = ""
		hyphenRow = "\t %s" % ("-" * ((self.noOfCells * 2) + 1))
		print hyphenRow
		
		for cellNo, value in self.cellData.items():
			row = row + ' ' + value
			if cellNo % self.noOfCells == 0:
				print "\t|%s |" % row
				row = ""
		
		print hyphenRow


