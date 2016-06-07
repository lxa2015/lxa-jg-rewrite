# Read in an LMR file
import time


def finddiff(a, b):
    # print a,b
    positive = []
    negative = []
    shared = []
    i = j = 0
    while (True):

        if i >= len(a) or j >= len(b):
            # print "break", i , j
            break;
        # print "i", i, "j", j, "a-i", a[i], "b-j", b[j]
        if a[i] == b[j]:
            shared.append(a[i])
            # print "shared" , a[i]
            i += 1
            j += 1
        elif a[i] < b[j]:
            positive.append(a[i])
            i += 1
        # print "to positive"
        elif a[i] > b[j]:
            negative.append(b[j])
            j += 1
            # print "new j" , j
            # print "to negative"
    if i < len(a):
        # print "left overs in first",
        for k in range(i, len(a)):
            # print a[k],
            positive.append(a[k])
            # print
    if j < len(b):
        # print "leftovers in second",
        for k in range(j, len(b)):
            # print b[k],
            negative.append(b[k])
            # print

    shared.sort()
    positive.sort()
    negative.sort()
    return (shared, positive, negative)


# ---------------------------------------------------------#
infolder = "../../data/english/"
language = "english"
size = 1
extension = ".txt"
infilename = infolder + language + "_LRM_" + str(size) + "Kwords.txt"
# ---------------------------------------------------------#
outfolder = infolder
outfilename = outfolder + language + str(size) + "K-stringintersection.txt"
outfile = open(outfilename, "w")
wholefile = open(infilename)
# ----------------------------------------------------------#

filelines = wholefile.readlines()

anagrams = {}
for line in filelines:
    pieces = line.split(' ')
    word = pieces[0]
    anagram = pieces[5]
    anagrams[word] = anagram

wordlist = anagrams.keys()
wordlist.sort()
wordlist2 = wordlist

for word in wordlist:
    print
    word
    for word2 in wordlist2:
        if word == word2:
            continue
        # print word2
        (shared, positive, negative) = finddiff(anagrams[word], anagrams[word2])
        if len(positive) < 4 and len(negative) < 4 and len(shared) > 3:
            # print word, word2, shared
            print >> outfile, word.ljust(20), word2.ljust(20), len(shared), len(positive), len(negative), ''.join(
                shared).ljust(20),
            if len(positive) == 0:
                positive.append("@")
            if len(negative) == 0:
                negative.append("@")
            print >> outfile, ''.join(positive).ljust(20), ''.join(negative).ljust(20)

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
