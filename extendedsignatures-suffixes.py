# Read in an LMR file:  

# This program looks for extended signatures, which are regular subgraphs among words, where the edges are
# (high-freq) Delta-Right pairs of words, and where a word may be *split differently* (without penalty!) 
# in different Delta-Right pairs: e.g., "moves" is part of the pair (move/move-s) and also of the pair
# (mov-es/mov-ing).
# 	Prototyping for bootstrapping of Lxa5
# 	Accepts name of input file as command-line argument.
##--------------------------------------------------------------------##
##		Main program begins on line 203.
##--------------------------------------------------------------------##

import os
import sys
import time

MinimumStemLength = 5
MaximumAffixLength = 2
MinimumStemCount = 5
MinimumNumberofSigUses = 15


# ---------------------------------------------------------#
def maximalcommonprefix(a, b):
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar):
        if not a[i] == b[i]:
            return a[:i]
    return a[:howfar]


# ---------------------------------------------------------#
# ---------------------------------------------------------#
def maximalcommonsuffix(a, b):
    alen = len(a)
    blen = len(b)
    howfar = alen
    if len(b) < howfar:
        howfar = len(b)
    # print "maximal common suffix",
    for i in range(0, howfar, 1):
        #		print alen, i, blen
        if not a[alen - i - 1] == b[blen - i - 1]:
            startingpoint = alen - i
            #			print a,b, i, a[alen-i:]
            return a[alen - i:]
            #	print a,b,a[alen- howfar:]
    return a[howfar:]


# ---------------------------------------------------------#
def DeltaLeft(a, b):
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar - 1, 0, -1):
        if not a[i] == b[i]:
            return (a[:i], b[:i])
    return (a[:howfar], b[:howfar])


# ---------------------------------------------------------#\
# ---------------------------------------------------------#
def DeltaRight(a, b):
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar):
        if not a[i] == b[i]:
            return (a[i:], b[i:])
    return (a[howfar:], b[howfar:])


# ---------------------------------------------------------#
def makesignature(a):
    # print "make sig", a, "len (a)", len(a)
    delimiter = '.'
    sig = ""
    for i in range(len(a) - 1):
        if len(a[i]) == 0:
            # print "i", i, "a[i]", a[i],
            sig += "NULL"
        else:
            sig += a[i]
        sig += delimiter
    sig += a[len(a) - 1]
    # print "sig", sig
    return sig


# ---------------------------------------------------------#
def makesignaturefrom2words(a, b):
    stemlength = 0
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(0, howfar, -1):
        if a[i] == b[i]:
            stemlength = i + 1
        else:
            break;
    affix1 = a[:stemlength]
    affix2 = b[:stemlength]
    if len(affix1) == 0:
        affix1 = "NULL"
    if len(affix2) == 0:
        affix2 = "NULL"
    return (affix1, affix2)


# ---------------------------------------------------------#
# ---------------------------------------------------------#
def makesignaturefrom2words_suffixes(a, b):
    stemlength = 0
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar):
        if a[i] == b[i]:
            stemlength = i + 1
        else:
            break;
    affix1 = a[stemlength:]
    affix2 = b[stemlength:]
    if len(affix1) == 0:
        affix1 = "NULL"
    if len(affix2) == 0:
        affix2 = "NULL"
    return (affix1, affix2)


# ---------------------------------------------------------#
def sortfunc(x, y):
    return cmp(x[1], y[1])


# ---------------------------------------------------------#
def sortfunc1(x, y):
    return cmp(x[1], len(y[1]))


# ---------------------------------------------------------#
def getrobustness(sig, stems):
    countofsig = len(sig)
    countofstems = len(stems)
    lettersinstems = 0
    lettersinaffixes = 0
    for stem in stems:
        lettersinstems += len(stem)
    for affix in sig:
        lettersinaffixes += len(affix)
    return lettersinstems * (countofsig - 1) + lettersinaffixes * (countofstems - 1)


# ---------------------------------------------------------#
def findmaximalrobustsuffix(wordlist, outfile):
    bestchunk = ""
    bestwidth = 0
    bestlength = 0
    bestrobustness = 0
    maximalchunksize = 3
    wordlist = sorted(wordlist)

    for size in range(1, maximalchunksize + 1):
        currentlength = 0
        here = 0
        while (here < len(wordlist) - 1):
            currentlength = 0
            chunk = wordlist[here][-1 * size:]
            # print  >>outfile, "here", here, "word here", wordlist[here], "chunk: ", chunk
            for there in range(here + 1, len(wordlist)):
                # print >>outfile, "\t", "A:", wordlist[here], wordlist[there], wordlist[there][-1*size:], chunk
                if (not wordlist[there][-1 * size:] == chunk) or (there == len(wordlist) - 1):
                    # print >>outfile, "\t\tFound difference, or else at end of list"
                    currentlength = there - here
                    currentrobustness = currentlength * size
                    if currentrobustness > bestrobustness:
                        bestrobustness = currentrobustness
                        bestchunk = chunk
                        bestwidth = size
                        bestlength = currentlength
                    # print >>outfile,  "Best chunk", bestchunk, "and best robustness", bestrobustness
                    break;
                    # else:
                    # print "OK match with ", wordlist[there]
            here = there

    return


# ---------------------------------------------------------#
def printmultilist(wordlist, depth):
    for item in wordlist:
        if type(item) == type(string()):
            print
            item
        elif type(item) == type(list()):
            printmultilist(item, depth + 1)
        print
        "end of item"
    return


# ---------------------------------------------------------#
def MakeBiSignatures_suffixes(wordlist,
                              SigToTuple):  # This function finds pairs of words which make a valid signature, and makes Dictionary whose key is the signature and whose value is a tuple: stem, word1, word2, signature.

    bisig = []  # signature with exactly two affixes
    numberofwords = len(wordlist)
    for n in range(numberofwords):
        word1 = wordlist[n]
        word1 = word1.lower()
        word1length = len(word1)
        minstem = word1[:MinimumStemLength]
        thisminstemlength = len(minstem)
        # print word1, minstem
        # if n%1000 == 0:
        # print n, word1;
        # if (word1 == "rich" and word2 == "riches"):
        if word1 == "rich":
            print
            " rich"
        if word1 == "riches":
            print
            "rich and riches"
        for m in range(n + 1, numberofwords):
            word2 = wordlist[m]
            word2length = len(word2)
            if (word1 == "rich" and word2 == "riches"):
                print
                "rich and riches"
            if not minstem == word2[:MinimumStemLength]:
                if (word1 == "rich" and word2 == "riches"):
                    print
                    "did not agree on minimum stem"
                break
            # print word1, word2
            thisstem = maximalcommonprefix(word1, word2)
            thisstemlength = len(thisstem)
            if thisstemlength < MinimumStemLength:
                continue
            suffix1length = word1length - thisstemlength
            suffix2length = word2length - thisstemlength
            if suffix1length > MaximumAffixLength or suffix2length > MaximumAffixLength:
                continue

            # print word1, word2, "common stem: ", thisstem,
            # ---------------------------------------#
            bisig[:] = []
            suffix1 = word1[thisstemlength:]
            suffix2 = word2[thisstemlength:]
            # print suffix1, suffix2
            if len(suffix1) == 0:
                suffix1 = "NULL"
            if len(suffix2) == 0:
                suffix2 = "NULL"
            bisig.append(suffix1)
            bisig.append(suffix2)
            bisig.sort()
            bisigstring = '='.join(bisig)
            # print bisigstring
            # ---------------------------------------#
            if not bisigstring in SigToTuple.keys():
                SigToTuple[bisigstring] = []
            chunk = (thisstem, word1, word2, bisigstring)
            SigToTuple[bisigstring].append(chunk)

            # ---------------------------------------#

    return SigToTuple


##--------------------------------------------------------------------##
##		Main program 
##--------------------------------------------------------------------##

language = "english"
infolder = "../../data/" + language + "/"
size = 14
extraname = ""
# infilename = infolder + language + ".dx1"
infilename = infolder + language + str(size) + "Kwords.txt"
# infilename = infolder + "browncorpus_1Kwords.txt"
# infilename = infolder + "SwahiliWordList.txt"
if len(sys.argv) > 1:
    print
    sys.argv[1]
    infilename = sys.argv[1]
if not os.path.isfile(infilename):
    print
    "Warning: ", infilename, " does not exist."
infile = open(infilename)

print
"Data file: ", infilename

# ---------------------------------------------------------#
outfolder = infolder
outfilename = outfolder + language + str(size) + "extendedsigs.txt"
outfile = open(outfilename, "w")
# ----------------------------------------------------------#
filelines = infile.readlines()
words = {}
for line in filelines:
    pieces = line.split(' ')
    word = pieces[0]
    # word = word[:-2]
    word = word.lower()
    if (len(pieces) > 1):
        words[word] = pieces[1]
    else:
        words[word] = 1

wordlist = words.keys()
wordlist.sort()
# --------------------------------------------------#

# --------------------------------------------------#
# 		Main part of program		   #
# --------------------------------------------------#
SigToTuple = {}  # key: bisig     value: ( stem, word1, word2, bisig )
numberofwords = len(wordlist)
SigToTuple = MakeBiSignatures_suffixes(wordlist, SigToTuple)

print
"Completed finding all pairs of words."

# --------------------------------------------------#
print
"Remove pairs of 2-word signatures whose overall count is low."
print
"Find sets of words using the same stem."
# --------------------------------------------------#
#    // remove excess Multisignatures, those with too few stems:
Signatures = {}
StemToWord = {}
WordToStem = {}
for sig in SigToTuple.keys():
    if len(SigToTuple[sig]) < MinimumNumberofSigUses:
        del SigToTuple[sig]
        print
        "DD too few stems"

    else:
        print
        "BB", sig
        for stem, word1, word2, bisigstring in SigToTuple[sig]:
            if not stem in StemToWord:
                StemToWord[stem] = set()
            StemToWord[stem].add(word1)
            StemToWord[stem].add(word2)
            if not word1 in WordToStem:
                WordToStem[word1] = set()
            WordToStem[word1].add(stem)
            if not word2 in WordToStem:
                WordToStem[word2] = set()
            WordToStem[word2].add(stem)
print
"Completed filtering out pairs used only a few times."

# --------------------------------------------------#
#	Make signatures, and WordToSig dictionary, and Signature dictionary-of-stem-lists
# --------------------------------------------------#
WordToSig = {}
SigToWord = {}
print
"AA"

for stem in StemToWord.keys():
    affixset = set()
    stemlength = len(stem)
    print
    "stem", stem
    for word in StemToWord[stem]:
        if word == stem:
            affixset.add("NULL")
        else:
            affixset.add(word[stemlength:])
            print
            "AA", stem, word, word[stemlength:]
    affixlist = list(affixset)
    affixlist.sort()
    thissig = "-".join(affixlist)
    if not thissig in Signatures:
        Signatures[thissig] = []
    Signatures[thissig].append(stem)
    for word in StemToWord[stem]:
        if not word in WordToSig:
            WordToSig[word] = []
        WordToSig[word].append(thissig)

# --------------------------------------------------#
SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
DisplayList = []
for sig, stemlist in SortedListOfSignatures:
    DisplayList.append((sig, len(stemlist), getrobustness(sig, stemlist)))
DisplayList.sort
print >> outfile, '{0:<35}{1:12s} {2:12s}'.format("Signature", "Stem count", "Robustness")
for sig, stemcount, robustness in DisplayList:
    print >> outfile, '{0:<35}{1:6d} {2:6d}'.format(sig, stemcount, robustness)
print >> outfile, "--------------------------------------------------------------"
# --------------------------------------------------#
# --------------------------------------------------#
print >> outfile, "\nSorted by Robustness\n"
DisplayList = sorted(DisplayList, lambda x, y: cmp(x[2], y[2]), reverse=True)
print >> outfile, '{0:<35}{1:12s} {2:12s}'.format("Signature", "Stem count", "Robustness")
for sig, stemcount, robustness in DisplayList:
    print >> outfile, '{0:<35}{1:6d} {2:6d}'.format(sig, stemcount, robustness)
print >> outfile, "--------------------------------------------------------------"
# --------------------------------------------------#
words = WordToSig.keys()
words.sort()
print >> outfile, "--------------------------------------------------------------"
print >> outfile, "Words and their signatures"
print >> outfile, "--------------------------------------------------------------"
print >> outfile, '{0:<30}{1}'.format("Word", "Signatures")
print >> outfile, "--------------------------------------------------------------\n"
for word in words:
    print >> outfile, '{0:<30}{1}'.format(word, WordToSig[word])
# --------------------------------------------------#
numberofstemsperline = 8
stemlist = []
for sig, stemcount, robustness in DisplayList:
    print >> outfile, "\n\n\n", '{0:30s} \n'.format(sig)
    n = 0
    stemlist = sorted(Signatures[sig])
    for stem in stemlist:
        n += 1
        print >> outfile, '{0:12s}'.format(stem),
        if n == numberofstemsperline:
            n = 0
            print >> outfile, "\n\t"
    findmaximalrobustsuffix(stemlist, outfile)

    stemlist
    SigToTuple = {}  # key: bisig     value: ( stem, word1, word2, bisig )
    SigToTuple = MakeBiSignatures_suffixes(stemlist, SigToTuple)
    print >> outfile, SigToTuple

# --------------------------------------------------#



# --------------------------------------------------#
print
"Deal with signatures with multiple stems."
# --------------------------------------------------#









# --------------------------------------------------#
print
"Make links between multiply-analyzed words."
# --------------------------------------------------#







# --------------------------------------------------#
#  Logging information
localtime = time.asctime(time.localtime(time.time()))
print
"Local current time :", localtime

numberofwords = len(wordlist)
logfilename = outfolder + "logfile.txt"
logfile = open(logfilename, "a")

print >> logfile, outfilename.ljust(60), '%30s wordcount: %8d data source:' % (
    localtime, numberofwords), infilename.ljust(50)

# --------------------------------------------------#
