import yaml
import os

# ############ SETUP ##############################
configfile: "configs/config_P1696_LungWES.yml"
# configfile: "configs/config.json"
workdir: config['workdir']

# extract the scriptdir for creating shell_paths
snakedir = os.path.dirname(workflow.snakefile)
scriptdir = os.path.join(snakedir, "scripts")
# include helper functionss
include: "includes/io.snk"
include: "includes/utils.snk"


# retrieve the file_df with all the file paths from the samplesheet
sample_df, short_sample_df = get_files(config['inputdirs'], config['samples']['samplesheet'])
chrom_list = get_chrom_list(config)

# ############ INCLUDES ##############################  
include: "includes/fastq.snk"
include: "includes/QC.snk"
include: "includes/map.snk"
include: "includes/splitBAM.snk"
include: "includes/processBAM.snk"
include: "includes/dedup.snk"
include: "includes/umi_filter.snk"

# convenience variables
ref_gen = full_path('genome')

# specified wildcards have to match the regex
wildcard_constraints:
    # eg sample cannot contain _ or / to prevent ambiguous wildcards
    # sample = "[^_/.]+_?[ABRX][12]?",
    sample = "[^_/.]+",
    read = "[^_/.]+",
    split = "[0-9]+",
    read_or_index = "[^_/.]+",
    chrom = "(chr)?[0-9XY]+",
    chrom_split = "[^_/.]+",


# ############## MASTER RULE ##############################################

rule all:
    input:
        QC_output,
        expand("coverBED/{samples}.txt", samples=sample_df.query('R1 == R1').index),

###########################################################################

# print out of installed tools
# onstart:
#     print("    EXOM SEQUENCING PIPELINE STARTING.......")
#     print('fastq:', short_sample_df.loc[:, ['R1', 'R2', 'index']])
#     ##########################
#     path_to_config = os.path.join(config['workdir'], "config.yaml")
#     with open(path_to_config, 'w+') as stream:
#         yaml.dump(config, stream, default_flow_style=False)
#     # create logs folder


# onsuccess:
#     # shell("export PATH=$ORG_PATH; unset ORG_PATH")
#     print("WESbam workflow finished - everything ran smoothly")

#     # cleanup
#     if config['setup']['cleanup']['run']:
#         no_bams = config['setup']['cleanup']['keep_only_final_bam']

#         split_fastq_pattern = '\.[0-9]+\.fastq.gz'
#         split_bam_pattern = 'chr[^.]+\..*'
#         split_table_pattern = 'chr[^.]+\.csv'

#         shell("rm -rf ubam realigned bam_metrics insert_metrics fastqc mapped bam_done")


#         # remove split fastqs
#         shell("ls fastq | grep -E '{split_fastq_pattern}' | sed 's_^_fastq/_' | xargs -r rm -f")
        
#         # remove split recalib bams
#         shell("ls recalib | grep -E '{split_bam_pattern}' | sed 's-^-recalib/-' | xargs -r rm -f")

#         if no_bams:
#             shell("rm -r bam_merge ")
#         else:
#             # only remove split_bams in bam_merge
#             shell("ls bam_merge | grep -E '{split_bam_pattern}' | sed 's-^-bam_merge/-' | xargs -r rm -f")
