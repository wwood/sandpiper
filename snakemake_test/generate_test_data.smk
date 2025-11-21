

test_data_dir = '../test/data/more_runs'
test_accessions_file = test_data_dir + '/accessions'

# Create test_data_dir if it doesn't already exist
import os
if not os.path.exists(test_data_dir):
    os.makedirs(test_data_dir)

with open(test_accessions_file, 'w') as f:
    f.write('\n'.join([
        'ERR1914274',
        'ERR2000810',
        'ERR3191584',
        'ERR4032157',
        'ERR4131628',
        'SRR9113719',
        'SRR3401492',
        'SRR7051324',
        'SRR7051350',
        'ERR575710',
        'ERR2194039',
        'ERR2193791',
        'SRR10875094', # Virome -> has SMF warning
    ]))

configfile: 'prod_config.yml'

rule all:
    input:
        test_data_dir + '/metadata_each_line.json',
        test_data_dir + '/condensed.csv.gz',
        test_data_dir + '/otu_table.csv.gz',
        test_data_dir + '/host_or_not_preds.tsv.gz',
        test_data_dir + '/smf.csv'

rule json_metadata_files:
    input:
        # config['JSON_METADATA_FILES'],
        test_accessions_file,
    output:
        test_data_dir + '/metadata_each_line.json',
    params:
        test_data_dir=test_data_dir,
        test_accessions_file=test_accessions_file,
    shell:
        """
        grep -hFf {params.test_accessions_file} {config[JSON_METADATA_FILES]} >{output}
        """

# condensed.csv.gz  host_or_not_preds.tsv.gz  metadata_each_line.json  otu_table.csv.gz
rule condense:
    input:
        config['CONDENSED_OTU_TABLE'],
        test_accessions_file,
    output:
        test_data_dir + '/condensed.csv.gz',
    params:
        test_data_dir=test_data_dir,
        test_accessions_file=test_accessions_file,
    shell:
        """
        pigz -cd {config[CONDENSED_OTU_TABLE]} |grep -Ff {params.test_accessions_file} |cat <(pigz -cd {config[CONDENSED_OTU_TABLE]} |head -1) - |pigz >{output}
        """

rule otu_table:
    input:
        config['OTU_TABLE'],
        test_accessions_file,
    output:
        test_data_dir + '/otu_table.csv.gz',
    params:
        test_data_dir=test_data_dir,
        test_accessions_file=test_accessions_file,
    shell: # Using zcat atm since the servers are having odd threading issues
        """
        zcat {config[OTU_TABLE]} |grep -Ff {params.test_accessions_file} |cat <(zcat {config[OTU_TABLE]} |head -1) - |pigz >{output}
        """

rule host_or_not_preds:
    input:
        config['HOST_OR_NOT_PREDICTION'],
        test_accessions_file,
    output:
        test_data_dir + '/host_or_not_preds.tsv.gz',
    params:
        test_data_dir=test_data_dir,
        test_accessions_file=test_accessions_file,
    shell:
        """
        cat {config[HOST_OR_NOT_PREDICTION]} |grep -Ff {params.test_accessions_file} |cat <(cat {config[HOST_OR_NOT_PREDICTION]} |head -1) - |pigz >{output}
        """

rule smf:
    input:
        config['SMF_FILE'],
        test_accessions_file,
    output:
        test_data_dir + '/smf.csv',
    params:
        test_data_dir=test_data_dir,
        test_accessions_file=test_accessions_file,
    shell:
        """
        grep -Ff {params.test_accessions_file} {config[SMF_FILE]} |cat <(head -1 {config[SMF_FILE]}) - >{output}
        """