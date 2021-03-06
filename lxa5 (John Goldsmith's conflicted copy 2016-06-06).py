# -*- coding: <utf-16> -*- 
unicode = True

# This program looks for extended signatures, which are regular subgraphs among words, where the edges are
# (high-freq) Delta-Right pairs of words, and where a word may be *split differently* (without penalty!) 
# in different Delta-Right pairs: e.g., "moves" is part of the pair (move/move-s) and also of the pair
# (mov-es/mov-ing).
# 	Prototyping for bootstrapping of Lxa5
# 	Accepts name of input file as command-line argument.
# --------------------------------------------------------------------##
#		Main program begins on line 174
# --------------------------------------------------------------------##

from lxa_module import *

# --------------------------------------------------------------------##
#		user modified variables
# --------------------------------------------------------------------##




NumberOfCorrections = 10
g_encoding = "asci"  # "utf8"
# g_encoding =   "utf-8"

MaximumAffixLength = 5
BreakAtHyphensFlag = True

# ----------------- command line parameters ------------------------------#


language = "english"
# language="english-encarta"
# language="swahili"

print("language", language)
# -----------------------------------------------------------------------#




# -----------------------------------------------------------------------#


FindSuffixesFlag = True

numberofwords = 1000

datafolder = "../../data/" + language + "/"
outfolder = datafolder + "lxa/"
infolder = datafolder + 'dx1/'

# shortfilename = "english-encarta"
shortfilename = "browncorpus"
# shortfilename="swahili"


infilename = infolder + shortfilename + ".dx1"
stemfilename = infolder + shortfilename + "_stems.txt"
outfile_Signatures_name = outfolder + shortfilename + "_Signatures.txt"
outfile_SigTransforms_name = outfolder + shortfilename + "_sigtransforms.txt"
outfile_signature_exemplar_name = outfolder + shortfilename + "_signature_exemplars.txt"
outfile_stemtowords_name = outfolder + shortfilename + "_stemtowords.txt"
outfile_FSA_graphics_name = outfolder + shortfilename + "_FSA_graphics.png"
outfile_FSA_name = outfolder + shortfilename + "_FSA.txt"
outfile_log_name = outfolder + shortfilename + "_log.txt"
outfile_WordToSig_name = outfolder + shortfilename + "_WordToSig.txt"
outfile_wordparses_name = outfolder + shortfilename + "_WordParses.txt"
outfile_wordlist_name = outfolder + shortfilename + "_WordList.txt"

print
"Reading dx file: ", infilename

lxalogfile = open(outfile_log_name, "w")
print
"Logging to ", outfile_log_name
print
"Data file: ", infilename

if len(sys.argv) > 1:
    print
    sys.argv[1]
    infilename = sys.argv[1]
if not os.path.isfile(infilename):
    print
    "Warning: ", infilename, " does not exist."
if g_encoding == "utf8":
    infile = codecs.open(infilename, g_encoding='utf-8')
else:
    infile = open(infilename)

# ----------------------------------------------------------#



if g_encoding == "utf8":
    print
    "yes utf8"
else:
    Signatures_outfile = open(outfile_Signatures_name, mode='w')

outfile_Signatures = open(outfile_Signatures_name, "w")
outfile_FSA = open(outfile_FSA_name, "w")
outfile_SigExemplars = open(outfile_signature_exemplar_name, "w")
outfile_WordToSig = open(outfile_WordToSig_name, "w")
outfile_SigTransforms = open(outfile_SigTransforms_name, "w")
outfile_StemToWords = open(outfile_stemtowords_name, "w")
outfile_WordParses = open(outfile_wordparses_name, "w")
outfile_WordList = open(outfile_wordlist_name, "w")

# -------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------#
# 					Main part of program		   			   	#
# -------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------#


# This is just part of documentation:
# A signature is a tuple of strings (each an affix).
# Signatures is a map: its keys are signatures.  Its values are *sets* of stems.
# StemToWord is a map; its keys are stems.       Its values are *sets* of words.
# StemToSig  is a map; its keys are stems.       Its values are individual signatures.
# WordToSig  is a Map. its keys are words.       Its values are *lists* of signatures.
# StemCounts is a map. Its keys are words. 	 Its values are corpus counts of stems.
# SignatureToStems is a dict: its keys are tuples of strings, and its values are dicts of stems. We don't need both this and Signatures!

print
"148"

Lexicon = CLexicon()

# --------------------------------------------------------------------##
#		read wordlist (dx1)
# --------------------------------------------------------------------##

filelines = infile.readlines()
WordCounts = dict()

for line in filelines:
    pieces = line.split()
    word = pieces[0]
    if word == '#':
        continue
    if len(word) == 0:
        continue
    word = word.lower()
    if (BreakAtHyphensFlag and '-' in word):
        words = word.split('-')
        for word in words:
            if len(word) == 0:
                continue
            if word not in WordCounts:
                WordCounts[word] = 0
            WordCounts[word] += 1
            Lexicon.TotalLetterCountInWords += len(word)
    else:
        if word not in WordCounts:
            WordCounts[word] = 0
        WordCounts[word] += 1
        Lexicon.TotalLetterCountInWords += len(word)
    if len(WordCounts) >= numberofwords:
        break
print
Lexicon.TotalLetterCountInWords
for word in WordCounts:
    Lexicon.WordList.AddWord(word)
print
"about to sort"
Lexicon.WordList.sort()
print
"in main program"
Lexicon.PrintWordList(outfile_WordList)

print
"{:40s}{:>10,}".format("Total words: ", len(Lexicon.WordList.mylist))
print
"{:40s}{:>10,d}".format("Total letter count in words: ", Lexicon.TotalLetterCountInWords)
print
"{:40s}{:>10,d}".format("average letters per word: ", Lexicon.TotalLetterCountInWords / len(Lexicon.WordList.mylist))

print >> outfile_Signatures, "# ", language, numberofwords

print >> lxalogfile, "{:40s}{:15s}".format("Language: ", language)
print >> lxalogfile, "{:40s}{:>10,}{:15s}{:5d}{:15s}{:>10,}".format("Minimum Stem Length", Lexicon.MinimumStemLength,
                                                                    "Maximum Affix Length", MaximumAffixLength,
                                                                    "Minimum Number of Signature uses: ",
                                                                    Lexicon.MinimumStemsInaSignature)
print >> lxalogfile, "{:40s}{:15,d}".format("Total words:", len(Lexicon.WordList.mylist))
print >> lxalogfile, "{:40s}{:15,d}".format("Total letter count in words: ", Lexicon.TotalLetterCountInWords)
print >> lxalogfile, "{:40s}{:15.2f}".format("Average letters per word: ",
                                             float(Lexicon.TotalLetterCountInWords) / len(Lexicon.WordList.mylist))

splitEndState = True
morphology = FSA_lxa(splitEndState)

if True:
    MakeSignatures(Lexicon, lxalogfile, FindSuffixesFlag, Lexicon.MinimumStemLength)
    print
    "Main program again."

if True:
    print
    "Printing signatures."
    printSignatures(Lexicon, lxalogfile, outfile_Signatures, outfile_WordToSig, outfile_StemToWords, g_encoding,
                    FindSuffixesFlag)

if False:
    print
    "Printing signature transforms for each word."
    printWordsToSigTransforms(Lexicon.SignatureToStems, Lexicon.WordToSig, Lexicon.StemCounts, outfile_SigTransforms,
                              g_encoding, FindSuffixesFlag)

if False:
    print
    "Slicing signatures."
    SliceSignatures(Lexicon, g_encoding, FindSuffixesFlag, lxalogfile)

if True:
    print
    "Adding signatures to the FSA."
    AddSignaturesToFSA(Lexicon, Lexicon.SignatureToStems, morphology, FindSuffixesFlag)

if True:
    print
    "Printing the FSA."
    print >> outfile_FSA, "#", language, shortfilename, numberofwords
    morphology.printFSA(outfile_FSA)

if False:
    print
    "Printing signatures."
    printSignatures(Lexicon, outfile_Signatures, outfile_WordToSig, outfile_StemToWords, g_encoding, FindSuffixesFlag,
                    letterCostOfStems, letterCostOfSignatures)

if False:
    print
    "Finding robust peripheral pieces on edges in FSA."
    for loopno in range(NumberOfCorrections):
        morphology.find_highest_weight_affix_in_an_edge(lxalogfile, FindSuffixesFlag)

if False:
    for state in morphology.States:
        # do not print the entire graph:
        # if state == morphology.startState:
        #	continue
        ###
        graph = morphology.createPySubgraph(state)
        # if the graph has 3 edges or fewer, do not print it:
        if len(graph.edges()) < 4:
            continue
        ###
        # if the graph has no branching nodes, do not print it:
        # if len(graph.nodes() ) > len(graph.edges() ):
        #	continue
        ###
        graph.layout(prog='dot')
        filename = outfolder + 'morphology' + str(state.index) + '.png'
        graph.draw(filename)
        filename = outfolder + 'morphology' + str(state.index) + '.dot'
        graph.write(filename)

# ---------------------------------------------------------------------------------#
#	5d. Print FSA again, with these changes.
# ---------------------------------------------------------------------------------#

if False:
    print
    "Printing the FSA."
    morphology.printFSA(outfile_FSA)

if True:
    print
    "Parsing all words through FSA."
    morphology.parseWords(Lexicon.WordToSig.keys(), outfile_WordParses)

if False:
    print
    "Printing all the words' parses."
    morphology.printAllParses(outfile_WordParses)

if False:
    print
    "Now look for common morphemes across different edges."
    morphology.findCommonMorphemes(lxalogfile)

if False:

    # we will remove this. It will be replaced by a function that looks at all cross-edge sharing of morphemes.
    print >> outfile_FSA, "Finding common stems across edges."
    HowManyTimesToCollapseEdges = 0
    for loop in range(HowManyTimesToCollapseEdges):
        print
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        print
        "Loop number", loop
        print
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        (commonEdgePairs, EdgeToEdgeCommonMorphs) = morphology.findCommonStems(lxalogfile)

        if len(commonEdgePairs) == 0:
            print
            "There are no more pairs of edges to consider."
            break
        edge1, edge2 = commonEdgePairs[0]
        state1 = edge1.fromState
        state2 = edge2.fromState
        state3 = edge1.toState
        state4 = edge2.toState
        print
        "\n\nWe are considering merging edge ", edge1.index, "(", edge1.fromState.index, "->", edge1.toState.index, ") and  edge", edge2.index, "(", edge2.fromState.index, "->", edge2.toState.index, ")"

        print
        "Printed graph", str(loop), "before_merger"
        graph = morphology.createDoublePySubgraph(state1, state2)
        graph.layout(prog='dot')
        filename = outfolder + str(loop) + '_before_merger' + str(state1.index) + "-" + str(state2.index) + '.png'
        graph.draw(filename)

        if state1 == state2:
            print
            "The from-States are identical"
            state_changed_1 = state1
            state_changed_2 = state2
            morphology.mergeTwoStatesCommonMother(state3, state4)
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        elif state3 == state4:
            print
            "The to-States are identical"
            state_changed_1 = state3
            state_changed_2 = state4
            morphology.mergeTwoStatesCommonDaughter(state1, state2)
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        elif morphology.mergeTwoStatesCommonMother(state1, state2):
            print
            "Now we have merged two sister edges from line 374 **********"
            state_changed_1 = state1
            state_changed_2 = state2
            morphology.EdgePairsToIgnore.append((edge1, edge2))


        elif morphology.mergeTwoStatesCommonDaughter((state3, state4)):
            print
            "Now we have merged two daughter edges from line 377 **********"
            state_changed_1 = state3
            state_changed_2 = state4
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        graph = morphology.createPySubgraph(state1)
        graph.layout(prog='dot')
        filename = outfolder + str(loop) + '_after_merger_' + str(state_changed_1.index) + "-" + str(
            state_changed_2.index) + '.png'
        print
        "Printed graph", str(loop), "after_merger"
        graph.draw(filename)


        # ------------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------------#
#		User inquiries about morphology
# ------------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------------#

morphology_copy = morphology.MakeCopy()

initialParseChain = list()
CompletedParses = list()
IncompleteParses = list()
word = ""
while True:
    word = raw_input('Inquire about a word: ')
    if word == "exit":
        break
    if word == "State":
        while True:
            stateno = raw_input("State number:")
            if stateno == "" or stateno == "exit":
                break
            stateno = int(stateno)
            for state in morphology.States:
                if state.index == stateno:
                    break
            state = morphology.States[stateno]
            for edge in state.getOutgoingEdges():
                print
                "Edge number", edge.index
                i = 0
                for morph in edge.labels:
                    print
                    "%12s" % morph,
                    i += 1
                    if i % 6 == 0: print
            print
            "\n\n"
            continue
    if word == "Edge":
        while True:
            edgeno = raw_input("Edge number:")
            if edgeno == "" or edgeno == "exit":
                break
            edgeno = int(edgeno)
            for edge in morphology.Edges:
                if edge.index == edgeno:
                    break
            print
            "From state", morphology.Edges[edgeno].fromState.index, "To state", morphology.Edges[edgeno].toState.index
            for edge in morphology.Edges:
                if edge.index == int(edgeno):
                    morphlist = list(edge.labels)
            for i in range(len(morphlist)):
                print
                "%12s" % morphlist[i],
                if i % 6 == 0:
                    print
            print
            "\n\n"
            continue
    if word == "graph":
        while True:
            stateno = raw_input("Graph state number:")

    del CompletedParses[:]
    del IncompleteParses[:]
    del initialParseChain[:]
    startingParseChunk = parseChunk("", word)
    startingParseChunk.toState = morphology.startState

    initialParseChain.append(startingParseChunk)
    IncompleteParses.append(initialParseChain)
    while len(IncompleteParses) > 0:
        CompletedParses, IncompleteParses = morphology.lparse(CompletedParses, IncompleteParses)
    if len(CompletedParses) == 0: print
    "no analysis found."

    for parseChain in CompletedParses:
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.morph,
        print
    print

    for parseChain in CompletedParses:
        print
        "\tStates: ",
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.fromState.index,
        print
        "\t", thisParseChunk.toState.index
    print

    for parseChain in CompletedParses:
        print
        "\tEdges: ",
        for thisParseChunk in parseChain:
            if (thisParseChunk.edge):
                print
                "\t", thisParseChunk.edge.index,
        print
    print
    "\n\n"

# ---------------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------#
#	Close output files
# ---------------------------------------------------------------------------------#

outfile_FSA.close()
Signatures_outfile.close()
outfile_SigTransforms.close()
lxalogfile.close()

# ---------------------------------------------------------------------------------#
#	Logging information
# ---------------------------------------------------------------------------------#

localtime = time.asctime(time.localtime(time.time()))
print
"Local current time :", localtime

lxalogfile.close()
# --------------------------------------------------#
