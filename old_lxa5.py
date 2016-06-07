# -*- coding: <utf-16> -*- 
unicode = True

# Read in an LMR file:

# This program looks for extended signatures, which are regular subgraphs among words, where the edges are
# (high-freq) Delta-Right pairs of words, and where a word may be *split differently* (without penalty!) 
# in different Delta-Right pairs: e.g., "moves" is part of the pair (move/move-s) and also of the pair
# (mov-es/mov-ing).
# 	Prototyping for bootstrapping of Lxa5
# 	Accepts name of input file as command-line argument.
# --------------------------------------------------------------------##
#		Main program begins on line 305
# --------------------------------------------------------------------##

from lxa_module import *

g_encoding = "asci"  # "utf8"
# g_encoding = "utf8"

MinimumStemLength = 5
MaximumAffixLength = 3
MinimumNumberofSigUses = 10

# Signatures is a map: its keys are signatures.  Its values are *sets* of stems.
# StemToWord is a map; its keys are stems.       Its values are *sets* of words.
# StemToSig  is a map; its keys are stems.       Its values are individual signatures.
# WordToSig  is a Map. its keys are words.       Its values are *lists* of signatures.
# StemCounts is a map. Its keys are words. 	 Its values are corpus counts of stems.



language = "french"
language = "english"
# language = "turkish"
language = "swahili"

suffix_languages = ["english", "french", "hungarian", "turkish"]
prefix_languages = ["swahili"]

if language in suffix_languages:
    side = "suffixal"
    FindSuffixesFlag = True

if language in prefix_languages:
    side = "prefixal"
    FindSuffixesFlag = False

size = 47  # french 153 10 english 10 46 swahili 47

if language == "english":
    smallfilename = "encarta"
    side = "suffixal"
    g_encoding = "ascii"
    size = 80

if language == "french":
    smallfilename = "french_dickens"
    side = "suffixal"
    size = 40
    g_encoding == "utf8"

if language == "hungarian":
    smallfilename = "hungarian"
    side = "suffixal"

if language == "swahili":
    smallfilename = "bible"
    side = "prefixal"

if language == "turkish":
    smallfilename = "turkish"
    side = "suffixal"

infolder = '../../data/' + language + '/'
infilename = infolder + smallfilename + "_" + str(size) + "Kwords" + ".txt"

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
# ------------------- New -----------------------------------------------------------------------------------
filename = language + "_" + str(size) + "Kwords_" + side + "_extendedsigs"
outfilename = decorateFilenameWithIteration(filename, outfolder, ".txt")

if g_encoding == "utf8":
    outfile = codecs.open(outfilename, encoding="utf-8", mode='w', )
    print
    "yes utf8"
else:
    outfile = open(outfilename, mode='w')
outfile = open(outfilename, "w")

outfilename = language + "_" + str(size) + "Kwords_" + side + "sigtransforms"
outfileSigTransformsname = decorateFilenameWithIteration(outfilename, outfolder, ".txt")
# ------------------- end of New -----------------------------------------------------------------------------------
# outfileSigTransforms = open(outfileSigTransformsname, "w" )
# ----------------------------------------------------------#

filelines = infile.readlines()
WordCounts = {}

for line in filelines:
    pieces = line.split(' ')
    word = pieces[0]
    if word == '#':
        continue
    word = word.lower()
    if (len(pieces) > 1):
        WordCounts[word] = int(pieces[1])
    else:
        WordCounts[word] = 1

wordlist = WordCounts.keys()
wordlist.sort()
# -------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------#
# 					Main part of program		   			   	#
# -------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------#

SigToTuple = {}  # key: bisig     value: ( stem, word1, word2, bisig )
Signatures = {}
WordToSig = {}
StemToWord = {}
StemCounts = {}
StemToSig = {}
numberofwords = len(wordlist)

# --------------------------------------------------#
# 		Read files					   			   #
# --------------------------------------------------#

stemfilename = infolder + language + "_" + str(size) + "Kwords_" + side + "_stems" + ".txt"
StemFileExistsFlag = False
if os.path.isfile(stemfilename):
    print
    "stem file is named: ", stemfilename
    print
    "stem file found"
    StemFileExistsFlag = True
    stemfile = open(stemfilename)
    filelines = stemfile.readlines()
    for line in filelines:
        pieces = line.split()
        stem = pieces[0]
        StemCounts[stem] = 1  # pieces[1]
        StemToWord[stem] = set()
        for i in range(2, len(pieces)):
            word = pieces[i]
            # if not FindSuffixesFlag:
            #	word = word[::-1]
            StemToWord[stem].add(word)
else:
    print
    "stem file not found"
    SigToTuple = MakeBiSignatures(wordlist, SigToTuple, FindSuffixesFlag)
    for sig in SigToTuple.keys():
        if len(SigToTuple[sig]) < MinimumNumberofSigUses:
            del SigToTuple[sig]
        else:
            for stem, word1, word2, bisigstring in SigToTuple[sig]:
                if not stem in StemToWord:
                    StemToWord[stem] = set()
                StemToWord[stem].add(word1)
                StemToWord[stem].add(word2)
    print
    "Completed filtering out pairs used only a few times."

for stem in StemToWord:
    StemCounts[stem] = 0
    for word in StemToWord[stem]:
        StemCounts[stem] += WordCounts[word]

if (not StemFileExistsFlag):  # we use this to create a one-time list of stems with their words
    if g_encoding == "utf8":
        outfile2 = codecs.open(stemfilename, encoding="utf-8", mode="w")
    else:
        outfile2 = open(stemfilename, "w")

    for stem in StemToWord.keys():
        print >> outfile2, stem, StemCounts[stem],
        for word in StemToWord[stem]:
            print >> outfile2, word,
        print >> outfile2

# -----------------------------------------------------------------------------------------------------------------#
#	1. Make signatures, and WordToSig dictionary, and Signature dictionary-of-stem-lists, and StemToSig dictionary
# -----------------------------------------------------------------------------------------------------------------#
print
"1. Make signatures 1"

# ---------------------------------------------------------------------------------#
#	1a. Declare a linguistica-style FSA
# ---------------------------------------------------------------------------------#

morphology = FSA_lxa()

# ---------------------------------------------------------------------------------#
#	1b. Find signatures, and put them in the FSA also.
# ---------------------------------------------------------------------------------#

StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures_1(StemToWord, StemToSig, FindSuffixesFlag, morphology,
                                                                outfile)

# ---------------------------------------------------------------------------------#
#	1c. Print the FSA to file.
# ---------------------------------------------------------------------------------#

morphology.printFSA(outfile)

print >> outfile, "_________________ \n End of Make Signatures."

# -----------------------------------------------------------------------------------------------------------------#
#	2. Compare signatures to see which can be collapsed
# -----------------------------------------------------------------------------------------------------------------#

StemCountThreshold = 15
outputtemplate = "%25s  %25s  %5d %35s %35s"
SigPairList = []
MaxNumberOfSimilarSignatures = 3
if False:
    print
    "2a. Calculating signature differences"
    print >> outfile, "\n\n*** 2a. Signature differences \n"
    for m in range(len(Signatures) - 1):
        sig1 = Signatures.keys()[m]
        if len(Signatures[sig1]) < StemCountThreshold:
            continue
        ListOfSigComparisons = []
        for n in range(m, len(Signatures) - 1):
            sig2 = Signatures.keys()[n]
            if len(Signatures[sig2]) < StemCountThreshold:
                continue
            siglist1 = sig1.split('-')
            siglist2 = sig2.split('-')
            if not len(siglist1) == len(siglist2):
                continue
            if sig1 == sig2:
                continue
            (diff, alignedlist1, alignedlist2) = SignatureDifference(sig1, sig2, outfile)
            if diff > 0:
                ListOfSigComparisons.append((diff, sig1, sig2, alignedlist1, alignedlist2))
        ListOfSigComparisons.sort(key=lambda stuff: stuff[0], reverse=True)
        for i in range(len(ListOfSigComparisons)):
            if i == MaxNumberOfSimilarSignatures:
                break
            (diff, sig1, sig2, alignedlist1, alignedlist2) = ListOfSigComparisons[i]
            # print >>outfile, outputtemplate %(sig1, sig2, diff, alignedlist1, alignedlist2)
            SigPairList.append((sig1, sig2, diff, alignedlist1, alignedlist2))

    SigPairList.sort(key=lambda quintuple: quintuple[2], reverse=True)
    for quintuple in SigPairList:
        print >> outfile, "---------------------------------------------------------------------------------------------"
        print >> outfile, outputtemplate % (quintuple[0], quintuple[1], quintuple[2], quintuple[3], quintuple[4])
        basictableau1 = intrasignaturetable()
        # print >>outfile, quintuple[3], listToSignature(quintuple[3])
        basictableau1.setsignature(listToSignature(quintuple[3]))
        basictableau1.displaytofile(outfile)
        basictableau2 = intrasignaturetable()
        basictableau2.setsignature(listToSignature(quintuple[4]))
        basictableau2.displaytofile(outfile)
        basictableau1.minus_aligned(basictableau2, side)
        print >> outfile, basictableau1.displaytolist_aligned(outfile)

    print
    "2b.  End of Calculating signature differences"

# -----------------------------------------------------------------------------------------------------------------#
#	3. Find larger groupings of signatures
# -----------------------------------------------------------------------------------------------------------------#
# 1. Sort signatures by robustness. Scan through them in decreasing robustness order.
#	Associate with each signature any subsignature that is lower than it in the list.

if False:
    print >> outfile, "\n\n  *** 3a. Find larger groupings of signatures \n\n"
    print
    "3a. Find larger groupings of signatures"
    SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
    SortedList = []
    for sig in Signatures.keys():
        SortedList.append((sig, getrobustness(sig, Signatures[sig])))
    SortedList = sorted(SortedList, lambda x, y: cmp(x[1], y[1]), reverse=True)

    RemainingSignatures = Signatures
    Subsignatures = {}
    Satellites = {}
    topsetcount = 10
    for n in range(topsetcount):
        topsig = SortedList[n][0]
        topsigset = set(topsig.split('-'))
        for m in range(n + 1, len(SortedList)):
            lowsig = SortedList[m][0]
            # print topsig, lowsig
            if not lowsig in RemainingSignatures:
                continue
            if subsignature(lowsig, topsig):
                if not topsig in Subsignatures:
                    Subsignatures[topsig] = []
                Subsignatures[topsig].append(lowsig)
        if topsig in Subsignatures:
            print >> outfile, "\nSubsignatures", topsig, Subsignatures[topsig]

        if False:
            for m in range(n + 1, len(SortedList)):
                lowsig = SortedList[m][0]
                lowsigset = set(lowsig.split('-'))
                if len(lowsigset) == len(topsigset) + 1 and topsigset <= lowsigset:
                    moon = lowsigset ^ topsigset
                    if not topsig in Satellites:
                        Satellites[topsig] = []
                    Satellites[topsig].append((moon.pop(), len(Signatures[lowsig])))
            if topsig in Satellites:
                print >> outfile, "\nSatellites", topsig, Satellites[topsig]
    print >> outfile, "\n\n  *** 3b. End of finding larger groupings of signatures \n\n"
    print
    "3b. End of finding larger groupings of signatures."

# ---------------------------------------------------------------------------------------------------------------------------------#
# 4. Check with each set of stems (each signature) if they all end with the same letter (or n-gram). If they
#  do, we shift at least one letter to the suffix. In short, shifting to the right.
# --------------------------------------------------------------------------------------------------------------------------------#
sizethreshold = 5
exceptionthreshold = 15
proportionthreshold = .9
proportion = 0.000
MaximalLettersToShift = 0
outputtemplate = "%25s %25s %3s  %5f  "

print
"4. Check with each stem of a sig if they all end with the same gram."
print >> outfile, "\n\n*** 4. Check with each stem of a sig if they all end with the same gram. Shift one letter from end of stems.\n"

for loopno in range(MaximalLettersToShift):
    print >> outfile, "*** Loop number in letter shift: ", loopno + 1
    for sig in Signatures.keys():
        stemlist = sorted(Signatures[sig])
        if len(stemlist) < sizethreshold:
            continue
        (CommonLastLetter, ExceptionCount, proportion) = TestForCommonSuffix(stemlist, outfile, FindSuffixesFlag)
        if ExceptionCount <= exceptionthreshold and proportion >= proportionthreshold:
            StemToWord, newsig = ShiftFinalLetter(StemToWord, StemCounts, stemlist, CommonLastLetter, sig,
                                                  FindSuffixesFlag, outfile)
            print >> outfile, outputtemplate % (sig, newsig, CommonLastLetter, proportion)
    NoLengthLimitFlag = True
    StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord, StemToSig, FindSuffixesFlag, outfile,
                                                                  NoLengthLimitFlag)
print >> outfile, "\n\n*** 4. End of shifting one letter from end of stems"
print
"4. End of shifting one letter from end of stems"

# printSignatures(Signatures, WordToSig, StemCounts, outfile, g_encoding, FindSuffixesFlag)

# morphology.shiftLettersToRight(sizethreshold, exceptionthreshold, proportionthreshold, proportion, MaximalLettersToShift,outfile, FindSuffixesFlag)







# -------------------------------------------------------------------------------------------------------------------------------------#
# 5. Look to see which signatures could be improved, and score the improvement quantitatively with robustness.
# Then we improve the one whose robustness increase is the greatest.
# -------------------------------------------------------------------------------------------------------------------------------------#
NumberOfCorrections = 100
print >> outfile, "***"
print >> outfile, "*** 5. Finding robust suffixes in stem sets\n\n"
print
"5a. Finding robust suffixes in stem sets"

# ---------------------------------------------------------------------------------#
#	5a. Loop: how many times? NumberOfCorrections
# ---------------------------------------------------------------------------------#

for loopno in range(NumberOfCorrections):
    # -------------------------------------------------------------------------#
    #	5b. For each edge, find best peripheral piece that might be
    #           a separate morpheme.
    # -------------------------------------------------------------------------#
    morphology.find_highest_weight_affix_in_an_edge(outfile, FindSuffixesFlag)

# ---------------------------------------------------------------------------------#
#	5c. Print graphics based on each state.
# ---------------------------------------------------------------------------------#

for state in morphology.States:
    graph = morphology.createPySubgraph(state)
    # thingsprint "S", state.index,
    if len(graph.edges()) < 2:
        continue
    # if len(graph.edges()) > 300:
    #	print "Not graphing:", state.index
    #	continue

    # print "\n***" , state.index, " out of " , len (morphology.States)

    graph.layout(prog='dot')
    filename = infolder + 'morphology' + str(state.index) + '.png'
    graph.draw(filename)
# print filename,

print >> outfile, " ---------------------- \n 5b: \n\n"

commonEdgePairs, EdgeToEdgeDict = morphology.findCommonStems()
for x in commonEdgePairs:
    print >> outfile, x[0].index, x[1].index, EdgeToEdgeDict[x]
# ---------------------------------------------------------------------------------#
#	5d. Print FSA again, with these changes.
# ---------------------------------------------------------------------------------#


morphology.printFSA(outfile)
print
" out of loop"

# -------------------------------------------------------#

NumberOfCorrections = 0
for loopno in range(1, NumberOfCorrections):
    bestrobustness = 0
    count = 0
    globalbestrobustness = 0
    bestsigtochange = ''
    shift = ''
    bestwidth = 0
    bestchunk = ''
    print >> outfile, "\n\nIteration", loopno, " Best chunk found at end of stems in signatures: \n"

    for sig in Signatures.keys():
        n = 0
        stemlist = sorted(Signatures[sig])
        bestchunk, bestrobustness = findmaximalrobustsuffix(stemlist)
        if bestchunk:
            print >> outfile, "Here is a best chunk", sig, bestchunk
            if bestrobustness > globalbestrobustness:
                globalbestrobustness = bestrobustness
                bestsigtochange = sig
                shift = bestchunk
    print
    loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
    print >> outfile, "\n\nLoop number:", loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
    sig_target = bestsigtochange
    if len(shift) == 1:
        print >> outfile, "best chunk is 1 letter"
        StemToWord, Signatures = ShiftSignature(sig_target, shift, StemToWord, Signatures, outfile)
    if len(shift) > 1:
        print >> outfile, "best chunk is big: "
        StemToWord, Signatures = PullOffSuffix(sig_target, shift, StemToWord, Signatures, outfile)
    print >> outfile
    StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord, StemToSig, FindSuffixesFlag, outfile)
    printSignatures(Signatures, WordToSig, StemCounts, outfile, g_encoding, FindSuffixesFlag)

# -------------------------------------------------------------------------------------------------------------------------------#
print
"5b. End of finding robust suffixes in stem sets"
# -------------------------------------------------------------------------------------------------------------------------------#






# -------------------------------------------------------------------------------------------#
# 6. We consider each signature's stems, and ask for each stem t, whether t without its final letter is also a stem 
# in some other signature. We are looking for cases where two such stems *explain the same words*.
# If there are enough stem-pairs like that, we go ahead and try to explain those pairings
# as multi-stem (i.e., allomorphy) patterns.
# -------------------------------------------------------------------------------------------#
print
"6a. Deal with pairs of stems of adjacent lengths in distinct signatures"
# -------------------------------------------------------------------------------------------#
StemCountThreshold = 5
StemProportionThreshold = .9
print >> outfile, "\n\n***6. Pairs of stems of adjacent lengths.\n"
outputtemplate = "%35s : %35s  %15s %15s %50s"

if False:
    BiSigPatterns = {}
    for sig in Signatures.keys():
        stemlist = list(Signatures[sig])
        stemlist.sort()
        for stem in stemlist:
            localwords = StemToWord[stem]
            stem2 = stem[:-1]
            if g_encoding == "utf8":
                finalletter = stem[-1] + " "
            else:
                finalletter = "(" + stem[-1] + "): "
            if stem2 in StemToWord.keys():
                overlapwordset = localwords.intersection(StemToWord[stem2])
                wordstring = ""
                for word in overlapwordset:
                    wordstring += " " + word
                if len(overlapwordset) > 1:
                    sig2 = StemToSig[stem2]
                    if FindSuffixesFlag:
                        print >> outfile, outputtemplate % (sig, sig2, stem, stem2, wordstring)
                    else:
                        print >> outfile, "<", sig, ": ", sig2, ">\n\t", stem[::-1], stem2[::-1], overlapwordset
                    pattern = finalletter + "=" + sig + "=" + sig2
                    if not pattern in BiSigPatterns.keys():
                        BiSigPatterns[pattern] = 1
                    else:
                        BiSigPatterns[pattern] += 1

print
"6b. End of dealing with multiple sigs for stems"

if False:
    print >> outfile, "***\n\nSummary: "
    outputtemplate = "%5s  %5s  %20s  %20s   "
    patternlist = sorted(BiSigPatterns, key=BiSigPatterns.get, reverse=True)
    threshold = 2
    for item in patternlist:
        if BiSigPatterns[item] > threshold:
            letter, sig1, sig2 = item.split("=")
            print >> outfile, outputtemplate % (BiSigPatterns[item], letter, sig1, sig2)

    print >> outfile, "\n\n"

    print >> outfile, "-------------------------------------------------------"
    print >> outfile, "6. End of dealing with signatures with multiple stems"
    print >> outfile, "-------------------------------------------------------"
# -------------------------------------------------------------------------------------------#







# -------------------------------------------------------------------------------------------------------------------------------#
# 7. Separate joined affixes
print
"7. Separate joined affixes."
# -------------------------------------------------------------------------------------------------------------------------------#

SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
DisplayList = []

for sig, stemlist in SortedListOfSignatures:
    DisplayList.append((sig, len(stemlist), getrobustness(sig, stemlist)))
if False:
    for signo in range(len(DisplayList)):
        sig = DisplayList[signo][0]
        affixlist = sig.split('-')
        if not len(affixlist) == 2:
            continue;
        if not affixlist[0] == 'NULL':
            continue;
        if len(Signatures[sig]) < 10:
            continue;
        print >> outfile, "Signature", sig
        tally = 0
        stemset = Signatures[sig]
        for stem in stemset:
            biggerword = stem + affixlist[1]
            for otherstem in StemToWord.keys():
                if otherstem == stem:
                    continue
                if otherstem == biggerword:
                    continue
                if len(otherstem) > len(stem):
                    continue
                if biggerword in StemToWord[otherstem]:
                    tally += 1
                    print >> outfile, biggerword, "(", otherstem, ")"
                    # StemToWord[otherstem].discard(biggerword)
        print >> outfile, "Tally = ", tally


        # StemToWord, Signatures, WordToSig, StemToSig =  MakeSignatures(StemToWord, FindSuffixesFlag, outfile)
        # printSignatures(Signatures, WordToSig, StemCounts, outfile, g_encoding, FindSuffixesFlag)
        # printWordsToSigTransforms(Signatures, WordToSig, StemCounts, outfileSigTransforms, g_encoding, FindSuffixesFlag)

if False:
    PerfectSignatures = {}
    basictableau = intrasignaturetable()
    basictableau.setsignature(DisplayList[0][0])
    basictableau.displaytofile(outfile)

    print
    "On to loop"
    minimumstemcount = 15
    print >> outfile, "\n\nPerfect signatures: \n"
    ShortList = []
    MaxSizeForShortList = 100
    for sig1, numberofstems, robustness in DisplayList:
        if numberofstems < minimumstemcount:
            continue
        tableau1 = intrasignaturetable()
        tableau1.setsignature(sig1)
        print >> outfile, "\n\n--------------------------------------------------\n\t", "sig 1: ", sig1
        print >> outfile, "--------------------------------------------------\n\t"
        tableau1.displaytofile(outfile)
        print >> outfile, '\n'
        for sig2, numberofstems2, robustness2 in DisplayList:
            if numberofstems2 < minimumstemcount:
                continue
            if sig1 == sig2:
                continuecontraction
            if not sig1.count('-') == sig2.count('-'):
                continue
            print >> outfile, "\n\n---------------------------------\n\t", "sig 2: ", sig2
            tableau2 = intrasignaturetable()
            tableau2.setsignature(sig2)
            tableau2.minus(tableau1, side)
            print >> outfile, "Difference of tableaux:"
            compressedSize = tableau2.displaytofile(outfile)
            for n in range(len(ShortList)):
                # print ShortList[n]
                if compressedSize < ShortList[n][2]:
                    ShortList.insert(n, (sig1, sig2, compressedSize))
                    # print sig2
                    break;
            if n < MaxSizeForShortList:
                ShortList.append((sig1, sig2, compressedSize))
            if len(ShortList) > MaxSizeForShortList:
                del ShortList[-1]

    print >> outfile, "end of loop: "
    for n in range(len(ShortList)):
        print >> outfile, ShortList[n]


# ------------------------------------------------------------------------------------------#
class parseChunk:
    def __init__(self, morph, rString, edge=None):
        self.morph = morph
        self.edge = edge
        self.remainingString = rString
        if (edge):
            self.fromState = self.edge.fromState
            self.toState = self.edge.toState
        else:
            self.fromState = None
            self.toState = None

    def Copy(self, otherChunk):
        self.morph = otherChunk.morph
        self.edge = otherChunk.edge
        self.remainingString = otherChunk.remainingString


# ------------------------------------------------------------------------------------------#


# ------------------------------------------------------------------------------------------#
# This takes a State and a string and a set of parses of the string so far, and extends the set of parses 
def lparse(morphology, CompletedParses, IncompleteParses):
    currentParseChain = IncompleteParses.pop()  # or we could start reading it from the beginning, it shouldn't matter...
    currentParseChunk = currentParseChain[-1]
    currentParseToState = currentParseChunk.toState

    outgoingedges = currentParseToState.getOutgoingEdges()
    currentRemainingString = currentParseChunk.remainingString

    for edge in outgoingedges:
        for label in edge.labels:
            if label == "NULL" and len(
                    currentParseChunk.remainingString) == 0 and edge.toState.acceptingStateFlag == True:
                CopyOfCurrentParseChain = list()
                for item in currentParseChain:
                    chunkcopy = parseChunk(item.morph, item.remainingString, item.edge)
                    CopyOfCurrentParseChain.append(chunkcopy)
                newParseChunk = parseChunk(label, "", edge)
                CopyOfCurrentParseChain.append(newParseChunk)
                CompletedParses.append(CopyOfCurrentParseChain)
                break  # break in label's for loop

            labellength = len(label)
            if currentRemainingString[:labellength] == label:
                CopyOfCurrentParseChain = list()
                for item in currentParseChain:
                    chunkcopy = parseChunk(item.morph, item.remainingString, item.edge)
                    CopyOfCurrentParseChain.append(chunkcopy)
                if labellength == len(currentRemainingString) and edge.toState.acceptingStateFlag == True:
                    newParseChunk = parseChunk(label, "", edge)
                    CopyOfCurrentParseChain.append(newParseChunk)
                    CompletedParses.append(CopyOfCurrentParseChain)
                else:
                    newRemainingString = currentRemainingString[labellength:]
                    newParseChunk = parseChunk(label, newRemainingString, edge)
                    CopyOfCurrentParseChain.append(newParseChunk)
                    IncompleteParses.append(CopyOfCurrentParseChain)

    return (CompletedParses, IncompleteParses)


# ------------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------------#
#		User inquiries about morphology
# ------------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------------#


initialParseChain = list()
CompletedParses = list()
IncompleteParses = list()
word = ""
while True:
    word = raw_input('Inquiry about a word: ')
    if word == "exit":
        break
    if word == "State":
        while True:
            stateno = raw_input("State number:")
            if stateno == "" or stateno == "exit":
                break
            stateno = int(stateno)
            state = morphology.States[stateno]
            for edge in state.getOutgoingEdges():
                print
                "Edge number", edge.index
                i = 0
                for morph in edge.labels:
                    print
                    "%12s" % morph,
                    i += 1
                    if i % 6 == 0: print
            print
            "\n\n"
            continue
    if word == "Edge":
        while True:
            edgeno = raw_input("Edge number:")
            if edgeno == "" or edgeno == "exit":
                break
            edgeno = int(edgeno)
            for edge in morphology.Edges:
                if edge.index == int(edgeno):
                    morphlist = list(edge.labels)
            for i in range(len(morphlist)):
                print
                "%12s" % morphlist[i],
                if i % 6 == 0:
                    print
            print
            "\n\n"
            continue
    del CompletedParses[:]
    del IncompleteParses[:]
    del initialParseChain[:]
    startingParseChunk = parseChunk("", word)
    startingParseChunk.toState = morphology.startState

    initialParseChain.append(startingParseChunk)
    IncompleteParses.append(initialParseChain)
    while len(IncompleteParses) > 0:
        CompletedParses, IncompleteParses = lparse(morphology, CompletedParses, IncompleteParses)
    if len(CompletedParses) == 0: print
    "no analysis found."

    for parseChain in CompletedParses:
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.morph,
        print
    print

    for parseChain in CompletedParses:
        print
        "\tStates: ",
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.fromState.index,
        print
        "\t", thisParseChunk.toState.index
    print

    for parseChain in CompletedParses:
        print
        "\tEdges: ",
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.edge.index,
        print
    print
    "\n\n"

# ---------------------------------------------------------------------------------------------------------------------------#
# We create a list of words, each word with its signature transform (so DOGS is turned into NULL.s_s, for example)

if False:
    printWordsToSigTransforms(Signatures, WordToSig, StemCounts, outfileSigTransforms, g_encoding, FindSuffixesFlag)

# ---------------------------------------------------------------------------------------------------------------------------#

outfile.close()
# print outfilename





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
