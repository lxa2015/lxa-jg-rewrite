import math

# -------------------------------------------------------------------------
#	Establish names of files, both in and out
# --------------------------------------------------------------------------
numberofKwords = 48
numberofwords = numberofKwords * 1000
language = "browncorpus"
infolder = r'../../data/english/'
outfolder = r'../../data/english/'
countthreshold = 500

outfilename = outfolder + language + "_CountProfile_" + str(numberofKwords) + "Kwords.txt"
outfile = open(outfilename, "w")

infilename = infolder + language + "_LRM_" + str(numberofKwords) + "Kwords.txt"
wholefile = open(infilename)
filelines = wholefile.readlines()

UpX = []
DownX = []
UpY = []
DownY = []
wordlist = []
wordcounts = {}
inline = []
for line in filelines:
    line = line.strip()
    inline = line.split(' ')
    word = inline[0]
    x1 = float(inline[1])
    x2 = float(inline[2])
    y1 = float(inline[3])
    y2 = float(inline[4])
    count = int(inline[6])
    if count < countthreshold:
        continue
    wordlist.append(word)
    wordcounts[word] = int(count)
    t = (x1, count, word)
    # UpX.append( (x1,count, word) )
    UpX.append(t)
    td = (x2, count, word)
    # DownX.append( (x2,count, word) )
    DownX.append(td)
    print
    word, x1, x2, count

## We have made two lists, UpX and DownX. Each is a pair (coord, count). The Up-coor is the lower coordinate of a word's compression interval, the Down-coor is the upper-coordinate. By construction, UpX is sorted, but DownX is not, so we must sort it now. Profile is constructed by moving along the two lists, Up and Down, and keeping a count of where we are at any particular point (all the up's minus all the down's so far). Same for Y.

print
"upx"
for item in UpX:
    print
    item

DownX.sort(key=lambda chunk: chunk[0])

print
"DownX"
for item in DownX:
    print
    item

Xprofile = []
Xprofile.append((0, 0, "NULL"))
currentitem = UpX.pop(0)
currentlocation = currentitem[0]
currentcount = currentitem[1]
Xprofile.append((currentlocation, currentcount, currentitem[2]))

overallcount = currentcount
nextUp = UpX.pop(0)
nextDown = DownX.pop(0)
while (len(UpX) > 0 and len(DownX) > 0):
    if (nextUp[0] < nextDown[0]):
        currentlocation = nextUp[0]
        overallcount += nextUp[1]
        word = nextUp[2]
        print
        "up", nextUp[1], overallcount, nextUp[2]
        Xprofile.append((currentlocation, overallcount, word))
        nextUp = UpX.pop(0)
    else:
        currentlocation = nextDown[0]
        overallcount -= nextDown[1]
        print
        "down", nextDown[1], overallcount, nextDown[2]
        word = nextDown[2]
        Xprofile.append((currentlocation, overallcount, word))
        nextDown = DownX.pop(0)

lastcoord = 0
lastlogcount = 0
lastword = "!!!"
for coord, count, word in Xprofile:
    if count <= 0:
        count = 1
    logcount = math.log(count)
    print >> outfile, coord, lastlogcount
    print >> outfile, coord, logcount
    print
    word
    lastlogcount = logcount
    lastcoord = coord
    lastword = word
