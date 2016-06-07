#  This script takes a ccw as input, and a specific signature is hard coded (about 7 lines down from here). 
#  It determines all of the stems that match this signature perfectly .
#  It outputs the data in a format readable by R for color-coded display of words against this signature.

# Because of an R peculiarity, we are skipping words that contain an apostrophe

from collections import defaultdict

Signature = ""

colors = {}
colors['ED'] = 9  # black
colors['ed'] = 9  # black
colors['ING'] = 10  # red
colors['ing'] = 10  # red
colors['S'] = 11  # green
colors['s'] = 11  # green
colors[''] = 12  # blue
colors['e'] = 6  # violet
colors['E'] = 6  # violet
colors['es'] = 13  # light blue
colors['ES'] = 13  # light blue
colors['ly'] = 10  # red

colors['er'] = 10  # red
colors['e'] = 11  # green
colors['ent'] = 12  # blue
# 1. Read in word list, prepare for output
##-------------------------------------------------------------------------------------------
language = r'german'
size = 30
infolder = r'../../data/' + language + r'/'
infile = infolder + language + str(size) + "Kwords.ccw"
# infile = infolder+ language_12Kvocab.txt"


outfolder = r'../../data/' + language + r'/'
outfilename = outfolder + language + '-' + Signature + '-R.txt'
outfile = open(outfilename, "w")
print >> outfile, 'word', 'x', 'y', 'mycolor', 'mypch', 'mycex'
print
outfilename

lexicon = {}
for line in open(infile):
    if line.find("\'") > -1:
        continue
    data = line.split()
    word = data[0]
    if word[0] == '"':
        continue
    lexicon[word] = (data[1], data[2])  # lower x and y coordinates. Should use average, not lower!!

##---------------------------------------------------------------------------------------------------------------------
# 2. Read in signature, maybe from console. Canonical order will be descending length where null counts as zero length, and alphabetized among equilength affixes.
affixes = Signature.split('.')

ThisSignaturesWords = {}
##---------------------------------------------------------------------------------------------------------------------
# 3. Put all the words that satisfy the signature in a list/dictionary.
WordsSatisfyingInitialSignature = {}
##---------------------------------------------------------------------------------------------------------------------
# 4. Loop through affixes, longest first
StemsFromAffixes = defaultdict(dict)
for affix in affixes:
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
pch = 16  # symbol used on graphic

regularwords = {}
for stem in StemsFromAffixes[affixes[0]]:
    stembad = False
    for affix in affixes:
        if affix == 'NULL':
            affix = ''
        if affix == affixes[0]:
            continue
        elif not (stem in StemsFromAffixes[affix]):
            stembad = True
            break
    if stembad == False:
        StemsFromSig[stem] = 1
        for affix in affixes:
            if affix == 'NULL':
                affix = ''
            word = stem + affix
            regularwords[word] = 1

color = 9  # light gray
pch = 21
size = .2
for word in lexicon:
    if word in regularwords:
        continue
    x, y = lexicon[word]
    print >> outfile, word, x, y, color, pch, size

pch = 16  # symbol used on graphic
size = .6
for stem in StemsFromSig:
    for affix in affixes:
        if affix == 'NULL':
            affix = ''
        word = stem + affix
        x, y = lexicon[word]
        if affix in colors:
            thiscolor = colors[affix]
        else:
            thiscolor = 1
        print >> outfile, word, x, y, thiscolor, pch, size
