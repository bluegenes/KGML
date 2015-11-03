# 7.1.2015

# Builtins
import os, sys
# from armchair biology blog (now implemented in biopython)
from KGML_parser import read
from KGML_vis import KGMLCanvas
from KGML_scrape import retrieve_kgml_to_file, retrieve_KEGG_pathway
import argparse
############################
psr = argparse.ArgumentParser(description="Color KEGG maps with the Kegg Orthology entries that exist in your annotated transcriptome.")
# kegg pathway name
psr.add_argument('--path',help='Kegg Pathway Name', dest="path")
# folder for map output
psr.add_argument('--output',help='name of output folder', default = './', dest="outDir")
# KO (for just presence/absence)
psr.add_argument('--blastKO', help='Kegg Orthology from blast', dest='transKO')
# upregulated KO
psr.add_argument('--upReg', help='OPTIONAL: upregulated KO', nargs='?', default=None, dest= 'upKO') #os.devnull, dest= 'upKO')
# downregulated KO
psr.add_argument('--downReg', help='OPTIONAL: downregulated KO', nargs='?', default=None, dest= 'downKO') #os.devnull, dest= 'downKO')
##############################
args = psr.parse_args()
##############################
def readKOFile(koFile, keggPath):
    koList = []
    with open(koFile, 'r') as koF:
        for line in koF:
            path = 'ko:' + line.rstrip().split('\t')[2]
            koList.append(path)
        koF.close()
    entryList = [e for e in keggPath.entries.values() if len(set(e.name.split()).intersection(koList))]
    return set(entryList)

def colorMapItems(geneSet, color, width):
    for e in geneSet:
	for g in e.graphics:
	    if g.type == 'line':
		g.fgcolor = color
		g.width = width
	    g.bgcolor = color

if not os.path.exists(args.outDir):
    os.makedirs(args.outDir)

pathway = retrieve_KEGG_pathway(args.path) #pathway of interest

#get KO numbers from previously created file
#ko = ['ko:'+ ko for (trans,sp,ko) in (line.strip().split("\t") for line in (open(args.KO, 'r')))]

knownKOSet = readKOFile(args.transKO, pathway)
enhanceSet = knownKOSet
if args.upKO != None:
    upKOSet = readKOFile(args.upKO, pathway)
    enhanceSet.update(upKOSet)
if args.downKO != None:
    downKOSet = readKOFile(args.downKO, pathway)
    enhanceSet.update(downKOSet)

notDE = set([e for e in pathway.orthologs if not len(set(e.name.split()).intersection(enhanceSet))])

kgml_map = KGMLCanvas(pathway, show_maps=True)
kgml_map.import_imagemap = True  # turn this off to allow all elements to go gray!
kgml_map.show_maps = False
kgml_map.show_orthologs = False
kgml_map.draw_relations = False
kgml_map.show_compounds = False
kgml_map.show_genes = False

os.chdir(args.outDir)

colorMapItems(notDE,'#D3D3D3', 1)
colorMapItems(knownKOSet,'#666666', 10)

if args.upKO != None:
    colorMapItems(upKOSet,'#FF0000', 10)
if args.downKO != None:
    colorMapItems(downKOSet,'#0000FF', 10)

# And rendering elements as an overlay
kgml_map.show_compounds = True
kgml_map.show_genes = True
kgml_map.show_orthologs = True
#kgml_map.draw_relations = True

kgml_map.draw(args.path + '.pdf')



