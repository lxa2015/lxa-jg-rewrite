# Read in an LMR file:  

# This program looks for extended signatures, which are regular subgraphs among words, where the edges are
# (high-freq) Delta-Right pairs of words, and where a word may be *split differently* (without penalty!) 
# in different Delta-Right pairs: e.g., "moves" is part of the pair (move/move-s) and also of the pair
# (mov-es/mov-ing).
# 	Prototyping for bootstrapping of Lxa5
# 	Accepts name of input file as command-line argument.
##--------------------------------------------------------------------##
##		Main program begins on line 76. 
##--------------------------------------------------------------------##

import os
import sys
import time

MinimumStemLength = 3
MaximumAffixLength = 4
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


##--------------------------------------------------------------------##
##		Main program 
##--------------------------------------------------------------------##

language = "french"
infolder = "../../data/" + language + "/"
size = 48
extraname = ""
infilename = infolder + language + ".dx1"
# infilename = infolder + language + str(size) + "Kwords.txt"
# infilename = infolder + "browncorpus_1Kwords.txt"

if len(sys.argv) > 1:
    print
    sys.argv[1]
    infilename = sys.argv[1]
if not os.path.isfile(infilename):
    print
    "Warning: ", infilename, " does not exist."
infile = open(infilename)

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
    if (len(pieces) > 1):
        words[word] = pieces[1]
    else:
        words[word] = 1
# --------------------------------------------------#
Signatures = {}
# RegularSignatures 	= {}
WordToSig = {}
SigToWord = {}
StemToWord = {}
WordToStem = {}
bisig = []  # signature with exactly two affixes
wordlist = words.keys()
wordlist.sort()
# WordPairs		= []
SigToTuple = {}  # key: bisig     value: ( stem, word1, word2, bisig )
numberofwords = len(wordlist)

for n in range(numberofwords):
    word1 = wordlist[n]
    word1length = len(word1)
    minstem = word1[:MinimumStemLength]
    thisminstemlength = len(minstem)
    if n % 1000 == 0:
        print
        n, word1;
    for m in range(n + 1, numberofwords):
        word2 = wordlist[m]
        word2length = len(word2)
        wenttoofar = False
        if not word1[:thisminstemlength] == word2[:thisminstemlength]:
            break
        thisstem = maximalcommonprefix(word1, word2)
        thisstemlength = len(thisstem)
        if thisstemlength < MinimumStemLength:
            continue
        suffix1length = word1length - thisstemlength
        suffix2length = word2length - thisstemlength
        if suffix1length > MaximumAffixLength or suffix2length > MaximumAffixLength:
            continue

        # ---------------------------------------#
        bisig[:] = []
        suffix1 = word1[thisstemlength:]
        suffix2 = word2[thisstemlength:]
        if len(suffix1) == 0:
            suffix1 = "NULL"
        if len(suffix2) == 0:
            suffix2 = "NULL"
        bisig.append(suffix1)
        bisig.append(suffix2)
        bisig.sort()
        bisigstring = '='.join(bisig)

        # ---------------------------------------#
        if not bisigstring in SigToTuple.keys():
            SigToTuple[bisigstring] = []
        chunk = (thisstem, word1, word2, bisigstring)
        SigToTuple[bisigstring].append(chunk)

        # ---------------------------------------#

print
"Completed finding all pairs of words."

# --------------------------------------------------#
print
"Remove pairs of 2-word signatures whose overall count is low."
# --------------------------------------------------#
# --------------------------------------------------#
print
"Find sets of words using the same stem."
# --------------------------------------------------#
#    // remove excess Multisignatures, those with too few stems:
for sig in SigToTuple.keys():
    if len(SigToTuple[sig]) < MinimumNumberofSigUses:
        del SigToTuple[sig]

    else:
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

for stem in StemToWord.keys():
    affixset = set()
    stemlength = len(stem)
    for word in StemToWord[stem]:
        if word == stem:
            affixset.add("NULL")
        else:
            affixset.add(word[stemlength:])
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
print >> outfile, '{0:<35}{1:12s} {2:12s}'.format("Signature", "Stem count", "Robustness")
for sig, stemlist in SortedListOfSignatures:
    print >> outfile, '{0:<35}{stemcount:6d} {robustness:6d}'.format(sig, stemcount=len(stemlist),
                                                                     robustness=getrobustness(sig, stemlist))
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
