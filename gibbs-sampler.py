import math
import os
import random
import sys

g_encoding = "asci"  # "utf8"

morphemes = {}
totalmorphemecount = 0.0


# ----------------------------------------------------------#
def positionInBreaks(point, numberlist):
    for n in range(0, len(numberlist)):
        if numberlist[n] == point:
            # print "position found: ", n
            return n
        if numberlist[n] > point:
            return -1
    return -1


# ----------------------------------------------------------#
def AddIntegerToList(point, numberlist):  # expects that point is less than the last number in numberlist
    for n in range(0, len(numberlist)):
        if numberlist[n] > point:
            numberlist.insert(n, point)
            return n
    return -1


# ----------------------------------------------------------#
def GetPiece(piecenumber, word, numberlist):
    return word[numberlist[piecenumber - 1]: numberlist[piecenumber]]


# ----------------------------------------------------------#
def GetPlog(morpheme, morphemes, totalmorphemecount):
    if morpheme in morphemes:
        thiscount = morphemes[morpheme]
    else:
        thiscount = 1
    return math.log(totalmorphemecount / float(thiscount), 2)


# ----------------------------------------------------------#
def RecountMorphemes(words, breaks, morphemes):
    newmorphemes = {}
    for word in words:
        for n in range(len(breaks[word])):
            piece = word[breaks[word][n - 1]:breaks[word][n]]
            # IncrementCountAmount(piece,newmorphemes,len(piece))
            IncrementCount(piece, newmorphemes)
    return newmorphemes


# ----------------------------------------------------------#
def ComputeTotalMorphemeCount(morphemes):
    totalmorphemecount = 0
    for item in morphemes:
        totalmorphemecount += float(morphemes[item])
    return totalmorphemecount


# ----------------------------------------------------------#
def GetPieceFromLetterNumber(point, word, numberlist):
    # print "\nGetPieceFromLetter", point, word, numberlist
    for n in range(1, len(numberlist)):
        # print "get piece, n:", n,
        if point <= numberlist[n]:
            # print word[numberlist[n-1]:numberlist[n]]
            return word[numberlist[n - 1]:numberlist[n]]
    return -1


# ----------------------------------------------------------#
def GetCount(item, dictionary):
    defaultcount = 1  # 0.25 # 1
    if not item in dictionary:
        return defaultcount
    else:
        return dictionary[item]


# ----------------------------------------------------------#
def IncrementCount(item, dictionary):
    if not item in dictionary:
        dictionary[item] = 1
    else:
        dictionary[item] += 1


# ----------------------------------------------------------#
def IncrementCountAmount(item, dictionary, amount):
    if not item in dictionary:
        dictionary[item] = amount
    else:
        dictionary[item] += amount


# ----------------------------------------------------------#
def TestFunction(word, point, thiswordbreaks, outfile, totalmorphemecount):
    splitword = []
    start = 0
    for n in range(1, len(thiswordbreaks)):  # breaks[word] is a list of integers indicating morpheme breaks
        splitword.append(word[start: thiswordbreaks[n]])  # splitword is a list of the morphemes
        start = thiswordbreaks[n]
    breakpt = positionInBreaks(point, thiswordbreaks)  # returns -1 if point is not a breakpoint in this word
    if breakpt == -1:  # we will consider Splitting at this point
        OldPiece = GetPieceFromLetterNumber(point, word, thiswordbreaks)
        logfacWholeWord = math.log(math.factorial(len(thiswordbreaks)))
        logfacOldPiece = math.log(math.factorial(len(OldPiece)), 2)
        count = GetCount(OldPiece, morphemes)
        phonologicalcostOldPiece = BitsPerLetter * len(OldPiece) / count
        oldplog = GetPlog(OldPiece, morphemes, totalmorphemecount)
        oldscore = oldplog + logfacOldPiece + logfacWholeWord + phonologicalcostOldPiece

        newBreakNumber = AddIntegerToList(point, thiswordbreaks)
        logfacWholeWord2 = math.log(math.factorial(len(thiswordbreaks)))
        LeftPiece = GetPiece(newBreakNumber, word, thiswordbreaks)
        RightPiece = GetPiece(newBreakNumber + 1, word, thiswordbreaks)
        newscoreLeft = GetPlog(LeftPiece, morphemes, totalmorphemecount)
        newscoreRight = GetPlog(RightPiece, morphemes, totalmorphemecount)
        logfacLeftPiece = math.log(math.factorial(len(LeftPiece)), 2)
        logfacRightPiece = math.log(math.factorial(len(RightPiece)), 2)

        count = GetCount(LeftPiece, morphemes)
        phonologicalcostLeftPiece = BitsPerLetter * len(LeftPiece) / count
        count = GetCount(RightPiece, morphemes)
        phonologicalcostRightPiece = BitsPerLetter * len(RightPiece) / count

        newscore = newscoreLeft + newscoreRight + logfacLeftPiece + logfacRightPiece + logfacWholeWord2 + phonologicalcostLeftPiece + phonologicalcostRightPiece
        #			if newscore < oldscore:
        #				breaks[word] = thiswordbreaks
        #				totalmorphemecount += 1

        #			 	if not word in ChangingWords:
        #					ChangingWords[word] = 1
        #				else:
        #					ChangingWords[word] += 1

        #				print "Believed change occurying."

        if True:
            print >> outfile, SplitFormatString1 % (
                word, splitword, LeftPiece, RightPiece, OldPiece, oldscore, newscore, count)
            print >> outfile, SplitFormatString2 % (newscoreLeft, newscoreRight, oldplog)
            print >> outfile, SplitFormatString3 % (logfacLeftPiece, logfacRightPiece, logfacOldPiece)
            #				print >>outfile, "\tNew score:", newscore, "Ptr to left piece",  newscoreLeft,  "Ptr to right piece",  newscoreRight, "log fac Left piece", logfacLeftPiece, "log fac Right piece",   logfacRightPiece, "log fac whole word (old)", logfacWholeWord, \
            #						"\n\t", "Oldscore: ", oldscore, "log fac whole word with break", logfacWholeWord2
            # print "New score", newScore
            # ------------------------------------------------------------------------------------------------#
    else:  # we will consider removing this breakpoint
        LeftPiece = GetPiece(breakpt, word, thiswordbreaks)
        RightPiece = GetPiece(breakpt + 1, word, thiswordbreaks)
        count = GetCount(LeftPiece, morphemes)
        phonologicalcostLeftPiece = BitsPerLetter * len(LeftPiece) / count
        logfacLeftPiece = math.log(math.factorial(len(LeftPiece)), 2)
        count = GetCount(RightPiece, morphemes)
        phonologicalcostRightPiece = BitsPerLetter * len(RightPiece) / count
        logfacRightPiece = math.log(math.factorial(len(RightPiece)), 2)
        logfacWholeWord = math.log(math.factorial(len(thiswordbreaks)))
        oldscoreLeft = GetPlog(LeftPiece, morphemes, totalmorphemecount)
        oldscoreRight = GetPlog(RightPiece, morphemes, totalmorphemecount)
        oldscore = oldscoreLeft + oldscoreRight + logfacLeftPiece + logfacRightPiece + logfacWholeWord + phonologicalcostLeftPiece + phonologicalcostRightPiece

        NewPiece = LeftPiece + RightPiece
        count = GetCount(NewPiece, morphemes)
        phonologicalcostNewPiece = BitsPerLetter * len(NewPiece) / count
        logfacNewPiece = math.log(math.factorial(len(NewPiece)), 2)
        logfacWholeWordModified = math.log(math.factorial(len(thiswordbreaks) - 1), 2)

        newpiecescore = GetPlog(NewPiece, morphemes, totalmorphemecount)
        newscore = newpiecescore + logfacNewPiece + logfacWholeWordModified + phonologicalcostNewPiece

        #			if newscore  < oldscore:
        #				count = GetCount(NewPiece,morphemes)
        #				totalmorphemecount += -1
        #				breaks[word].remove(point)
        #
        #			 	if not word in ChangingWords:
        #					ChangingWords[word] = 1
        #				else:
        #					ChangingWords[word] += 1

        if True:
            print >> outfile, MergeFormatString1 % (
                word, splitword, LeftPiece, RightPiece, NewPiece, oldscore, newscore, count)
            print >> outfile, MergeFormatString2 % (oldscoreLeft, oldscoreRight, newpiecescore)
            print >> outfile, MergeFormatString3 % (logfacLeftPiece, logfacRightPiece, logfacNewPiece)


# ------------------------------------------------------------------------------------------------#

# ----------------------------------------------------------#
def ShiftBreak(word, thiswordbreaks, shiftamount, outfile, totalmorphemecount):
    ShiftFormatString1 = "\nShifting.   %20s %35s %12s %12s %12s  %12s -    Old score %7.1f newscore: %5.1f "
    ShiftFormatString2 = "                                                                      plog: %5.1f        %5.1f        %5.1f	    %5.1f"
    ShiftFormatString3 = "                                                             log factorial: %5.1f        %5.1f        %5.1f         %5.1f"
    splitword = []
    newwordbreaks = []
    start = 0

    # pick a break point and shift it.
    breakindex = random.randrange(1, len(thiswordbreaks) - 1)
    if shiftamount > 0:
        if thiswordbreaks[breakindex + 1] <= thiswordbreaks[
            breakindex] + shiftamount:  # this means the next breakpoint is too close to consider this shift
            return (False, thiswordbreaks);
    if shiftamount < 0:
        if thiswordbreaks[breakindex - 1] >= thiswordbreaks[
            breakindex] - shiftamount:  # this means the next breakpoint is too close to consider this shift
            return (False, thiswordbreaks);

    for n in range(1, len(thiswordbreaks)):  # breaks[word] is a list of integers indicating morpheme breaks
        splitword.append(word[start: thiswordbreaks[n]])  # splitword is a list of the morphemes
        start = thiswordbreaks[n]

    OldLeftPiece = GetPiece(breakindex, word, thiswordbreaks)
    OldRightPiece = GetPiece(breakindex + 1, word, thiswordbreaks)
    count = GetCount(OldLeftPiece, morphemes)
    phonologicalcostOldLeftPiece = BitsPerLetter * len(OldLeftPiece) / count
    logfacOldLeftPiece = math.log(math.factorial(len(OldLeftPiece)), 2)
    count = GetCount(OldRightPiece, morphemes)
    phonologicalcostOldRightPiece = BitsPerLetter * len(OldRightPiece) / count
    logfacOldRightPiece = math.log(math.factorial(len(OldRightPiece)), 2)

    oldscoreLeft = GetPlog(OldLeftPiece, morphemes, totalmorphemecount)
    oldscoreRight = GetPlog(OldRightPiece, morphemes, totalmorphemecount)
    oldscore = oldscoreLeft + oldscoreRight + logfacOldLeftPiece + logfacOldRightPiece + phonologicalcostOldLeftPiece + phonologicalcostOldRightPiece

    newwordbreaks = thiswordbreaks[:]
    newwordbreaks[breakindex] += shiftamount

    NewLeftPiece = GetPiece(breakindex, word, newwordbreaks)
    count = GetCount(NewLeftPiece, morphemes)
    phonologicalcostNewLeftPiece = BitsPerLetter * len(NewLeftPiece) / count
    logfacNewLeftPiece = math.log(math.factorial(len(NewLeftPiece)), 2)

    NewRightPiece = GetPiece(breakindex + 1, word, newwordbreaks)
    count = GetCount(NewRightPiece, morphemes)
    phonologicalcostNewRightPiece = BitsPerLetter * len(NewRightPiece) / count
    logfacNewRightPiece = math.log(math.factorial(len(NewRightPiece)), 2)

    newscoreLeft = GetPlog(NewLeftPiece, morphemes, totalmorphemecount)
    newscoreRight = GetPlog(NewRightPiece, morphemes, totalmorphemecount)
    newscore = newscoreLeft + newscoreRight + logfacNewLeftPiece + logfacNewRightPiece + phonologicalcostNewLeftPiece + phonologicalcostNewRightPiece

    if newscore < oldscore:
        #		print >>outfile, ShiftFormatString1 % (word, splitword, OldLeftPiece, OldRightPiece, NewLeftPiece, NewRightPiece, oldscore, newscore )
        #		print >>outfile, ShiftFormatString2 %(  oldscoreLeft , oldscoreRight, newscoreLeft, newscoreRight)
        #		print >>outfile, ShiftFormatString3 %(  logfacOldLeftPiece , logfacOldRightPiece, logfacNewLeftPiece, logfacNewRightPiece)
        return (True, newwordbreaks)
    return (False, thiswordbreaks)


# ------------------------------------------------------------------------------------------------#




# --------------------------------------------------------------------##
#		Main program 
# --------------------------------------------------------------------##


language = "english"
infolder = '../../data/' + language + '/'

size = 50  # french 153 10 english 14 46

infilename = infolder + language + "_" + str(size) + "Kwords" + ".txt"

if len(sys.argv) > 1:
    print
    sys.argv[1]
    infilename = sys.argv[1]
if not os.path.isfile(infilename):
    print
    "Warning: ", infilename, " does not exist."
if g_encoding == "utf8":
    infile = codecs.open(infilename, encoding='utf-8')
else:
    infile = open(infilename)

print
"Data file: ", infilename

# ---------------------------------------------------------#

outfolder = infolder
outfilename = outfolder + language + "_" + str(size) + "Kwords" + "_gibbspieces.txt"
if g_encoding == "utf8":
    outfile = codecs.open(outfilename, encoding="utf-8", mode='w', )
    print
    "yes utf8"
else:
    outfile = open(outfilename, mode='w')
outfile = open(outfilename, "w")

# ----------------------------------------------------------#

filelines = infile.readlines()
WordCounts = {}

for line in filelines:
    pieces = line.split(' ')
    word = pieces[0]
    #	word = word[:-1] # for french only?
    word = word.lower()
    #	if (len(pieces)>1):
    #		WordCounts[word] = int( pieces[1] )
    #	else:
    #		WordCounts[word]=1
    WordCounts[word] = 1

wordlist = WordCounts.keys()
wordlist.sort()

# ----------------------------------------------------------#
breakprob = 0.1
breaks = {}
totalmorphemecount = 0
for word in wordlist:
    start = 0
    breaks[word] = []
    breaks[word].append(0)
    for n in range(1, len(word)):
        if random.random() < breakprob:
            piece = word[start:n]
            breaks[word].append(n)
            start = n
            # IncrementCountAmount(piece,morphemes,len(piece))
            IncrementCount(piece, morphemes)
            totalmorphemecount += 1  # len(piece)
    if start < len(word):
        piece = word[start:]
        breaks[word].append(len(word))
        # IncrementCountAmount(piece,morphemes,len(piece))
        IncrementCount(piece, morphemes)
        totalmorphemecount += 1  # len(piece)

pieces = sorted(morphemes, key=morphemes.get, reverse=True)  # sort by value
for piece in pieces:
    if morphemes[piece] < 10:
        continue
        # print piece, morphemes[piece]
        # print >>outfile, piece, morphemes[piece]


        # ----------------------------------------------------------#
print >> outfile, "Dictionary"
morphemes = {}
for word in wordlist:
    # print "\n", "Dict:",  word, breaks[word]
    for n in range(1, len(breaks[word])):
        piece = word[breaks[word][n - 1]:breaks[word][n]]
        IncrementCount(piece, morphemes)

pieces = sorted(morphemes, key=morphemes.get, reverse=True)  # sort by value
for piece in pieces:
    if morphemes[piece] < 5:
        continue
    print >> outfile, piece, morphemes[piece]

# ----------------------------------------------------------#

BestMorphemes = {}
BitsPerLetter = 1
logflag = False
SplitFormatString1 = "\nSplitting. %20s %35s %12s %12s %12s -    Old score %7.1f newscore: %5.1f count: %3d"
SplitFormatString2 = "                                                                     plog: %5.1f        %5.1f        %5.1f"
SplitFormatString3 = "                                                            log factorial: %5.1f        %5.1f        %5.1f"
MergeFormatString1 = "\nMerging.   %20s %35s %12s %12s %12s -    Old score %7.1f newscore: %5.1f count: %3d"
MergeFormatString2 = "                                                                     plog: %5.1f        %5.1f        %5.1f"
MergeFormatString3 = "                                                            log factorial: %5.1f        %5.1f        %5.1f"
for loopno in range(201):
    splitsduringthisloop = 0
    mergesduringthisloop = 0
    shiftsduringthisloop = 0
    for word in wordlist:
        thiswordbreaks = breaks[word][:]
        if len(word) < 2:
            continue
        splitword = []
        start = 0
        for n in range(1, len(thiswordbreaks)):  # breaks[word] is a list of integers indicating morpheme breaks
            splitword.append(word[start: thiswordbreaks[n]])  # splitword is a list of the morphemes
            start = thiswordbreaks[n]

        point = random.randrange(1, len(word))

        breakpt = positionInBreaks(point, thiswordbreaks)  # returns -1 if point is not a breakpoint in this word
        if breakpt == -1:  # we will consider Splitting at this point
            OldPiece = GetPieceFromLetterNumber(point, word, thiswordbreaks)
            count = GetCount(OldPiece, morphemes)
            logfacWholeWord = math.log(math.factorial(len(thiswordbreaks)))
            logfacOldPiece = math.log(math.factorial(len(OldPiece)), 2) / count
            phonologicalcostOldPiece = BitsPerLetter * len(OldPiece) / count
            oldplog = GetPlog(OldPiece, morphemes, totalmorphemecount)
            oldscore = oldplog + logfacOldPiece + logfacWholeWord + phonologicalcostOldPiece

            newBreakNumber = AddIntegerToList(point, thiswordbreaks)
            logfacWholeWord2 = math.log(math.factorial(len(thiswordbreaks)))
            LeftPiece = GetPiece(newBreakNumber, word, thiswordbreaks)
            RightPiece = GetPiece(newBreakNumber + 1, word, thiswordbreaks)
            newscoreLeft = GetPlog(LeftPiece, morphemes, totalmorphemecount)
            newscoreRight = GetPlog(RightPiece, morphemes, totalmorphemecount)

            countLeftPiece = GetCount(LeftPiece, morphemes)
            phonologicalcostLeftPiece = BitsPerLetter * len(LeftPiece) / countLeftPiece
            countRightPiece = GetCount(RightPiece, morphemes)
            phonologicalcostRightPiece = BitsPerLetter * len(RightPiece) / countRightPiece
            logfacLeftPiece = math.log(math.factorial(len(LeftPiece)), 2) / countLeftPiece
            logfacRightPiece = math.log(math.factorial(len(RightPiece)), 2) / countRightPiece

            newscore = newscoreLeft + newscoreRight + logfacLeftPiece + logfacRightPiece + logfacWholeWord2 + phonologicalcostLeftPiece + phonologicalcostRightPiece

            if newscore < oldscore:
                breaks[word] = thiswordbreaks
                totalmorphemecount += 1
                splitsduringthisloop += 1

            if newscore < oldscore and logflag:
                print >> outfile, SplitFormatString1 % (
                    word, splitword, LeftPiece, RightPiece, OldPiece, oldscore, newscore, count)
                print >> outfile, SplitFormatString2 % (newscoreLeft, newscoreRight, oldplog)
                print >> outfile, SplitFormatString3 % (logfacLeftPiece, logfacRightPiece, logfacOldPiece)
                #				print >>outfile, "log fac whole word (old)", logfacWholeWord, "log fac whole word with break", logfacWholeWord2

                # ------------------------------------------------------------------------------------------------#
        else:  # we will consider removing this breakpoint
            LeftPiece = GetPiece(breakpt, word, thiswordbreaks)
            RightPiece = GetPiece(breakpt + 1, word, thiswordbreaks)
            countLeftPiece = GetCount(LeftPiece, morphemes)
            phonologicalcostLeftPiece = BitsPerLetter * len(LeftPiece) / countLeftPiece
            logfacLeftPiece = math.log(math.factorial(len(LeftPiece)), 2) / countLeftPiece
            countRightPiece = GetCount(RightPiece, morphemes)
            phonologicalcostRightPiece = BitsPerLetter * len(RightPiece) / countRightPiece
            logfacRightPiece = math.log(math.factorial(len(RightPiece)), 2) / countRightPiece
            logfacWholeWord = math.log(math.factorial(len(thiswordbreaks)))
            oldscoreLeft = GetPlog(LeftPiece, morphemes, totalmorphemecount)
            oldscoreRight = GetPlog(RightPiece, morphemes, totalmorphemecount)
            oldscore = oldscoreLeft + oldscoreRight + logfacLeftPiece + logfacRightPiece + logfacWholeWord + phonologicalcostLeftPiece + phonologicalcostRightPiece

            NewPiece = LeftPiece + RightPiece
            countNewPiece = GetCount(NewPiece, morphemes)
            phonologicalcostNewPiece = BitsPerLetter * len(NewPiece) / countNewPiece
            logfacNewPiece = math.log(math.factorial(len(NewPiece)), 2) / countNewPiece
            logfacWholeWordModified = math.log(math.factorial(len(thiswordbreaks) - 1), 2)
            newpiecescore = GetPlog(NewPiece, morphemes, totalmorphemecount)
            newscore = newpiecescore + logfacNewPiece + logfacWholeWordModified + phonologicalcostNewPiece

            if newscore < oldscore:
                count = GetCount(NewPiece, morphemes)
                totalmorphemecount += -1
                breaks[word].remove(point)
                mergesduringthisloop += 1
            if newscore < oldscore and logflag:
                print >> outfile, MergeFormatString1 % (
                    word, splitword, LeftPiece, RightPiece, NewPiece, oldscore, newscore, count)
                print >> outfile, MergeFormatString2 % (oldscoreLeft, oldscoreRight, newpiecescore)
                print >> outfile, MergeFormatString3 % (logfacLeftPiece, logfacRightPiece, logfacNewPiece)
                # else:
                #	#print "Not merging: new score is not better." , LeftPiece, RightPiece, NewPiece, oldscore, newscore, count

                # shiftamount = 1
                # (flag, wordbreaks) =ShiftBreak (word, thiswordbreaks, shiftamount, outfile, totalmorphemecount)
                # if flag == True:
                #	breaks[word] = wordbreaks
                #	shiftsduringthisloop += 1

    if splitsduringthisloop + mergesduringthisloop > 1:
        print >> outfile, loopno, "Splits during this loop:", splitsduringthisloop, "Merges: ", mergesduringthisloop, "Shifts: ", shiftsduringthisloop
        print
        loopno, "Splits during this loop:", splitsduringthisloop, "Merges: ", mergesduringthisloop, "Shifts: ", shiftsduringthisloop
    morphemes = RecountMorphemes(wordlist, breaks, morphemes)
    totalmorphemecount = ComputeTotalMorphemeCount(morphemes)

    if loopno == 0 or loopno == 10 or loopno == 100 or loopno == 200:
        morphemes = {}
        for word in wordlist:
            for n in range(1, len(breaks[word])):
                piece = word[breaks[word][n - 1]:breaks[word][n]]
                IncrementCount(piece, morphemes)
        print >> outfile, "----------------------------------------\nLoop number:", loopno, "\n"
        pieces = sorted(morphemes, key=morphemes.get, reverse=True)  # sort by value

        for n in range(100):
            morph = pieces[n]
            print >> outfile, n, morph, morphemes[morph]
            if not morph in BestMorphemes:
                BestMorphemes[morph] = []
            BestMorphemes[morph].append((loopno, morphemes[morph]))

for morph in BestMorphemes.keys():
    print >> outfile, morph, BestMorphemes[morph]

# ----------------------------------------------------------#


# ----------------------------------------------------------#
print >> outfile, "Dictionary"
morphemes = {}
for word in wordlist:
    for n in range(1, len(breaks[word])):
        piece = word[breaks[word][n - 1]:breaks[word][n]]
        IncrementCount(piece, morphemes)
print >> outfile, "----------------------------------------\n"
pieces = sorted(morphemes, key=morphemes.get, reverse=True)  # sort by value
for piece in pieces:
    if morphemes[piece] < 5:
        continue
    print >> outfile, piece, morphemes[piece]

print >> outfile, "----------------------------------------\n"
print >> outfile, "Word List \n"
print >> outfile, "----------------------------------------\n"
for word in wordlist:
    print >> outfile
    for n in breaks[word]:
        if n == 0:
            previous = n
            continue
        print >> outfile, word[previous: n],
        previous = n
