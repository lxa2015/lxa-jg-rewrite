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

import codecs  # for utf8
import os
import sys
import time

g_encoding = "asci"  # "utf8"
DiffType = "suffixal"  # could also be "unordered" and eventually "prefixal", though the latter, not yet

MinimumStemLength = 5
MaximumAffixLength = 3  # was 7
# MinimumStemCount = 4
MinimumNumberofSigUses = 10


# Signatures is a map: its keys are signatures. Its values are *sets* of stems.
# StemToWord is a map; its keys are stems.      Its values are *sets* of words.
# StemToSig is a map; its keys are stems.       Its values are individual signatures.
# WordToSig is a Map. its keys are words.       Its values are *lists* of signatures.
# StemCounts is a map. Its keys are words. 	Its values are corpus counts of stems.




# ---------------------------------------------------------#
def makesortedstring(string):
    letters = list(string)
    letters.sort()
    return letters


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
    for i in range(0, howfar, 1):
        if not a[alen - i - 1] == b[blen - i - 1]:
            startingpoint = alen - i
            return a[alen - i:]
    return a[howfar:]


# ---------------------------------------------------------#
def DeltaLeft(a,
              b):  # Returns a pair of strings, consisting of prefixes of a and b, up to the maximal common suffix that a and b share.
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar - 1, 0, -1):
        if not a[i] == b[i]:
            return (a[:i], b[:i])
    return (a[:howfar], b[:howfar])


# ---------------------------------------------------------#
def DifferenceOfDifference((X1, X2), (Y1, Y2)):
    # if DiffType == "suffixal"

    if DiffType == "unordered" or DiffType == "suffixal":
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
    r1 = ''.join(r1)
    r2 = ''.join(r2)
    return (r1, r2)


# ---------------------------------------------------------#
def DeltaRight(a,
               b):  # Returns a pair of strings, consisting of the suffixes of each string following any maximal common prefix that may exist.
    howfar = len(a)
    if len(b) < howfar:
        howfar = len(b)
    for i in range(howfar):
        if not a[i] == b[i]:
            return (a[i:], b[i:])
    return (a[howfar:], b[howfar:])


# ---------------------------------------------------------#
def makesignature(a):
    delimiter = '.'
    sig = ""
    for i in range(len(a) - 1):
        if len(a[i]) == 0:
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
def stringdiff(instring1, instring2):
    if instring1 == 'NULL':
        instring1 = ''
    if instring2 == 'NULL':
        instring2 = ''
    # ---------------------------#
    # this function can look for suffixal differences, prefixal differences, or unordered string differences
    # ---------------------------#
    DiffType = "suffixal"

    if DiffType == "suffixal":
        # this returns a pair of lists, which give the differences of the ends of instring1 and instring2
        positive, negative = DeltaRight(instring1, instring2)
        # print "stringdiff: ", instring1,':', instring2,':', positive,':', negative
        return (positive, negative)
    elif DiffType == "unordered":
        string1 = makesortedstring(instring1)
        # print string1
        string2 = makesortedstring(instring2)
        i = 0
        j = 0
        del positive[:]
        del negative[:]
        while (True):
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
            elif i == len(string1) and j == len(string2):
                for k2 in range(j, len(string2)):
                    negative.append(string2[k2])
                for k1 in range(i, len(string1)):
                    positive.append(string1[k1])
                break
            elif (i >= len(string1)):
                for k2 in range(j, len(string2)):
                    negative.append(string2[k2])
                break
            elif (j >= len(string2)):
                for k1 in range(i, len(string1)):
                    positive.append(string1[k1])
                break
    positive = ''.join(positive)
    negative = ''.join(negative)
    return (positive, negative)


# ---------------------------------------------------------#
class intrasignaturetable:
    def setsignature(self, sig):
        self.affixes = sig.split('-')
        self.affixlabels = {}
        for affix in self.affixes:
            self.affixlabels[affix] = affix
            if affix == 'NULL':
                affix = ''
        self.differences = {}
        positive = []
        negative = []
        for affix1 in self.affixes:
            for affix2 in self.affixes:
                (positive, negative) = stringdiff(affix1, affix2)
                self.differences[(affix1, affix2)] = (positive, negative)

    def compress(self):
        print
        "sig", self.affixes, self.differences
        pairInventory = {}
        costPerLetter = 5
        costForNull = 1
        TotalCost = 0
        print
        for pair in self.differences:
            (positive, negative) = self.differences[pair]
            pairString = ''.join(positive) + ':' + ''.join(negative)
            # print "pairString", pairString
            if not pairString in pairInventory:
                pairInventory[pairString] = 1
            # print "new pair: ", pairString, len(positive), len(negative)
            else:
                pairInventory[pairString] += 1
        for pair in pairInventory:
            print
            pair
            pieces = pair.split(':')
            affix1 = pieces[0]
            affix2 = pieces[1]
            if len(affix1) == 0 and len(affix2) == 0:
                costA = 0
                costB = 0
            # print "both null"
            else:
                if len(affix1) == 0:
                    costA = costForNull
                else:
                    costA = len(affix1) * costPerLetter
                if len(affix2) == 0:
                    costB = costForNull
                else:
                    costB = len(affix2) * costPerLetter
                TotalCost += (costA + costB) + (pairInventory[pair] - 1)  # we pay the "full price" for the first pair,
                # and each additional occurrence costs just one bit.
            print
            costA, costB

            print
            TotalCost
        print
        TotalCost
        return (TotalCost, pairInventory)

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

        for affix1 in self.affixes:
            print
            affix1, ':', '\t',
            for affix2 in self.affixes:
                print
                self.differences[(affix1, affix2)][0], ':', self.differences[(affix1, affix2)][1],
            print

    def changeAffixLabel(self, before, after):
        for n in range(len(self.affixes)):
            if self.affixes[n] == before:
                self.affixlabels[before] = after
                return
        return

    def displaytofile(self, outfile):
        positive = []
        negative = []

        for affix in self.affixes:
            print >> outfile, '%18s' % self.affixlabels[affix],
        print >> outfile

        for affix1 in self.affixes:
            print >> outfile, '%10s' % self.affixlabels[affix1],
            for affix2 in self.affixes:
                # print "display to file, suffixes", affix1, affix2
                item = self.differences[(affix1, affix2)]
                print >> outfile, '[%4s]:[%-4s]    ' % (item[0], item[1]),
            print >> outfile
        TotalCost, pairInventory = self.compress()
        print >> outfile, "Compressed form: ", TotalCost
        return TotalCost

    def minus(self, other):
        counterpart = {}
        (alignedAffixList1, alignedAffixList2) = FindBestAlignment(self.affixes, other.affixes)
        for i in range(len(alignedAffixList1)):
            counterpart[alignedAffixList1[i]] = alignedAffixList2[i]
        for index1 in range(len(alignedAffixList1)):
            for index2 in range(len(alignedAffixList2)):
                thispiece1 = alignedAffixList1[index1]
                thispiece2 = alignedAffixList1[index2]
                otherpiece1 = alignedAffixList2[index1]
                otherpiece2 = alignedAffixList2[index2]
                (thispositive, thisnegative) = self.differences[(thispiece1, thispiece2)]
                (otherpositive, othernegative) = other.differences[(otherpiece1, otherpiece2)]
                self.differences[(thispiece1, thispiece2)] = DifferenceOfDifference((thispositive, thisnegative),
                                                                                    (otherpositive, othernegative))

        # get rid of rows corresponding to unmatched affixes
        affixlistcopy = list(self.affixes)
        for affix1 in affixlistcopy:
            if not affix1 in alignedAffixList1:
                for affix2 in other.affixes:
                    if (affix1, affix2) in self.differences:
                        del self.differences[(affix1, affix2)]
                self.affixes.remove(affix1)
        for affix in self.affixes:
            self.changeAffixLabel(affix, str(affix + ":" + counterpart[affix]))
        return


# ---------------------------------------------------------#
# def Expansion(sig,stem):
#	wordset = set()
#	affixlist = sig.split('-')
#	for affix in affixlist:
#		if affix == 'NULL':
#			affix = ''
#		wordset.add(stem + affix)
#	return wordset
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


# ---------------------------------------------------------#
def RemoveNULL(list1):
    for item in list1:
        if item == "NULL":
            item = ""
    return list1


# ---------------------------------------------------------#
def StringDifference(str1, str2):
    if str1 == "NULL":
        str1 = ""
    if str2 == "NULL":
        str2 = ""
    list1 = list(str1)
    list2 = list(str2)
    list1.sort()
    list2.sort()
    m = 0
    n = 0
    overlap = 0
    difference = 0
    while (True):
        if m == len(str1) and n == len(str2):
            return (overlap, difference)
        if m == len(str1):
            difference += len(str2) - n
            return (overlap, difference)
        if n == len(str2):
            difference += len(str1) - m
            return (overlap, difference)

        if list1[m] == list2[n]:
            overlap += 1
            m += 1
            n += 1
        elif list1[m] < list2[n]:
            m += 1
            difference += 1
        elif list2[n] < list1[m]:
            n += 1
            difference += 1


# ----------------------------------------------------------------------------------------------------------------------------#
def SignatureDifference(sig1,
                        sig2):  # this finds the best alignments between affixes of a signature, and also gives a measure of the similarity.
    list1 = list(sig1.split('-'))
    list1.sort()
    list2 = list(sig2.split('-'))
    list2.sort()
    if (len(list1) > len(list2)):
        temp = list1
        list1 = list2
        list2 = temp  # now list2 is the longer one, if they differ in length
    differences = {}
    list3 = []
    Alignments = []
    # print >>outfile,  "---------------------------------------\n"
    # print >>outfile, "---------------------------------------\n",sig1, sig2, "** SignatureDifference **\n"
    for m in list1:
        differences[m] = {}
        # print >>outfile, '%8s ' % m, ":",
        for n in list2:
            o, d = StringDifference(m, n)
            differences[m][n] = o - d
            # print >>outfile, '%2s %2d;' % (n, o-d),
            # print >>outfile

    GoodAlignmentCount = 0
    TotalScore = 0
    for loopno in range(len(list1)):
        # print >>outfile, "-----------------------------\n"
        # print >>outfile, "loop no: ", loopno
        # for m in differences.keys():
        # print >>outfile, '%8s : ' % (m),
        # for n in differences[m].keys():
        # print >>outfile, '%2s %2d;' % (n, differences[m][n]),
        # print >>outfile
        # print >>outfile

        list3 = []
        for m in differences.keys():
            for n in differences[m].keys():
                list3.append(differences[m][n])
        list3.sort(reverse=True)

        bestvalue = list3[0]
        if bestvalue >= 0:
            GoodAlignmentCount += 1
        breakflag = False
        for m in differences.keys():
            for n in differences[m].keys():
                if differences[m][n] == bestvalue:
                    winner = (m, n)
                    # print >>outfile, "winner:", m, n, "closeness: ", bestvalue
                    breakflag = "True"
                    break
            if breakflag:
                break;

        Alignments.append((m, n, bestvalue))
        TotalScore += bestvalue
        del differences[winner[0]]
        for p in differences.keys():
            del differences[p][winner[1]]
            # print >>outfile, "Final affix alignments: "
            # for item in Alignments:
            # print >>outfile, "\t%7s %7s %7d" % ( item[0], item[1], item[2] )
    # For scoring: we count a pairing as OK if its alignment is non-negative, and we give extra credit if there are more than 2 pairings
    if GoodAlignmentCount > 2:
        TotalScore += GoodAlignmentCount - 2
    # print >>outfile, "Total score: ", TotalScore, "\n\n"
    return TotalScore


# ----------------------------------------------------------------------------------------------------------------------------#
def FindBestAlignment(list1, list2):  # this is very similar to SignatureDifference...
    AlignedList1 = []
    AlignedList2 = []
    reversedFlag = False
    if (len(list1) > len(list2)):
        temp = list1
        list1 = list2
        list2 = temp  # now list2 is the longer one, if they differ in length
        reversedFlag = True
    differences = {}
    list3 = []
    Alignments = []
    # print >>outfile,  "---------------------------------------\n"
    # print >>outfile, "---------------------------------------\n",list1, list2, "** Find Best Alignment **\n"
    for m in list1:
        differences[m] = {}
        # print >>outfile, '%8s ' % m, ":",
        for n in list2:
            o, d = StringDifference(m, n)
            differences[m][n] = o - d
            # print >>outfile, '%2s %2d;' % (n, o-d),
            # print >>outfile
    GoodAlignmentCount = 0
    TotalScore = 0
    for loopno in range(len(list1)):
        # print >>outfile, "-----------------------------\n"
        # print >>outfile, "loop ", loopno,
        # for m in differences.keys():
        # print >>outfile, '%8s : ' % (m),
        # for n in differences[m].keys():
        # print >>outfile, '%2s %2d;' % (n, differences[m][n]),
        # print >>outfile
        # print >>outfile

        list3 = []
        for m in differences.keys():
            for n in differences[m].keys():
                list3.append(differences[m][n])
        list3.sort(reverse=True)

        bestvalue = list3[0]
        if bestvalue >= 0:
            GoodAlignmentCount += 1
        breakflag = False
        for m in differences.keys():
            for n in differences[m].keys():
                if differences[m][n] == bestvalue:
                    winner = (m, n)
                    # print >>outfile, "winner: %8s %8s closeness: %2d" %( m, n, bestvalue)
                    breakflag = "True"
                    break
            if breakflag:
                break;
        AlignedList1.append(m)
        AlignedList2.append(n)
        del differences[winner[0]]
        for p in differences.keys():
            del differences[p][winner[1]]
            # print >>outfile,  "---------------------------------------\n"
            # print >>outfile, "Final affix alignments: "
            # for n in range(len(AlignedList1)):
            # print >>outfile, "\t%7s %7s " % ( AlignedList1[n], AlignedList2[n]  )
    if reversedFlag:
        return (AlignedList2, AlignedList1)
    return (AlignedList1, AlignedList2)


# ----------------------------------------------------------------------------------------------------------------------------#
def AverageCountOfTopStems(howmany, sig, Signatures, StemCounts):
    stemlist = list(Signatures[sig])
    countlist = []
    count = 0
    average = 0
    print
    "sig: ", sig
    for stem in stemlist:
        print
        stem
        countlist.append(StemCounts[stem])
    countlist = sorted(countlist, reverse=True)
    if len(countlist) < howmany:
        howmany = len(countlist)
    for n in range(howmany):
        average += countlist[n]
    average = average / howmany
    return average


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
    reversedstemlist = []
    count = 0
    print >> outfile, "***\n *** Stems in each signature"
    for sig, stemcount, robustness in DisplayList:
        if g_encoding == "utf8":
            print >> outfile, "\n=============================================\n", sig, "\n"
        else:
            print >> outfile, "\n=============================================\n", '{0:30s} \n'.format(sig)
        n = 0
        stemlist = Signatures[sig]
        reversedstemlist = []
        for stem in Signatures[sig]:
            reversedstemlist.append(stem[::-1])
        reversedstemlist = sorted(reversedstemlist)
        numberofstems = len(reversedstemlist)
        for stem in reversedstemlist:
            n += 1
            print >> outfile, '{0:12s}'.format(stem),
            if n == numberofstemsperline:
                n = 0
                print >> outfile

                # print the average count of the Top 5 most frequent stems
        print >> outfile, "\n-------------------------"
        print >> outfile, "Average count of top 5 stems:", AverageCountOfTopStems(5, sig, Signatures, StemCounts)

        print >> outfile, "\n", "High frequency stem finals\nNumber of stems: ", len(stemlist)
        formatstring = '%10s    weight: %5d count: %5d %2s'
        finalchunklist = find_N_highest_weight_suffix(stemlist)
        for item in finalchunklist:
            if item[2] >= numberofstems * 0.9:
                flag = "**"
            else:
                flag = ""
            print >> outfile, formatstring % (item[0][::-1], item[1], item[2], flag)

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
            print >> outfile, '{0:<30}{1}'.format(word[::-1], WordToSig[word])
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
        if not newstem in StemCounts.keys():
            StemCounts[newstem] = StemCounts[stem]
        else:
            StemCounts[newstem] += StemCounts[stem]
        del StemCounts[stem]
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
def find_N_highest_weight_suffix(wordlist):
    # ----------------------------------------------------------------------------------------------------------------------------#

    maximalchunksize = 9  # should be 3 or 4 ***********************************
    totalweight = 0
    threshold = 50
    weightthreshold = 0.02
    permittedexceptions = 2
    MinimalCount = 10
    chunkcounts = {}
    chunkweights = {}
    chunkweightlist = []
    chunkweights = {}
    tempdict = {}
    templist = []
    for word in wordlist:
        totalweight += len(word)

    for word in wordlist:
        for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the suffix being considered
            chunk = word[-1 * width:]
            if not chunk in chunkcounts.keys():
                chunkcounts[chunk] = 1
            else:
                chunkcounts[chunk] += 1
    for chunk in chunkcounts.keys():
        chunkweights[chunk] = chunkcounts[chunk] * len(chunk)
        if chunkweights[chunk] < weightthreshold * totalweight:
            continue
        if chunkcounts[chunk] < MinimalCount:
            continue
        tempdict[chunk] = chunkweights[chunk]

    templist = sorted(tempdict.items(), key=lambda chunk: chunk[1], reverse=True)
    for stem, weight in templist:
        chunkweightlist.append((stem, weight, chunkcounts[stem]))

    # ----------------------------------------------------------------------------------------------------------------------------#
    return chunkweightlist


# ----------------------------------------------------------------------------------------------------------------------------#



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
            n, word1[::-1]
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
    # StemToSig is a Map. Its keys are stems.	Its values are individual signatures.
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
                affix = word[stemlength:]
                affixset.add(affix[::-1])
        affixlist = list(affixset)
        affixlist.sort()
        thissig = "-".join(affixlist)
        # print >>outfile, thissig
        if not thissig in Signatures:
            Signatures[thissig] = set()
        Signatures[thissig].add(stem)
        StemToSig[stem] = thissig
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

language = "swahili"
infolder = '../../data/' + language + '/'

size = 43  #

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
outfilename = outfolder + language + "_" + str(size) + "Kwords" + "_extendedsigs.txt"
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
    word = word[::-1]  # to reverse order of all the words!!!!!
    # word = word[:-1] # for french only?
    word = word.lower()
    if (len(pieces) > 1):
        WordCounts[word] = int(pieces[1])
    else:
        WordCounts[word] = 1

wordlist = WordCounts.keys()
wordlist.sort()
# --------------------------------------------------#


# --------------------------------------------------#
# 		Main part of program		   #
# --------------------------------------------------#
SigToTuple = {}  # key: bisig     value: ( stem, word1, word2, bisig )
Signatures = {}
WordToSig = {}
StemToWord = {}
StemCounts = {}
numberofwords = len(wordlist)
stemfilename = infolder + language + "_" + str(size) + "Kwords_stems" + ".txt"
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
            StemToWord[stem].add(pieces[i])
else:
    print
    "stem file not found"
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
#	Make signatures, and WordToSig dictionary, and Signature dictionary-of-stem-lists, and StemToSig dictionary
# -----------------------------------------------------------------------------------------------------------------#
print
"Make signatures"
StemToWord, Signatures, WordToSig, StemToSig = MakeSignatures(StemToWord)
printSignatures(Signatures, WordToSig, outfile)

print
"Calculating signature differences"
for m in range(10):
    for n in range(10):
        sig1 = Signatures.keys()[m]
        sig2 = Signatures.keys()[n]
        if sig1 == sig2:
            continue
        diff = SignatureDifference(sig1, sig2)
        # if diff > 0:
        # print sig1, sig2, diff

print
"End of Calculating signature differences"

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
    # ------------------- remove this:
    continue
    # -------------------------------

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
MaximalLettersToShift = 1  ######################################## note that this is now 1
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
NumberOfCorrections = 0
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
    print
    loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
    sig_target = bestsigtochange
    if len(shift) == 1:
        print
        "best chunk is 1 letter"
        StemToWord, Signatures = ShiftSignature(sig_target, shift, StemToWord, Signatures, outfile)
    if len(shift) > 1:
        print
        "best chunk is big: "
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
"Deal with pairs of stems of adjacent lengths in distinct signatures"
# --------------------------------------------------#
# We consider each signature's stems, and ask for each stem t, whether t without its final letter is also a stem 
# in some other signature. We are looking for cases where two such stems *explain the same words*.
# If there are enough stem-pairs like that, we go ahead and try to explain those pairings
# as multi-stem (i.e., allomorphy) patterns.

StemCountThreshold = 5
StemProportionThreshold = .9
print >> outfile, "\n\n*** Pairs of stems of adjacent lengths"

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
            if len(overlapwordset) > 1:
                sig2 = StemToSig[stem2]
                print >> outfile, "<", sig, ": ", sig2, ">\n\t", stem[::-1], stem2[::-1], overlapwordset
                pattern = finalletter + "=" + sig + "=" + sig2
                if not pattern in BiSigPatterns.keys():
                    BiSigPatterns[pattern] = 1
                else:
                    BiSigPatterns[pattern] += 1

print
"End of dealing with multiple sigs for stems"

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
print >> outfile, "End of dealing with signatures with multiple stems"
print >> outfile, "-------------------------------------------------------"
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
# --------------------------------------------------#
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
    # print "sig1", sig1
    for sig2, numberofstems2, robustness2 in DisplayList:
        if numberofstems2 < minimumstemcount:
            continue
        if sig1 == sig2:
            continue
        if not sig1.count('-') == sig2.count('-'):
            continue
        # print "sig2", sig2
        print >> outfile, "\n\n---------------------------------\n\t", "sig 2: ", sig2
        tableau2 = intrasignaturetable()
        tableau2.setsignature(sig2)
        tableau2.minus(tableau1)
        print >> outfile, "Difference of tableaux:"
        compressedSize = tableau2.displaytofile(outfile)
        # print compressedSize
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

outfile.close()
print
outfilename

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
