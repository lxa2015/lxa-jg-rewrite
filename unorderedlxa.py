# Read in an LMR file
import operator
import time

# ---------------------------------------------------------#
language = "english"
infolder = "../../data/"
size = 46
infolder = infolder + language
extraname = ""
infilename = infolder + "/english1K-stringintersection.txt"
# infilename = infolder + language + "/" + extraname + str(size) + "K-stringintersection.txt"
infile = open(infilename)
# ---------------------------------------------------------#
outfolder = infolder
outfilename = outfolder + language + str(size) + "groupings.lxa"
outfile = open(outfilename, "w")
# ----------------------------------------------------------#

wordlist = []
piece2dict = {}
for line in infile:
    pieces = line.split()
    word1 = pieces[0]
    word2 = pieces[1]
    numbershared = int(pieces[2])
    number1 = int(pieces[3])
    number2 = int(pieces[4])
    shared = pieces[5]
    only1 = pieces[6]
    only2 = pieces[7]
    # print number1,
    wordlist.append(word1)
    if number1 + number2 < 3:
        # print only2,
        if only1 in piece2dict:
            piece2dict[only1] += 1
        else:
            piece2dict[only1] = 1

suffixes = sorted(piece2dict.iteritems(), key=operator.itemgetter(1))
suffixes.reverse()
print
suffixes

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
