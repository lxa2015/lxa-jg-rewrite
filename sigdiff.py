from lxa_module import *

DiffType = "suffixal"

outfilename = "../../documents/papers/allomorphy/french-verb.tex"
outfile = open(outfilename, "w")

words1 = "monter-monte-montes-monte-montons-montez-montent-monterai-monteras-montera-monterons-monterez-monteront"
words2 = "punir-punis-punis-punit-punissons-punissez-punissent-punirai-puniras-punira-punirons-punirez-puniront"
# words1 = "jump-jumps-jumped-jumping"
# words2 = "move-moves-moved-moving"
# words2 = "push-pushes-pushed-pushing"
# words1 = "monter-monte-montes-monte-montons-montez-montent"


basictableau1 = intrasignaturetable()
basictableau1.setsignature(words1)

basictableau2 = intrasignaturetable()
basictableau2.setsignature(words2)

outlist = []
StartLatexDoc(outfile)
MakeLatexFile(outfile, basictableau1.displaytolist(outlist))

MakeLatexFile(outfile, basictableau2.displaytolist(outlist))

basictableau1.minus_aligned(basictableau2, DiffType)
MakeLatexFile(outfile, basictableau1.displaytolist_aligned_latex(outlist))

EndLatexDoc(outfile)
