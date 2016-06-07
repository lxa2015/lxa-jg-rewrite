#  This script takes a wordlist as input, and a specific signature is hard coded (about 7 lines down from here). 
#  It determines all of the stems that match this signature perfectly .
#  It outputs the data in a format readable by R for color-coded display of words against this signature.

# Because of an R peculiarity, we are skipping words that contain an apostrophe

from collections import defaultdict

Signatures = []
# Signatures.append( "s.NULL")
# Signatures.append("ing.ed.s.NULL")
Signatures.append("NULL.e.en")
NumberOfSignatures = 1
colors = {}
colors[Signatures[0]] = 2  # red
# colors[Signatures[1]] 	= 12  	# blue
colors[3] = 11  # green
colors[4] = 10  # black
colors[5] = 6  # violet
colors[6] = 13  # light blue
##---------------------------------------------------------------------------------------------------------------------
# 1. Read in signature, maybe from console. Canonical order will be descending length where null counts as zero length, and alphabetized among equilength affixes.
affixes = {}
ThisSignaturesWords = defaultdict(dict)
for sig in Signatures:
    affixes[sig] = sig.split('.')

# 2 Read in word list, prepare for output
##-------------------------------------------------------------------------------------------
language = r'browncorpus'
size = 48
infolder = r'../../data/german/'
infile = infolder + language + "_LRM_" + str(size) + "Kwords.txt"
infile = infolder + "german.dic"
# infile = r'../../data/test2.txt'


outfolder = r'../../data/german/'
outfilename = outfolder + language + '-' + "StemDistribution" + '.txt'
outfilename = outfolder + "stemdistribution.txt"
outfile = open(outfilename, "w")
# print >>outfile,  'ing', 'ed', 's', 'NULL'
print >> outfile, "en", "e", "NULL"
print
outfilename

lexicon = {}
counts = {}
for line in open(infile):
    if line.find("\'") > -1:
        continue
    data = line.split()
    word = data[0]
    lexicon[word] = (data[1], data[3])  # lower x and y coordinates. Should use average, not lower!!
    counts[word] = float(data[6])

for sig in Signatures:
    print
    sig
    ##---------------------------------------------------------------------------------------------------------------------
    # 3. Put all the words that satisfy the signature in a list/dictionary.
    WordsSatisfyingInitialSignature = {}
    ##---------------------------------------------------------------------------------------------------------------------
    # 4. Loop through affixes, longest first
    StemsFromAffixes = defaultdict(dict)
    for affix in affixes[sig]:

        if affix == 'NULL':
            affix = ''
        negativeaffixlength = -1 * len(affix)
        if negativeaffixlength == 0:
            StemsFromAffixes[affix] = lexicon  # this treats null the same as any other affix....
        else:
            for word in lexicon:
                if word[negativeaffixlength:] == affix:
                    stem = word[:negativeaffixlength]
                    StemsFromAffixes[affix][stem] = 1

                    ##---------------------------------------------------------------------------------------------------------------------
                    # Find stems  in the intersection of all of these StemsFromAffixes sets.
    StemsFromSig = {}

    # print >>outfile, "Good words: "
    AllRegularWords = {}
    for stem in StemsFromAffixes[affixes[sig][0]]:
        stembad = False
        for affix in affixes[sig]:
            if affix == 'NULL':
                affix = ''
            if affix == affixes[sig][0]:
                continue
            elif not (stem in StemsFromAffixes[affix]):
                stembad = True
                break
        if stembad == False:
            StemsFromSig[stem] = 1
            for affix in affixes[sig]:
                if affix == 'NULL':
                    affix = ''
                word = stem + affix
                ThisSignaturesWords[sig][word] = 1
                AllRegularWords[word] = 1
                #				%print >>outfile, word
                #	%print >>outfile, "end of good words"

                ##-----------------------------------------------------------------------------------------------

    for stem in StemsFromSig:
        #		print >>outfile, stem,
        total = 0
        for affix in affixes[sig]:
            if affix == 'NULL':
                affix = ''
            word = stem + affix
            total += float(counts[word])
        for affix in affixes[sig]:
            if affix == 'NULL':
                affix = ''
            word = stem + affix
            print >> outfile, counts[word] / total,
        print >> outfile

##---------------------------------------------------------------------------------------------------------------------
# for all the words that have not been identified: light gray
color = 8  # light gray
pch = 21
size = 1
for word in lexicon:
    if word in AllRegularWords:
        continue
    x, y = lexicon[word]
# print >>outfile, word, x,y,color, pch, size
##---------------------------------------------------------------------------------------------------------------------
for sig in Signatures:
    color = colors[sig]
    pch = 16  # symbol used on graphic
    size = .5
    for word in ThisSignaturesWords[sig]:
        x, y = lexicon[word]
# print >>outfile, word, x,y , color, pch, size
