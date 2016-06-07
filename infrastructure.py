# -*- coding: <utf-16> -*- 
unicode = True
from lxa_module import *


def ReadDx1(filename)
    g_encoding = "asci"  # "utf8"
    infolder = '../../data/' + language + '/'
    infilename = infolder + smallfilename + "_" + "Kwords" + ".dx1"

    if not os.path.isfile(infilename):
        print
        "Warning: ", infilename, " does not exist."
    if g_encoding == "utf8":
        infile = codecs.open(infilename, g_encoding='utf-8')
    else:
        infile = open(infilename)
    print
    "Data file: ", infilename
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
