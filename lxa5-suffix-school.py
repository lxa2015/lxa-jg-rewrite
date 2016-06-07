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

g_encoding = ""  # "utf8"

MinimumStemLength = 4
MaximumAffixLength = 5
MinimumStemCount = 4
MinimumNumberofSigUses = 15


# Signatures is a map: its keys are signatures. Its values are *sets* of stems.
# StemToWord is a map; its keys are stems.      Its values are *sets* of words.
# StemToSig is a map; its keys are stems.       Its values are *lists* of signatures.
# WordToSig is a Map. its keys are words.       Its values are *lists* of signatures
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
def Expansion(sig, stem):
    wordset = set()
    affixlist = sig.split('-')
    for affix in affixlist:
        if affix == 'NULL':
            affix = ''
        wordset.add(stem + affix)
    return wordset


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
def subsignature(sig1, sig2):
    sigset1 = set(sig1.split('-'))
    sigset2 = set(sig2.split('-'))
    if sigset1 <= sigset2:  # subset
        return True
    return False


# ----------------------------------------------------------------------------------------------------------------------------#

# ----------------------------------------------------------------------------------------------------------------------------#
def printSignatures(Signatures, WordToSig, outfile):
    # ----------------------------------------------------------------------------------------------------------------------------#
    # Print signatures (not their stems) , sorted by number of stems
    SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
    DisplayList = []
    for sig, stemlist in SortedListOfSignatures:
        DisplayList.append((sig, len(stemlist), getrobustness(sig, stemlist)))
    DisplayList.sort

    print >> outfile, "\n--------------------------------------------------------------"
    print >> outfile, '{0:<35}{1:12s} {2:12s}'.format("Signature", "Stem count", "Robustness")
    print >> outfile, "--------------------------------------------------------------"
    for sig, stemcount, robustness in DisplayList:
        if g_encoding == "utf8":
            print >> outfile, sig, stemcount, robustness
        else:
            print >> outfile, '{0:<35}{1:6d} {2:6d}'.format(sig, stemcount, robustness)
    print >> outfile, "--------------------------------------------------------------"

    # Print signatures (not their stems) sorted by robustness
    print >> outfile, "***"
    print >> outfile, "\nSorted by Robustness\n"
    DisplayList = sorted(DisplayList, lambda x, y: cmp(x[2], y[2]), reverse=True)
    print >> outfile, '{0:<35}{1:12s} {2:12s}'.format("Signature", "Stem count", "Robustness")
    print >> outfile, "--------------------------------------------------------------"
    for sig, stemcount, robustness in DisplayList:
        if g_encoding == "utf8":
            print >> outfile, sig, stemcount, robustness
        else:
            print >> outfile, '{0:<35}{1:6d} {2:6d}'.format(sig, stemcount, robustness)
    print >> outfile, "--------------------------------------------------------------"

    # print the stems of each signature:

    numberofstemsperline = 6
    stemlist = []
    count = 0
    print >> outfile, "***\n *** Stems in each signature"
    for sig, stemcount, robustness in DisplayList:
        if g_encoding == "utf8":
            print >> outfile, "\n\n\n=============================================\n", sig, "\n"
        else:
            print >> outfile, "\n\n\n=============================================\n", '{0:30s} \n'.format(sig)
        n = 0
        stemlist = sorted(Signatures[sig])
        for stem in stemlist:
            n += 1
            print >> outfile, '{0:12s}'.format(stem),
            if n == numberofstemsperline:
                n = 0
                print >> outfile
                # shiftstring = findmaximalrobustsuffix (stemlist, outfile,count)
                # Shift one letter from stem to suffix if the overwhelming majority of stems end with that letter:

                # print WORDS of each signature:
    words = WordToSig.keys()
    words.sort()
    print >> outfile, "***"
    print >> outfile, "\n--------------------------------------------------------------"
    print >> outfile, "Words and their signatures"
    print >> outfile, "--------------------------------------------------------------"
    print >> outfile, '{0:<30}{1}'.format("Word", "Signatures")
    print >> outfile, "--------------------------------------------------------------\n"
    for word in words:
        if g_encoding == "utf8":
            print >> outfile, word,
            for sig in WordToSig[word]:
                print >> outfile, sig,
            print >> outfile
        else:
            print >> outfile, '{0:<30}{1}'.format(word, WordToSig[word])
            # ----------------------------------------------------------------------------------------------------------------------------#
    return


# ----------------------------------------------------------------------------------------------------------------------------#




# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def getrobustness(sig, stems):
    # ----------------------------------------------------------------------------------------------------------------------------#
    countofsig = len(sig)
    countofstems = len(stems)
    lettersinstems = 0
    lettersinaffixes = 0
    for stem in stems:
        lettersinstems += len(stem)
    for affix in sig:
        lettersinaffixes += len(affix)
    # ----------------------------------------------------------------------------------------------------------------------------#
    return lettersinstems * (countofsig - 1) + lettersinaffixes * (countofstems - 1)


# ----------------------------------------------------------------------------------------------------------------------------#




# ----------------------------------------------------------------------------------------------------------------------------#
def TestForCommonSuffix(stemlist, outfile):
    # ----------------------------------------------------------------------------------------------------------------------------#
    CommonLastLetter = ''
    ExceptionCount = 0
    proportion = 0.0
    FinalLetterCount = {}
    for stem in stemlist:
        l = stem[-1]
        if not l in FinalLetterCount.keys():
            FinalLetterCount[l] = 1
        else:
            FinalLetterCount[l] += 1

    sorteditems = sorted(FinalLetterCount, key=FinalLetterCount.get, reverse=True)  # sort by value
    CommonLastLetter = sorteditems[0]
    if (len(sorteditems)) == 1:
        ExceptionCount = 0
        proportion = 1.0
    else:
        ExceptionCount = len(stemlist) - FinalLetterCount[CommonLastLetter]
        proportion = 1 - float(ExceptionCount) / float(len(stemlist))
    for letter in sorteditems:
        print >> outfile, letter, FinalLetterCount[letter]
    # ----------------------------------------------------------------------------------------------------------------------------#
    return (CommonLastLetter, ExceptionCount, proportion)


# ----------------------------------------------------------------------------------------------------------------------------#









# ----------------------------------------------------------------------------------------------------------------------------#
def ShiftFinalLetter(StemToWord, stemlist, CommonLastLetter, sig):
    # ----------------------------------------------------------------------------------------------------------------------------#
    newsig = ''
    affixlist = sig.split('-')
    newaffixlist = []
    for affix in affixlist:
        if affix == "NULL":
            newaffixlist.append(CommonLastLetter)
        else:
            newaffixlist.append(CommonLastLetter + affix)
    newsig = makesignature(newaffixlist)
    # print "old sig", sig, "new sig", newsig
    for stem in stemlist:
        if not stem[-1] == CommonLastLetter:
            continue
        newstem = stem[:-1]
        if not newstem in StemToWord.keys():
            StemToWord[newstem] = set()
        wordlistcopy = StemToWord[stem].copy()
        for word in wordlistcopy:
            StemToWord[stem].remove(word)
            if not word in StemToWord[newstem]:
                StemToWord[newstem].add(word)
        if len(StemToWord[stem]) == 0:
            del StemToWord[stem]
            # ----------------------------------------------------------------------------------------------------------------------------#
    return (StemToWord, newsig)


# ----------------------------------------------------------------------------------------------------------------------------#











# ----------------------------------------------------------------------------------------------------------------------------#
def findmaximalrobustsuffix(wordlist, outfile, bestcount):
    # ----------------------------------------------------------------------------------------------------------------------------#
    bestchunk = ""
    bestwidth = 0
    bestlength = 0
    bestrobustness = 0
    maximalchunksize = 4  # should be 3 or 4 ***********************************
    threshold = 50
    bestsize = 0
    # sort by end of words:
    templist = []
    for word in wordlist:
        wordrev = word[::-1]
        templist.append(wordrev)
    templist.sort()
    wordlist = []
    for wordrev in templist:
        word = wordrev[::-1]
        wordlist.append(word)
    for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the suffix being considered
        numberofoccurrences = 0
        here = 0
        while (here < len(wordlist) - 1):
            numberofoccurrences = 0
            chunk = wordlist[here][-1 * width:]
            for there in range(here + 1, len(wordlist)):
                if (not wordlist[there][-1 * width:] == chunk) or (there == len(wordlist) - 1):
                    numberofoccurrences = there - here
                    currentrobustness = numberofoccurrences * width
                    if currentrobustness > bestrobustness:
                        bestrobustness = currentrobustness
                        bestchunk = chunk
                        bestwidth = width
                        bestnumberofoccurrences = numberofoccurrences
                        count = numberofoccurrences
                    break
            here = there
    permittedexceptions = 2
    if bestwidth == 1:
        if bestnumberofoccurrences > 5 and bestnumberofoccurrences >= len(
                wordlist) - permittedexceptions and bestrobustness > threshold:
            return (bestchunk, bestrobustness)
    if bestrobustness > threshold:
        return (bestchunk, bestrobustness)
    # ----------------------------------------------------------------------------------------------------------------------------#
    return ('', 0)


# ----------------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------------#
def find-N - highest - weight - suffix(N, wordlist, outfile, bestcount)

:
# ----------------------------------------------------------------------------------------------------------------------------#

maximalchunksize = 4  # should be 3 or 4 ***********************************
totalweight = 0
threshold = 50
weightthreshold = 0.005

# sort by end of words:
templist = []
for word in wordlist:
    wordrev = word[::-1]
    templist.append(wordrev)
templist.sort()
wordlist = []
weightlist = []
for wordrev in templist:
    word = wordrev[::-1]
    wordlist.append(word)
    totalweight += len(word)
for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the suffix being considered
    numberofoccurrences = 0
    here = 0
    while (here < len(wordlist) - 1):
        numberofoccurrences = 0
        chunk = wordlist[here][-1 * width:]
        for there in range(here + 1, len(wordlist)):
            if (not wordlist[there][-1 * width:] == chunk) or (there == len(wordlist) - 1):
                numberofoccurrences = there - here
                currentweight = numberofoccurrences * width
                if currentweight > 0:
                    weightlist.append((chunk, currentweight, numberofoccurrences))
                break
        here = there
permittedexceptions = 2

chunks = []
chunks = sorted(weightlist.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
chunks - copy = chunks[:]
for chunk in chunks - copy:
    if estnumberofoccurrences > 5 and bestnumberofoccurrences >= len(
            wordlist) - permittedexceptions and bestweight > threshold:
        return (bestchunk, bestweight)
if bestrobustness > threshold:
    return (bestchunk, bestrobustness)
# ----------------------------------------------------------------------------------------------------------------------------#
return ('',
        0)  # ----------------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------------#
def MakeBiSignatures_suffixes(wordlist,
                              SigToTuple):  # This function finds pairs of words which make a valid signature, and makes Dictionary whose key is the signature and whose value is a tuple: stem, word1, word2, signature.
    # ----------------------------------------------------------------------------------------------------------------------------#
    bisig = []  # signature with exactly two affixes
    numberofwords = len(wordlist)
    for n in range(numberofwords):
        word1 = wordlist[n]
        word1 = word1.lower()
        word1length = len(word1)
        minstem = word1[:MinimumStemLength]
        thisminstemlength = len(minstem)
        if n % 1000 == 0:
            print
            n, word1
        for m in range(n + 1, numberofwords):
            word2 = wordlist[m]
            word2length = len(word2)
            if not minstem == word2[:MinimumStemLength]:
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

            # ----------------------------------------------------------------------------------------------------------------------------#
    return SigToTuple


# ----------------------------------------------------------------------------------------------------------------------------#

# ----------------------------------------------------------------------------------------------------------------------------#
def MakeSignatures(StemToWord):  # Signatures is a map from the signature to a set of its stems.
    # ----------------------------------------------------------------------------------------------------------------------------#
    # Signatures is a map: its keys are signatures. Its values are *sets* of stems.
    # StemToWord is a map; its keys are stems.      Its values are *sets* of words.
    # WordToSig is a Map. its keys are words.       Its values are *lists* of signatures
    # StemToSig is a Map. Its keys are stems.	Its values are *lists* of signatures.
    WordToSig = {}
    Signatures = {}
    StemToSig = {}
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
        # print >>outfile, thissig
        if not thissig in Signatures:
            Signatures[thissig] = set()
        Signatures[thissig].add(stem)
        if not stem in StemToSig.keys():
            StemToSig[stem] = []
        StemToSig[stem].append(thissig)
        for word in StemToWord[stem]:
            if not word in WordToSig:
                WordToSig[word] = []
            WordToSig[word].append(thissig)
            # print thissig
            # ----------------------------------------------------------------------------------------------------------------------------#
    return (StemToWord, Signatures, WordToSig, StemToSig)


# ----------------------------------------------------------------------------------------------------------------------------#







# ----------------------------------------------------------------------------------------------------------------------------#
def ShiftSignature(sig_target, shift, StemToWord, Signatures, outfile):
    # ----------------------------------------------------------------------------------------------------------------------------#
    print >> outfile, "-------------------------------------------------------"
    print >> outfile, "Shift wrongly cut suffixes"
    print >> outfile, "-------------------------------------------------------"
    suffixlist = []
    print >> outfile, sig_target, shift
    suffixes = sig_target.split('-')
    for n in range(len(suffixes)):
        if suffixes[n] == 'NULL':
            suffixes[n] = ''
    for suffix in suffixes:
        suffix = shift + suffix
        suffixlist.append(suffix)
    suffixlist.sort()
    newsig = '-'.join(suffixlist)
    Signatures[newsig] = set()
    shiftlength = len(shift)
    stemset = Signatures[sig_target].copy()  # a set to iterate over while removing stems from Signature[sig_target]
    for stem in stemset:
        thesewords = []
        if not stem.endswith(shift):
            continue
        newstem = stem[:-1 * shiftlength]
        for suffix in suffixes:
            thesewords.append(stem + suffix)
        Signatures[sig_target].remove(stem)
        Signatures[newsig].add(newstem)
        for word in thesewords:
            StemToWord[stem].remove(word)
        if len(StemToWord[stem]) == 0:
            del StemToWord[stem]
        if not newstem in StemToWord:
            StemToWord[newstem] = set()
        for word in thesewords:
            StemToWord[newstem].add(word)
    if len(Signatures[sig_target]) == 0:
        del Signatures[sig_target]
    # ----------------------------------------------------------------------------------------------------------------------------#
    return (StemToWord, Signatures)


# ----------------------------------------------------------------------------------------------------------------------------#




# ----------------------------------------------------------------------------------------------------------------------------#
def PullOffSuffix(sig_target, shift, StemToWord, Signatures, outfile):
    # ----------------------------------------------------------------------------------------------------------------------------#
    print >> outfile, "-------------------------------------------------------"
    print >> outfile, "Pull off a suffix from a stem set"
    print >> outfile, "-------------------------------------------------------"
    print >> outfile, sig_target, shift
    print
    sig_target, shift
    shiftlength = len(shift)
    newsig = shift
    suffixes = sig_target.split('-')
    stemset = Signatures[sig_target].copy()  # a set to iterate over while removing stems from Signature[sig_target]
    while newsig in Signatures:
        newsig = "*" + newsig  # add *s to beginning to make sure the string is unique, i.e. not used earlier elsewhere
    print
    "newsig", newsig
    Signatures[newsig] = set()
    StemToWord["*" + shift] = sig_target
    print
    "adding", shift, "to", sig_target
    for stem in stemset:
        thesewords = []
        if not stem.endswith(shift):
            continue
        newstem = stem[:-1 * shiftlength]
        for suffix in suffixes:
            if suffix == "NULL":
                word = stem
            else:
                word = stem + suffix
            StemToWord[stem].remove(word)
        # print "Remove: " , word, "from stem ", stem
        # print
        if len(StemToWord[stem]) == 0:
            del StemToWord[stem]
        if newstem in StemToWord:
            newstem = "*" + newstem
            StemToWord[newstem] = set()
        for word in thesewords:
            StemToWord[newstem].add(word)
    if len(Signatures[sig_target]) == 0:
        del Signatures[sig_target]
    # ----------------------------------------------------------------------------------------------------------------------------#
    return (StemToWord, Signatures)


# ----------------------------------------------------------------------------------------------------------------------------#






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
outfilename = outfolder + language + str(size) + "Kwords" + "_extendedsigs.txt"
if g_encoding == "utf8":
    outfile = codecs.open(outfilename, encoding="utf-8", mode='w')
    print
    "yes utf8"
else:
    outfile = open(outfilename, mode='w')
outfile = open(outfilename, "w")

# ----------------------------------------------------------#

filelines = infile.readlines()
words = {}

for line in filelines:
    pieces = line.split(' ')
    word = pieces[0]
    #	word = word[:-1] # for french only?
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
Signatures = {}
WordToSig = {}
StemToWord = {}
numberofwords = len(wordlist)
stemfilename = infolder + language + "_" + str(size) + "Kwords_stems" + ".txt"
StemFileExistsFlag = False
if os.path.isfile(stemfilename):
    StemFileExistsFlag = True
    stemfile = open(stemfilename)
    filelines = stemfile.readlines()
    for line in filelines:
        pieces = line.split()
        stem = pieces[0]
        StemToWord[stem] = set()
        for i in range(1, len(pieces)):
            StemToWord[stem].add(pieces[i])
else:
    SigToTuple = MakeBiSignatures_suffixes(wordlist, SigToTuple)
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

if (StemFileExistsFlag):  # we use this to create a one-time list of stems with their words
    if g_encoding == "utf8":
        outfile2 = codecs.open(stemfilename, encoding="utf-8", mode="w")
    else:
        outfile2 = open(stemfilename, "w")

    for stem in StemToWord.keys():
        # print "stem: ", stem
        print >> outfile2, stem,
        for word in StemToWord[stem]:
            print >> outfile2, word,
        print >> outfile2

# -----------------------------------------------------------------------------------------------------------------#
#	Make signatures, and WordToSig dictionary, and Signature dictionary-of-stem-lists, and StemToSig dictionary
# -----------------------------------------------------------------------------------------------------------------#
StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord)
printSignatures(Signatures, WordToSig, outfile)

# -----------------------------------------------------------------------------------------------------------------#
#	Find larger groupings of signatures
# -----------------------------------------------------------------------------------------------------------------#
# sort by robustness

print >> outfile, "\n\n  *** Find larger groupings of signatures \n\n"
print
"Find larger groupings of signatures"
SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
SortedList = []
for sig in Signatures.keys():
    SortedList.append((sig, getrobustness(sig, Signatures[sig])))
SortedList = sorted(SortedList, lambda x, y: cmp(x[1], y[1]), reverse=True)
# for sig in SortedList:
#	print >>outfile, sig[0]

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

print >> outfile, "\n\n  *** End of finding larger groupings of signatures \n\n"

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# In this loop, we check with each set of stems (each signature) if they all end with the same letter (or n-gram). If they
#  do, we shift at least one letter to the suffix.
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
sizethreshold = 5
exceptionthreshold = 6
proportionthreshold = .9
proportion = 0.000
MaximalLettersToShift = 0  ######################################## note that this is now 0
print >> outfile, "***"
print >> outfile, "\n\n Shift one letter from end of stems"
for loopno in range(MaximalLettersToShift):
    for sig in Signatures.keys():
        stemlist = sorted(Signatures[sig])
        if len(stemlist) < sizethreshold:
            continue
        # print >>outfile, "checking out: ", sig
        (CommonLastLetter, ExceptionCount, proportion) = TestForCommonSuffix(stemlist, outfile)
        if ExceptionCount <= exceptionthreshold and proportion >= proportionthreshold:
            print >> outfile, "Shiftable signature: ", sig, proportion, CommonLastLetter
            StemToWord, newsig = ShiftFinalLetter(StemToWord, stemlist, CommonLastLetter, sig)
            # if ExceptionCount > exceptionthreshold:
            #	print >>outfile, sig, CommonLastLetter, "Too many exceptions", ExceptionCount
            # if proportion > 0.5 and proportion < proportionthreshold:
            #	print >>outfile, sig, "proportion of final letter too low:", proportion

    StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord)

printSignatures(Signatures, WordToSig, outfile)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# In this loop, we look to see which signatures could be improved, and score the improvement quantitatively with robustness.
# Then we improve the one whose robustness increase is the greatest.
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
NumberOfCorrections = 1
print >> outfile, "***"
print
"Finding robust suffixes in stem sets"
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
        bestchunk, bestrobustness = findmaximalrobustsuffix(stemlist, outfile, count)
        if bestchunk:
            print >> outfile, sig, bestchunk
            if bestrobustness > globalbestrobustness:
                globalbestrobustness = bestrobustness
                bestsigtochange = sig
                shift = bestchunk
                # print loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
    sig_target = bestsigtochange
    if len(shift) == 1:
        # print "best chunk is 1 letter"
        StemToWord, Signatures = ShiftSignature(sig_target, shift, StemToWord, Signatures, outfile)
    if len(shift) > 1:
        # print "best chunk is big: "
        StemToWord, Signatures = PullOffSuffix(sig_target, shift, StemToWord, Signatures, outfile)
    print >> outfile
    StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord)
    printSignatures(Signatures, WordToSig, outfile)

print
"End of finding robust suffixes in stem sets"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#





# --------------------------------------------------#
print
"Deal with signatures with multiple stems."
# --------------------------------------------------#
# We consider each signature's stems, and ask for each stem t, whether t without its final letter is also a stem 
# in some other signature. We are looking for cases where two such stems *explain the same words*.
# If there are enough stem-pairs like that, we go ahead and try to explain those pairings
# as multi-stem (i.e., allomorphy) patterns.

StemCountThreshold = 5
StemProportionThreshold = .9
print >> outfile, "\n\nSignatures with multiple stems"
print
"Multiple stems in sigs"
BiSigPatterns = {}
for sig in Signatures.keys():
    print >> outfile, sig
    # print sig
    stemlist = list(Signatures[sig])
    stemlist.sort()
    for stem in stemlist:
        localwords = Expansion(sig, stem)  # this is a *set*
        # for word in  localwords:
        #	print word
        stem2 = stem[:-1]
        # print "stem and stem2", stem, stem2
        if g_encoding == "utf8":
            finalletter = unichr(stem[-1])
        else:
            finalletter = "(" + stem[-1] + "): "
        # print finalletter
        if stem2 in StemToWord.keys():
            # for word in StemToWord[stem2]:
            # print "words in stem:", stem2, word
            overlapwordset = localwords.intersection(StemToWord[stem2])
            # for word in overlapwordset:
            # print "overlapset", word
            if len(overlapwordset) > 1:
                print >> outfile, "\t", stem, stem2, overlapwordset
                for word in overlapwordset:
                    print >> outfile, "\t\t", word, WordToSig[word]
                    pattern = WordToSig[word]
                    pattern.sort()
                    pattern = '='.join(pattern)
                    pattern = finalletter + pattern
                    if not pattern in BiSigPatterns.keys():
                        BiSigPatterns[pattern] = 1
                    else:
                        BiSigPatterns[pattern] += 1
                print >> outfile, "\n"
print
"End of dealing with multiple sigs for stems"

print >> outfile, "-------------------------------------------------------"
print >> outfile, "End of dealing with signatures with multiple stems"
print >> outfile, "-------------------------------------------------------"
patternlist = sorted(BiSigPatterns, key=BiSigPatterns.get, reverse=True)
for item in patternlist:
    if BiSigPatterns[item] > 5:
        print >> outfile, item, BiSigPatterns[item]

# --------------------------------------------------#
print
"Separate joined affixes."
# --------------------------------------------------#



SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
DisplayList = []

for sig, stemlist in SortedListOfSignatures:
    DisplayList.append((sig, len(stemlist), getrobustness(sig, stemlist)))
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

StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord)
printSignatures(Signatures, WordToSig, outfile)

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
