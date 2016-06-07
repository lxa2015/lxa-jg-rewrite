#  This script takes a wordlist as input, and a specific signature is hard coded (about 7 lines down from here). 
#  It determines all of the stems that match this signature perfectly, and then it seeks stems that match it imperfectly.
#  It can output the data in a format readable by R for color-coded display of words against this signature.

##--------------------------------------------------------------------##
##		Main program begins on line 210. 
##--------------------------------------------------------------------##


from collections import defaultdict

Signature = 'ing.ed.s.NULL'


##--------------------------------------------------------------------##
##		Some functions:
##--------------------------------------------------------------------##

def makesortedstring(string):
    letters = list(string)
    letters.sort()
    return letters


## --------------------

def Difference1(string1, string2, maxdiff):
    minimalcommonprefix = 3
    if string1 == string2:
        return 0
    length1 = len(string1)
    length2 = len(string2)
    if length1 - length2 > maxdiff or length2 - length1 > maxdiff:
        return 99
    commonprefixlength = 0
    for i in range(1, length1 + 1):
        if i > length2:
            break
        if string1[0:i] == string2[0:i]:
            commonprefixlength = i
        else:
            break

    difference = length1 + length2 - 2 * commonprefixlength
    return difference


def stringdiff(instring1, instring2, positive, negative):
    if instring1 == 'NULL':
        instring1 = ''
    if instring2 == 'NULL':
        instring2 = ''
    string1 = makesortedstring(instring1)
    string2 = makesortedstring(instring2)
    i = 0
    j = 0
    del positive[:]
    del negative[:]
    while (1):
        if (i < len(string1) and j < len(string2)):
            if (string1[i] == string2[j]):
                i = i + 1
                j = j + 1
            elif (string1[i] < string2[j]):
                positive.append(string1[i])
                i = i + 1
            else:
                negative.append(string2[j])
                j = j + 1
        elif (i >= len(string1)):
            for k2 in range(j, len(string2)):
                negative.append(string2[k2])

            break;
        elif (j >= len(string2)):

            for k1 in range(i, len(string1)):
                positive.append(string1[k1])

            break;
            # print 'positive', positive, 'negative', negative


def DifferenceOfDifference((X1, X2), (Y1, Y2)):
    x1 = list(X1)
    x2 = list(X2)
    y1 = list(Y1)
    y2 = list(Y2)
    r1 = []
    r2 = []
    x1.extend(y2)  # add y2 to x1
    del y2[:]
    x1.sort()

    x2.extend(y1)
    del y1[:]
    x2.sort()

    while len(x1) > 0:  # remove anything in y1 from x1
        if len(x2) == 0:
            r1.extend(x1)
            del x1[:]
            break
        else:
            if x1[0] < x2[0]:
                r1.append(x1.pop(0))
            elif x1[0] == x2[0]:
                x1.pop(0)
                x2.pop(0)
            else:
                r2.append(x2.pop(0))
    if len(x2) > 0:
        r2.extend(x2)
        del x2[:]

    return (r1, r2)


class intrasignaturetable:
    def setsignature(self, sig):
        self.affixes = sig.split('.')
        for affix in self.affixes:
            if affix == 'NULL':
                affix = ''
        self.differences = {}
        self.differences2 = {}
        positive = []
        negative = []

        for index1 in range(len(self.affixes)):
            for index2 in range(len(self.affixes)):
                affix1 = self.affixes[index1]
                affix2 = self.affixes[index2]
                stringdiff(affix1, affix2, positive, negative)
                positivelabel = ''.join(positive)
                negativelabel = ''.join(negative)
                self.differences2[(index1, index2)] = (positivelabel, negativelabel)

    def display(self):
        positive = []
        negative = []
        print
        'making table'
        print
        '\t',
        for affix in self.affixes:
            print
            affix, '\t',
        print

        for index1 in range(len(self.affixes)):
            affix1 = self.affixes[index1]
            print
            affix1, ':', '\t',
            for index2 in range(len(self.affixes)):
                affix2 = self.affixes[index2]
                print
                self.differences2[(index1, index2)][0], ':', self.differences2[(index1, index2)][1],
            print

    def displaytofile(self, outfile):
        positive = []
        negative = []
        print >> outfile, '      ',
        for affix in self.affixes:
            print >> outfile, '%18s' % affix,
        print >> outfile

        for index1 in range(len(self.affixes)):
            print >> outfile, '%10s' % self.affixes[index1],
            for index2 in range(len(self.affixes)):
                print >> outfile, '%12s %-6s' % (
                    self.differences2[(index1, index2)][0], self.differences2[(index1, index2)][1]),
            print >> outfile

    def minus(self, other):
        for index1 in range(0, len(affixes)):
            for index2 in range(0, len(affixes)):
                thispiece1 = self.affixes[index1]
                thispiece2 = self.affixes[index2]
                otherpiece1 = other.affixes[index1]
                otherpiece2 = other.affixes[index2]

                (thispositive, thisnegative) = self.differences2[(index1, index2)]
                (otherpositive, othernegative) = other.differences2[(index1, index2)]
                self.differences2[(index1, index2)] = DifferenceOfDifference((thispositive, thisnegative),
                                                                             (otherpositive, othernegative))

    def calculatesizeof2nddifference(self):
        numberofaffixes = len(affixes)
        difference = 0;
        for index1 in range(1, len(affixes)):
            for index2 in range(0, index1):
                (a, b) = self.differences2[(index1, index2)]
                difference += len(a) + len(b)
        return difference;

    def convert2nddifferencetostring(self):
        trans = str("")
        for index1 in range(0, len(affixes) - 1):
            for index2 in range(index1 + 1, len(affixes)):
                (a, b) = self.differences2[(index1, index2)]
                piece = "".join(a)
                if len(piece) == 0:
                    trans += "*"
                else:
                    trans += piece;
                trans += "-"
                piece = "".join(b)
                if len(piece) == 0:
                    trans += "*"
                else:
                    trans += piece;
                if index2 < len(affixes) - 1:
                    trans += " "
            trans += "/"
        return trans


##--------------------------------------------------------------------##
##		Main program
##--------------------------------------------------------------------##


# 1. Read in word list
language = 'english'
size = 46
infolder = r'../../data/english/'
infile = infolder + language + "_LRM_" + str(size) + "Kwords.txt"
outfolder = r'../../data/english/'
outfile = open(outfolder + language + "_ExtendedSignatures.txt", "w")

lexicon = {}
for line in open(infile):
    data = line.split()
    word = data[0]
    lexicon[word] = data[5]  # sorted string version of word



    # 2. Read in signature, maybe from console. Canonical order will be descending length where null counts as zero length, and alphabetized among equilength affixes.
affixes = Signature.split('.')

ThisSignaturesWords = {}

# 3. Put all the words that satisfy the signature in a list/dictionary.
WordsSatisfyingInitialSignature = {}

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

                # Find stems  in the intersection of all of these StemsFromAffixes sets.
StemsFromSig = {}
print >> outfile, 'finding regular stems now'
for stem in StemsFromAffixes[affixes[0]]:
    stembad = False
    for affix in affixes:
        if affix == 'NULL':
            affix = ''
        if affix == affixes[0]:
            continue
        elif not (stem in StemsFromAffixes[affix]):
            if affix == '':
                affix = 'NULL'
            # print >>outfile, stem, 'was not found in stem set for ', affix
            stembad = True
            break
    if stembad == False:
        StemsFromSig[stem] = 1

# print Signature
# print StemsFromSig.keys()

# Remove the words and stems that have already been discovered -- these were the totally regular cases.
print >> outfile, "Regular stems found."
for stem in StemsFromSig.keys():
    # print >>outfile, stem+affix
    for affix in affixes:
        if affix == 'NULL':
            affix = ''
        del lexicon[stem + affix]

for affixno in range(len(affixes)):
    # print affixno, affixes[affixno]
    for stem in StemsFromSig:
        if stem in StemsFromAffixes[affixes[affixno]]:
            del StemsFromAffixes[affixes[affixno]][stem]




            # Find sets of similar stems in the stem-sets of the different affixes: this time, variable number of stems.
MaxNumberOfStems = 3
MaxDiff = 1;  # MaxDiffBetweenStemAndClosestNeighbor = 3
seedaffixno = 0
stemset = []
SignatureSet = defaultdict(dict)  # for each affix, a dictionary of words that might form  its signature

PerfectSignatures = {}
print >> outfile, 'most general algorithm'
sortedstems = sorted(StemsFromAffixes[affixes[seedaffixno]])
for NumberOfStems in range(2, MaxNumberOfStems):
    # for Difference  in range( 1 ,  MaxDiff+1): #at presesnt this loop structure is not used. It is set up so that we can gently increase the permitted complexity across the stems within a signature.
    for Difference in range(1, 2):  # this is a placeholder statement (see line above)
        print >> outfile, "\n\n\n********  Maximum Difference permitted among stems: ", Difference, "\n\n"
        for stem in sortedstems:
            stemset = []
            ImplausibleWords = defaultdict(list)
            WordsSoFar = []
            SignatureSet.clear()
            if len(stem) < 2:
                continue
            print >> outfile
            print >> outfile, stem, '::::::'
            for affix in affixes:
                print >> outfile, '\t 1.', affix, ':'
                testforthisaffix = False
                if affix == affixes[seedaffixno]:
                    SignatureSet[affixes[seedaffixno]][stem + affix] = 1
                    WordsSoFar.append(stem + affix)
                    continue
                if affix == 'NULL':
                    affix = ''
                if stem in StemsFromAffixes[affix]:
                    print >> outfile, '\t\t 2.', stem, 'found the same stem as original.'
                    SignatureSet[affix][stem + affix] = 1
                    WordsSoFar.append(stem + affix)
                    testforthisaffix = True
                    continue
                for stem2 in StemsFromAffixes[affix].keys():
                    if len(stem2) < 2:
                        continue
                    # diff = Difference1(stem, stem2, Difference)
                    diff = Difference1(stem, stem2, MaxDiff)
                    # if diff <= Difference and diff >= Difference -1:
                    if diff <= MaxDiff:
                        if stem2 + affix in WordsSoFar:
                            ImplausibleWords[affix].append(stem2)
                        else:
                            testforthisaffix = True
                            SignatureSet[affix][stem2 + affix] = 1
                            stemset.append(stem2)
                            WordsSoFar.append(stem2 + affix)
                            print >> outfile, '\t\t 4. altered:\t', stem2, affix, ';'
                if testforthisaffix == False:
                    if affix == '':
                        affix = 'NULL'
                    print >> outfile, '\t\t 5. Could not find a form with suffix ', affix, ';'
                    continue
            if True:
                # print  "\n***  ",stem
                for affix in affixes:
                    # print affix,
                    if affix == 'NULL':
                        affix = ''
                        # for word in SignatureSet[affix]:
                        # print word,
                        # print ';'
                print >> outfile, "\n***  ", stem
                for affix in affixes:
                    print >> outfile, affix,
                    if affix == 'NULL':
                        affix = ''
                    if len(SignatureSet[affix]) == 0:
                        print >> outfile, '(none)',
                    else:
                        for word in SignatureSet[affix]:
                            print >> outfile, word,
                    if len(ImplausibleWords[affix]) > 0:
                        print >> outfile, "Implausible candidates:",
                        print >> outfile, ImplausibleWords[affix]
                        print >> outfile, ';'
                    print >> outfile
            signatureperfectflag = True
            for affix in affixes:
                if affix == 'NULL':
                    affix = ''
                if not (len(SignatureSet[affix]) == 1):
                    signatureperfectflag = False
                    break
            if signatureperfectflag == True:
                print >> outfile, "This signature is perfect."
                PerfectSignatures[stem] = WordsSoFar
                # print 'perfect signature', PerfectSignatures[stem]

##--------------------------------------------------------------------##
##      Keep only patterns with one word candidate per suffix         ##	

basictableau = intrasignaturetable()
basictableau.setsignature(Signature)
basictableau.displaytofile(outfile)

print >> outfile, "\n\nPerfect signatures: \n"

Signatures = {}
for stem in PerfectSignatures.keys():
    individualsignature = ".".join(PerfectSignatures[stem])

    tableau = intrasignaturetable()
    tableau.setsignature(individualsignature)
    tableau.display()
    tableau.displaytofile(outfile)
    print >> outfile, '\n'

    tableau.minus(basictableau)
    tableau.displaytofile(outfile)
    print >> outfile, '\n\n'

    linearization = tableau.convert2nddifferencetostring()
    print >> outfile, linearization
    if not Signatures.has_key(linearization):
        Signatures[linearization] = []
    Signatures[linearization].append(stem)
    print >> outfile, stem, Signatures[linearization]
ThresholdForPlausibleEvidence = 5
##--------------------------------------------------------------------##
##		Retain only common signature patterns		      ##		
print >> outfile, "-----------------------------------------------------------"
print >> outfile, "-----------------------------------------------------------"
print >> outfile, "   Patterns discovered  "
print >> outfile, "-----------------------------------------------------------"
count = 1
for encoding in Signatures.keys():
    if len(Signatures[encoding]) < ThresholdForPlausibleEvidence:
        continue;
    print >> outfile, "-----------------------------------------------------------"
    print >> outfile, count, ".  Stems found: ", Signatures[encoding]
    stem = Signatures[encoding][0]
    individualsignature = ".".join(PerfectSignatures[stem])
    tableau = intrasignaturetable()
    tableau.setsignature(individualsignature)
    tableau.display()
    tableau.displaytofile(outfile)
    print >> outfile, '\n'
    count += 1
