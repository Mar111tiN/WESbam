import os
import pandas as pd

# ############ SNAKEMAKE ##################

w = snakemake.wildcards
config = snakemake.config
f_config = config['filter']

# loading filter 1
mut_file = snakemake.input.filter1
print(f'Loading mutation file {mut_file}.')
filter1_df = pd.read_csv(mut_file, sep='\t')
print('Done.')

# loading filter 2 settings
filter_name = f_config['filter2']
filter_file = os.path.join(
    config['paths']['filter_settings'],
    f_config['filter_settings']
)
sheet = f_config['excel_sheet']
print(f"Running filter2 {filter_name}")
print(f"Loading filter file {filter_file}")
if "xls" in os.path.splitext(filter_file)[1]:
    filter_settings = pd.read_excel(filter_file, sheet_name=sheet, index_col=0)[:4]
else:
    filter_settings = pd.read_csv(filter_file, sep='\t', index_col=0)

print('Done.')

output_base = snakemake.output.filter2.replace('.loose.csv', '')
threads = f_config['threads']
keep_syn = f_config['keep_syn']


# ######## FILTER 2 ######################
def filter2(df, _filter='moderate'):
    '''
    creates filtered output using the daniel filtering
    input: pd.dataframe of unfiltered annovar output
    output:
    - filtered/sample_tumor-normal_daniel.csv
    '''
    # get thresholds
    print("filter: ", f"filter2-{_filter}")
    thresh = filter_settings.loc[f"filter2-{_filter}", :]

    # ##### TUMOR DEPTH ############
    tumor_depth = (df['TR2'] > thresh['variantT']) & (
        df['Tdepth'] > thresh['Tdepth'])

    # ##### VAF ##################
    # minimum TVAF if not candidate
    is_candidate = (df['isCandidate'] == 1) | (df['isDriver'] == 1) | (df['ChipFreq'] > 0)
    # either cand with higher TVAF or lower TVAF
    TVAF = (is_candidate & (df['TVAF'] >= thresh['TVAF4Cand'])) | (df['TVAF'] >= thresh['TVAF'])
    # NVAF is computed from upper threshold and a max similarity to TVAF
    upper = (1 + thresh['VAFSim']) * df['NVAF']
    lower = (1 - thresh['VAFSim']) * df['NVAF']
    NVAF = ((upper < df['TVAF']) | (df['TVAF'] < lower)) & (df['NVAF'] <= thresh['NVAF'])
    VAF = NVAF & TVAF

    # ##### EB/PoN-Filter ##########
    if thresh['EBscore'] == thresh['EBscore']:
        eb = df['EBscore'] >= thresh['EBscore']
    else:
        eb = True
    pon_eb = (eb & (df['PoN-Ratio'] < thresh['PoN-Ratio'])) | (df['PoN-Alt-NonZeros'] < thresh['PoN-Alt-NonZeros'])

    # ############ HDR ####################
    HDR = (df['TumorHDRcount'] <= thresh['HDRcount']) & (df['NormalHDRcount'] <= thresh['HDRcount'])

    # ##### POPULATION #############
    # reformat population columns for filtering
    for col in ['gnomAD_exome_ALL', 'esp6500siv2_all', 'dbSNP153_AltFreq']:
        df.loc[df[col] == ".", col] = 0
        df[col] = df[col].fillna(0).astype(float)

    if thresh['PopFreq'] == thresh['PopFreq']:
        noSNP = (df['gnomAD_exome_ALL'] < thresh['PopFreq']) & (df['esp6500siv2_all'] < thresh['PopFreq']) & (df['dbSNP153_AltFreq'] < thresh['PopFreq'])
    else:
        noSNP = True

    # ####### STRANDBIAS / POLARITY ##########################
    # Strand Ratio (as FisherScore and simple)
    no_strand_bias = df['FisherScore'] <= thresh['FisherScore']
    # Strand Polarity (filters out very uneven strand distribution of alt calls)
    if thresh['strand_polarity'] == thresh['strand_polarity']:
        pol = thresh['strand_polarity']
        no_strand_polarity = no_strand_polarity = (df['TR2+'] / df['TR2'] <= pol) & (df['TR2+'] / df['TR2'] >= (1-pol))
    else:
        no_strand_polarity = True

    strandOK = no_strand_bias & no_strand_polarity

    # ## FILTER2 RESCUE ##########
    # Clin_score is used for rescue of all mutations
    clin_score = df['ClinScore'] >= thresh['ClinScore']

    rescue = clin_score

    filter_criteria = tumor_depth & pon_eb & (noSNP & strandOK & VAF & HDR | rescue)
    # apply filters to dataframe
    df = df[filter_criteria].sort_values(['TVAF'], ascending=False)
    list_len = len(df.index)
    return df, list_len


# ################ OUTPUT #############################################################
print(f"Writing filter2 lists to {output_base}.<stringency>.csv")

excel_file = f"{output_base}.xlsx"
with pd.ExcelWriter(excel_file) as writer:
    filter2_dfs = {}
    df_lengths = {}
    for stringency in ['loose', 'moderate', 'strict']:
        filter2_dfs[stringency], df_lengths[stringency] = filter2(
            filter1_df, _filter=stringency)
        print(f"{stringency}: {df_lengths[stringency]}")
        output_file = f"{output_base}.{stringency}.csv"
        filter2_dfs[stringency].to_csv(output_file, sep='\t', index=False)
        filter2_dfs[stringency].to_excel(
            writer, sheet_name=f'{stringency} <{df_lengths[stringency]}>', index=False)
    print(f"Writing combined filters to excel file {excel_file}.")
    filter1_df.to_excel(
        writer, sheet_name=f'filter1 <{len(filter1_df.index)}>', index=False)


# Writing mutation list for filterbam
stringency = config['filter_bam']['stringency_for_bam']
list_for_bam = snakemake.output.filter2_for_filterbam
# select stringency based on filter_bam config
filter2_dfs[stringency].to_csv(list_for_bam, sep='\t', index=False)
