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

"""ProcessCrosswordImage - This class analyzes crossword image and calculates
word length for each clue for both "across" and "down" direction.

"""

import sys
import os

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
	from PIL import Image
except ImportError:
   	sys.exit('ERROR: module "PIL" is missing. Please install it by running "pip install pillow" or "easy_install pillow".')

# Doing this to get the site-packages path.
from distutils.sysconfig import get_python_lib

# Include 'pytesser' folder in path list.
lib_folder = os.path.join(get_python_lib(), 'pytesser')
if lib_folder not in sys.path:
	sys.path.insert(0, lib_folder)

# Checking for pytesser module existence.
try:
	from pytesser import image_to_string
except ImportError:
	print 'ERROR: module "PyTesser" is missing. Follow these steps to install'
	print '\t1. Download the zip from here https://code.google.com/p/pytesser/downloads/list'
	print '\t2. Unzip the folder & paste it in your "Python2x\Lib\site-packages" folder'
	print '\t3. Rename it to pytesser'
	print '\t4. Create a blank "__init__.py" under "pytesser" folder'
	print '\t5. Edit the file "pytesser.py"'
	print '\t6. Change the line "import Image" to "from PIL import Image"'
	print '\t7. Change the line "tesseract_exe_name = "tesseract"" to "tesseract_exe_name = os.path.dirname(__file__) + \'/tesseract\'"'
	sys.exit(1)




class ProcessCrosswordImage:
	"""Analyzes crossword image and calculates word length for each clue for
		both "across" and "down" direction.
	"""
	
	def __init__(self, imgFile, numOfCells = 15):
		"""Initialize the object """
		if os.path.exists(imgFile):
			self.imgFile = imgFile
		else:
			sys.exit('ERROR: Incorrect path or filename: "%s"') % imgFile
		try:		
			self.numOfCells = int(numOfCells)
		except ValueError:
			print 'ERROR: Second parameter should be number, not a string "%s".' % numOfCells
			sys.exit(1)
		self.__crosswordDetails = OrderedDict()
		self.__wordsLengthAcross = OrderedDict()
		self.__wordsLengthDown = OrderedDict()
		self.__cellNoAndTextReference = OrderedDict()
		self.__totalClues = None
		self.__ACROSS = "Across"
		self.__DOWN = "Down"


	def __printInfo(self, show, wordType):
		"""Prints words length
		"""
		
		if show:
			if (wordType == self.__ACROSS.lower() or wordType == "both"):
				print "\n%s\tLength" % self.__ACROSS
				for c, l in (self.__wordsLengthAcross.items()):
					print "%s\t%s" % (c, l)
			
			if (wordType == self.__DOWN.lower() or wordType == "both"):
				print "\n%s\tLength" % self.__DOWN
				for c, l in (self.__wordsLengthDown.items()):
					print "%s\t%s" % (c, l)


	def __parseImage(self):
		"""Scans the image, extracts the text and calculate clue length
		"""
		
		try:
			img = Image.open(self.imgFile)
		except IOError:
			sys.exit('ERROR: "%s" is not a valid image file.' % (imgFile))
		if (img.width == img.height):
			sizeOfEachCell = img.width / self.numOfCells
		cellCount = 0		# Stores
		acrossStart = 0		# Stores the first cell number until it finds the end of the across word.
		# Increasing the image size so OCR works precisely.		
		newImgSize = 90
		
		for row in range(0, img.width, sizeOfEachCell):
			for column in range (0, self.numOfCells):
				imageDetails = {}
				cellCount += 1
				if acrossStart == 0:
					imageDetails['across'] = True
				else:
					imageDetails['across'] = False
				imageDetails['cell'] = cellCount
				imageDetails['left'] = column * sizeOfEachCell + 1 	# Adding 1 to remove border
				imageDetails['top'] = row + 1					# Adding 1 to remove border
				imageDetails['right'] = imageDetails['left'] + sizeOfEachCell - 1	# Subtracting 1 to remove border
				imageDetails['bottom'] = row + sizeOfEachCell
				if imageDetails['bottom'] >= img.width:
					break
				boxForCell = [imageDetails['left'],
							  imageDetails['top'],
							  imageDetails['right'],
							  imageDetails['bottom']]
				imgOfCell = img.crop(boxForCell)
				
				# Get no. of colors, if the list is equal to 1 then
				# the cell is filled with white or black.
				listOfColors = imgOfCell.getcolors()
				if listOfColors != None and len(listOfColors) > 1:
					number = image_to_string(imgOfCell.resize([newImgSize, newImgSize], 1)).strip()
					if number.isdigit():
						acrossStart = self.__setAcross(cellCount, row, acrossStart, imageDetails, number)
					else:
						acrossStart = self.__setAcross(cellCount, row, acrossStart, imageDetails)
				
				if listOfColors != None and len(listOfColors) == 1:
					# Condition for black cell
					if (listOfColors[0][1][0] == 0 or listOfColors[0][1][1] == 0
						or listOfColors[0][1][2] == 0):
						if acrossStart != 0:
							self.__crosswordDetails[acrossStart]['aLength'] = cellCount - self.__crosswordDetails[acrossStart]['cell']
							if acrossStart not in self.__wordsLengthAcross:
								self.__wordsLengthAcross[acrossStart] = {}
							self.__wordsLengthAcross[acrossStart]['length'] = self.__crosswordDetails[acrossStart]['aLength']
							self.__wordsLengthAcross[acrossStart]['cellno'] = self.__crosswordDetails[acrossStart]['cell']
							acrossStart = 0
						if row > 0:
							self.__setDownLength(cellCount)
					else:
						if cellCount not in self.__cellNoAndTextReference:
							self.__cellNoAndTextReference[cellCount] = ""
				# Condition if the cell is the last cell is blank or has Number 
				if (cellCount % self.numOfCells == 0) and acrossStart != 0:
					# Adding 1 when the end of the column is not black cell.
					self.__crosswordDetails[acrossStart]['aLength'] = cellCount - self.__crosswordDetails[acrossStart]['cell'] + 1
					if acrossStart not in self.__wordsLengthAcross:
						self.__wordsLengthAcross[acrossStart] = {}
					self.__wordsLengthAcross[acrossStart]['length'] = self.__crosswordDetails[acrossStart]['aLength']
					self.__wordsLengthAcross[acrossStart]['cellno'] = self.__crosswordDetails[acrossStart]['cell']
					acrossStart = 0
				
				if imageDetails['bottom'] >= img.width - 1:
					self.__setDownLength(cellCount, True)
		
		# Sorting
		self.__crosswordDetails = OrderedDict(sorted(self.__crosswordDetails.items(), key = lambda(k,v):(int(k),v)))
		self.__wordsLengthAcross = OrderedDict(sorted(self.__wordsLengthAcross.items(), key = lambda(k,v):(int(k),v)))
		self.__wordsLengthDown = OrderedDict(sorted(self.__wordsLengthDown.items(), key = lambda(k,v):(int(k),v)))


	def __setAcross(self, cellCount, row, acrossStart, imageDetails, number = 0):
		"""Sets clue starting number and determine if the same clue is also 
			down direction
		"""
		
		if number == 0:
			number = len(self.__crosswordDetails) + 1
			print 'WARNING: Unable to extract the number from cell "%s". Assigning "%s" by incrementing last scanned number' % (cellCount, number)
		self.__crosswordDetails[number] = imageDetails
		if row == 0:
			imageDetails['down'] = True
		else:
			if (cellCount - self.numOfCells) in self.__cellNoAndTextReference:
				self.__crosswordDetails[number]['down'] = False
			else:
				self.__crosswordDetails[number]['down'] = True
		if acrossStart == 0:
			acrossStart = number
		self.__cellNoAndTextReference[cellCount] = number
		
		return acrossStart
	
	
	def __setDownLength(self, cellCount, isLastRow = False):
		"""Determines end of word boundary for down clues
		"""
		
		index = 0
		for cell in range(cellCount - self.numOfCells, 0, -self.numOfCells):
			index += 1
			if cell in self.__cellNoAndTextReference:
				cellText = self.__cellNoAndTextReference[cell]
				if (cellText != "" and self.__crosswordDetails[cellText]['down'] == True):
					if index == 1:	#If length of clue is equal to 1 set the down property to false
						self.__crosswordDetails[cellText]['down'] = False
					else:
						if isLastRow:
							index += 1
						self.__crosswordDetails[cellText]['dLength'] = index
						if cellText not in self.__wordsLengthDown:
							self.__wordsLengthDown[cellText] = {}
						self.__wordsLengthDown[cellText]['length'] = self.__crosswordDetails[cellText]['dLength']
						self.__wordsLengthDown[cellText]['cellno'] = self.__crosswordDetails[cellText]['cell']
						
			else:
				break;


	def getTotalClues(self):
		"""Return the total count of across and down clues. This will treat no. 1
			down and accross as one count.
		"""
		if self.__totalClues == None:
			# Merging list by removing duplicate index
			totalClues = set(self.__wordsLengthAcross.keys()) | set(self.__wordsLengthDown.keys())
			self.__totalClues = len(totalClues)
		
		return self.__totalClues


	def getWordsLength(self, wordType = "both", show = False):
		"""Get the words length of each crossword clue. Both across and down.
		
		Args:
			wordType (Optional[str]): Value can be either "across" or "down" or none
			show (Optional[bool]): Prints the list on console.
		Returns:
			OrderedDict: Dictionary of all the words length.
		"""
		if len(self.__crosswordDetails) == 0:
			self.__parseImage()
		
		wordType= wordType.lower()
		if (wordType == "across"):
			self.__printInfo(show, wordType)
			return self.__wordsLengthAcross
		elif (wordType == "down"):
			self.__printInfo(show, wordType)
			return self.__wordsLengthDown
		else:
			self.__printInfo(show, wordType)
			return OrderedDict({"Across" : self.__wordsLengthAcross, "Down" : self.__wordsLengthDown})


	def getIndividualCellImages(self, clueNumbers = [], outputPath = "cellImages"):
		"""Extract and save the cells with number from the full image.
		
		Args:
			clueNumbers (Optional[list]): Clue No's for which the image will be extracted.
			outputPath (Optional[str]): Path where the generated image(s) should be stored.
		"""
		if len(self.__crosswordDetails) == 0:
			self.__parseImage()
		
		ext = os.path.splitext(self.imgFile)[1]
		img = Image.open(self.imgFile)
		
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		
		if type(clueNumbers) is not list:
			if type(clueNumbers) is int:
				clueNumbers = [clueNumbers]
			elif type(clueNumbers) is str and clueNumbers.isdigit():
				clueNumbers = [clueNumbers]
			else:
				sys.exit('ERROR: Wrong argument provided.')
				
		
		if len(clueNumbers) == 0:
			for k, v in (self.__crosswordDetails.items()):
				boxForCell = [self.__crosswordDetails[k]['left'],
							  self.__crosswordDetails[k]['top'],
							  self.__crosswordDetails[k]['right'],
							  self.__crosswordDetails[k]['bottom']]
				imgOfCell = img.crop(boxForCell)
				imgOfCell.save(os.path.join(outputPath, "cell_%s%s" % (self.__crosswordDetails[k]['cell'], ext)))			
		else:
			for clueNumber in (clueNumbers):
				clueNumber = str(clueNumber)
				if (clueNumber == 0 or clueNumber not in self.__crosswordDetails):
					print 'WARNING: Invalid clue number "%s". Please provide the number between 1 and %s' % (clueNumber, len(self.__crosswordDetails))
				boxForCell = [self.__crosswordDetails[clueNumber]['left'],
							  self.__crosswordDetails[clueNumber]['top'],
							  self.__crosswordDetails[clueNumber]['right'],
							  self.__crosswordDetails[clueNumber]['bottom']]
				imgOfCell = img.crop(boxForCell)
				imgOfCell.save(os.path.join(outputPath, "cell_%s%s" % (self.__crosswordDetails[clueNumber]['cell'], ext)))

