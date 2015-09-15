# CrosswordPuzzleSolver
Scripts to solve Crossword Puzzle

**bootstrap.py:** This is the main file to be executed/run

**WebPageScraping.py:** Collect Crossword clues & Image from http://www.onlinecrosswords.net/printable-daily-crosswords-1.php. This same script is used to find the answer for each clue from http://crosswordheaven.com/search.

**ProcessCrosswordImage.py:** This has the algorithm of image processing and extracting clue no. and finding their word length

**SolveCrossword.py:** This has the algorithm for answer lookup and generating the output on console.

Command to call
```shell
python bootstrap.py
```



**Note:** This script has some 3rd party dependencies (such as PIL, pytesser (OCR) & Beautiful Soup) which you may have to download/install, if it's not already there on your system. If it's missing no worries the script will guide you on how to download/install it
