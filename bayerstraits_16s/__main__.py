import os
from Bio import SeqIO
import argparse
import glob
import bayerstraits_16s
import sys


################################################### Decalration #######################################################
print ("\
------------------------------------------------------------------------\n\
bayerstraits_16s infers traits by 16S\n\
input: otu table (-t) and otu sequences (-s)\n\
requirement: mafft and fasttree\n\n\
Copyright:An Ni Zhang, Prof. Eric Alm, MIT\n\n\
Citation:\n\
Contact anniz44@mit.edu\n\
------------------------------------------------------------------------\n\
")

def main():
    usage = ("usage: bayerstraits_16s -t your.otu.table -s your.otu.seqs")
    version_string = 'bayerstraits_16s {v}, on Python {pyv[0]}.{pyv[1]}.{pyv[2]}'.format(
        v=bayerstraits_16s.__version__,
        pyv=sys.version_info,
    )
    ############################################ Arguments and declarations ##############################################
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-t",
                        help="file name of your otu_table", type=str,
                        default='your.otu.table', metavar='your.otu.table')
    parser.add_argument("-s",
                        help="file name of your otu_seq", type=str,
                        default='your.otu.fasta', metavar='your.otu.fasta')
    parser.add_argument("-r",
                        help="results_dir", type=str, default='BayersTraits', metavar='BayersTraits')
    parser.add_argument("-top",
                        help="number of top OTUs", type=int, default=1000, metavar=1000)
    parser.add_argument("--m",
                        help="the path of mafft", type=str,
                        default='/usr/local/bin/mafft', metavar='mafft')
    parser.add_argument("--ft",
                        help="the path of fasttree", type=str,
                        default='/usr/local/bin/FastTree', metavar='your FastTree')
    parser.add_argument("--rs",
                        help="the reference 16S", type=str,
                        default='default', metavar='default or your own reference 16s sequences')
    parser.add_argument("--rt",
                        help="the reference data of gene traits", type=str,
                        default='default', metavar='default or your own reference traits')
    parser.add_argument("--th",
                        help="number of threads", type=int, default=1, metavar=1)
    parser.add_argument("--test",
                        help="test the bayerstraits_16s", action="store_true")
    ################################################## Definition ########################################################
    args = parser.parse_args()
    workingdir=os.path.abspath(os.path.dirname(__file__))
    if args.rs == 'default':
        ref_tree = os.path.join(workingdir,'data/Complete_genome_16S.fasta')
    else:
        ref_tree = args.rs
    if args.rt == 'default':
        ref_traits = os.path.join(workingdir, 'data/Genome_butyrate_buk_ptbORbut.txt')
    else:
        ref_traits = args.rt
    if args.test:
        input_table = os.path.join(workingdir, 'example/example.otu_table')
        input_seq = os.path.join(workingdir, 'example/example.otu_seqs')
    else:
        input_table = args.t
        input_seq = args.s
    try:
        os.mkdir(args.r)
    except OSError:
        pass
    try:
        os.mkdir(args.r + '/Bayers_model')
    except OSError:
        pass
    rootofus, otuseq = os.path.split(input_seq)
    rootofutb, otutable = os.path.split(input_table)
    ################################################### Programme #######################################################
    f1 = open(os.path.join(args.r, otutable + 'BayersTraits.log'), 'w')
    # filter the OTU sequences of top args.top max abudance
    print ('filter the OTU sequences of top ' + str(args.top) + ' max abudance')
    try:
        ftry = open(str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter', 'r')
    except IOError:
        cmd = 'python ' + workingdir + '/scripts/OTU.filter.py -t ' + str(input_table) + ' -s ' + str(input_seq) \
               + ' -top ' + str(args.top) + ' -r ' + str(args.r) + '/Filtered_OTU \n'
        os.system(cmd)
        f1.write(cmd)
    # align the otus with reference 16S
    print('align the otus sequences with reference 16S sequences\nit takes quite a while...')
    try:
        ftry = open(str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S', 'r')
    except IOError:
        cmd = 'cat ' + str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter ' + str(ref_tree) + ' > ' + \
               str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.16S \n'
        os.system(cmd)
        f1.write(cmd)
        # InferTraits
        cmd = args.m + ' --nuc --adjustdirection --quiet --maxiterate 0 --retree 2 --nofft --thread ' + str(
            args.th) + ' ' + \
               str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.16S > ' + \
               str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S \n'
        os.system(cmd)
        f1.write(cmd)
    print('alignment finished!\nnow we are building the tree\nit also takes quite a while...')
    try:
        ftry = open(str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S.nwk', 'r')
    except IOError:
        cmd = 'python ' + workingdir + '/scripts/treeformat.py -a ' + str(args.r) + \
               '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S \n'
        os.system(cmd)
        f1.write(cmd)
        cmd = args.ft + ' -quiet -fastest -nt -nosupport ' + str(args.r) + '/Filtered_OTU/' + \
               str(otuseq) + '.filter.align.16S.format > ' + \
               str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S.nwk \n'
        os.system(cmd)
        f1.write(cmd)
    # run BayersTraits
    # build the model
    print('infer the traits based on 16s\nwe are almost there!')
    try:
        ftry = open(str(args.r) + '/Bayers_model/' + str(otuseq) + '.filter.align.16S.nwk.infertraits.txt', 'r')
    except IOError:
        # InferTraits only
        cmd = 'python ' + workingdir + '/scripts/Bayers.model.py -t ' + str(args.r) + '/Filtered_OTU/' + str(
            otuseq) + '.filter.align.16S.nwk -n ' + \
               str(args.r) + '/Filtered_OTU/' + str(otuseq) + '.filter.align.16S.format.name -rd ' + \
               str(ref_traits) + ' -a ' + \
               str(args.r) + '/Filtered_OTU/' + str(otutable) + '.abu.table -r ' \
               + str(args.r) + '/Bayers_model -b ' + str(workingdir + "/scripts/inferTraits.py") + ' \n'
        os.system(cmd)
        f1.write(cmd)
    f1.close()

################################################## Function ########################################################

if __name__ == '__main__':
    main()
