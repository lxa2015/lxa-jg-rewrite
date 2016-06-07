import os
import sys

g_encoding = "asci"  # "utf8"
# --------------------------------------------------------------------##
#		Main program 
# --------------------------------------------------------------------##

language = "medline"
infolder = '../../data/' + language + '/'

size = 100  # french 153 10 english 14 46

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
outfilename = outfolder + language + "_" + str(size) + "Kwords" + "_weightyNgrams.txt"
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
    #	word = word[:-1] # for french only?
    word = word.lower()
    if (len(pieces) > 1):
        WordCounts[word] = int(pieces[1])
    else:
        WordCounts[word] = 1

wordlist = WordCounts.keys()
wordlist.sort()

# ----------------------------------------------------------#
maxlength = 15
ngrams = {}
for word in wordlist:
    for l in range(1, maxlength + 1):
        for n in range(len(word)):
            if n + l > len(word):
                continue
            piece = word[n:n + l]
            if not piece in ngrams:
                ngrams[piece] = l * WordCounts[word]
            else:
                ngrams[piece] += l * WordCounts[word]

pieces = sorted(ngrams, key=ngrams.get, reverse=True)  # sort by value
for piece in pieces:
    if ngrams[piece] < 1000:
        continue
    print
    piece, ngrams[piece]
    print >> outfile, piece, ngrams[piece]
