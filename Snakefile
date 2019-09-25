configfile:"config.yaml"

output_dir = config["output_dir"]
inter_dir = config["inter_dir"]
data_dir= config["data_dir"]
source_dir = config["source_dir"]

#from snakemake.remote.GS import RemoteProvider as GSRemoteProvider

#===============================================================================
rule target_safety:
    input:
        clf = inter_dir + "/clinical_findings.json",
        tis = inter_dir + "/high_tissue_expression.json",
        biof = inter_dir + "/biofunction.json",
        dasc = inter_dir + "/disease_associations.json",
        anim = inter_dir + "/animal_data.json",
        par = inter_dir + "/high_perc_paralogues.json"
    output:
        output_dir + "/target_safety.json"
    shell:
        "python {source_dir}/target_safety.py -clinical_findings {input.clf} -tissue_expression {input.tis} -bio_function {input.biof} -disease_associations {input.dasc} -animal_data {input.anim} -potential_off_targets {input.par} -o {output}"
#===============================================================================
rule clinical_findings:
    input:
        drug_index = data_dir + "/OT_data/drug_index.json",
        adr = data_dir + "/OT_spreadsheets/known_safety_adr.tsv",
        sri = data_dir + "/OT_spreadsheets/known_safety_sri.tsv",
        ubr = data_dir + "/OT_spreadsheets/known_safety_ubr.tsv",
        efo = data_dir + "/OT_spreadsheets/known_safety_efo.tsv",
        ref = data_dir + "/OT_spreadsheets/known_safety_ref.tsv",
        fda_aes = data_dir + "/significant_AEs_by_target.csv",
        gene_mapfile = data_dir + "/OT_data/gene_mapfile.json"
    output:
        inter_dir + "/clinical_findings.json"
    shell:
        "python {source_dir}/clinical_buckets.py -drug_index {input.drug_index} -adr {input.adr} -sri {input.sri} -ubr {input.ubr} -efo {input.efo} -ref {input.ref} -fda_aes {input.fda_aes} -gene_mapfile {input.gene_mapfile} -o {output}"

#-------------------------------------------------------------------------------
rule collect_drug_info:
    input:
        drug_index = data_dir + "/OT_data/drug_index.json"
    output:
        inter_dir + "/drug_info.json"
    shell:
        "python {source_dir}/drug_info.py -drug_index {input.drug_index} -o {output}"

#-------------------------------------------------------------------------------
rule known_target_safety:
    input:
        adr = data_dir + "/OT_spreadsheets/known_safety_adr.tsv",
        sri = data_dir + "/OT_spreadsheets/known_safety_sri.tsv",
        ubr = data_dir + "/OT_spreadsheets/known_safety_ubr.tsv",
        efo = data_dir + "/OT_spreadsheets/known_safety_efo.tsv",
        ref = data_dir + "/OT_spreadsheets/known_safety_ref.tsv"
    output:
        inter_dir + "/known_target_safety.json"
    shell:
        "python {source_dir}/known_target_safety.py -adr {input.adr} -sri {input.sri} -ubr {input.ubr} -efo {input.efo} -ref {input.ref} -o {output}"

rule known_target_safety_tables_download:
    params:
        gkey = config["known_safety"]["gkey"],
        adr_gid = config["known_safety"]["adr_gid"],
        sri_gid = config["known_safety"]["sri_gid"],
        ubr_gid = config["known_safety"]["ubr_gid"],
        efo_gid = config["known_safety"]["efo_gid"],
        ref_gid = config["known_safety"]["ref_gid"]
    output:
        adr = data_dir + "/OT_spreadsheets/known_safety_adr.tsv",
        sri = data_dir + "/OT_spreadsheets/known_safety_sri.tsv",
        ubr = data_dir + "/OT_spreadsheets/known_safety_ubr.tsv",
        efo = data_dir + "/OT_spreadsheets/known_safety_efo.tsv",
        ref = data_dir + "/OT_spreadsheets/known_safety_ref.tsv"
    shell:
        """
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.adr_gid} -o {output.adr}
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.sri_gid} -o {output.sri}
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.ubr_gid} -o {output.ubr}
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.efo_gid} -o {output.efo}
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.ref_gid} -o {output.ref}
        """

#-------------------------------------------------------------------------------
rule FDA_AEs_by_target:
    input:
        data_dir + "/significant_AEs_by_target.csv"
    output:
        inter_dir + "/adverse_effects_per_target.json"
    shell:
        "python {source_dir}/FDA_AEs_per_target.py -i {input} -o {output}"

rule significant_AEs_by_target_MonteCarlo:
    input:
        data_dir + "/OT_data/fda_aes_by_target.json"
    output:
        data_dir + "/significant_AEs_by_target.csv"
    shell:
        "Rscript {source_dir}/openFDA_MonteCarlo_target.R {input} {output}"

#===============================================================================
rule tissue_expression:
    input:
        data_dir + "/OT_data/expression_index.json"
    output:
        inter_dir + "/high_tissue_expression.json"
    shell:
        "python {source_dir}/tissue_expression.py -expression_index {input} -o {output}"

#===============================================================================
rule biofunction_buckets:
    input:
        gene_index =  data_dir + "/OT_data/gene_index.json",
        go = data_dir + "/OT_spreadsheets/GO_Enriched_Terms_Lists.tsv",
        react = data_dir + "/OT_spreadsheets/Reactome_Enriched_Terms_Lists.tsv",
        sanger = data_dir + "/coreFitnessADAM_Sanger.txt",
        broad = data_dir + "/coreFitnessADAM_Broad.txt",
        bagel = data_dir + "/external_downloads/coreFitness_BAGEL.tsv",
        ogee = data_dir + "/external_downloads/ogee_all.txt",
        gene_mapfile = data_dir + "/OT_data/gene_mapfile.json"
    output:
        inter_dir + "/biofunction.json"
    shell:
        "python {source_dir}/bio_function_buckets.py -gene_index {input.gene_index} -go {input.go} -react {input.react} -sanger {input.sanger} -broad {input.broad} -bagel {input.bagel} -ogee {input.ogee} -gene_mapfile {input.gene_mapfile} -o {output}"

#-------------------------------------------------------------------------------
rule flag_essential_genes:
    input:
        sanger = data_dir + "/coreFitnessADAM_Sanger.txt",
        broad = data_dir + "/coreFitnessADAM_Broad.txt",
        bagel = data_dir + "/external_downloads/coreFitness_BAGEL.tsv",
        ogee = data_dir + "/external_downloads/ogee_all.txt",
        gene_mapfile = data_dir + "/OT_data/gene_mapfile.json"
    output:
        inter_dir + "/essential_genes.json"
    shell:
        "python {source_dir}/essential_genes.py -sanger {input.sanger} -broad {input.broad} -bagel {input.bagel} -ogee {input.ogee} -gene_mapfile {input.gene_mapfile} -o {output}"

rule run_ADAM_sanger:
    input:
        adam_repo = source_dir + "/ADAM",
        depscores = data_dir + "/external_downloads/sanger_binaryDepScores.tsv"
    output:
        data_dir + "/coreFitnessADAM_Sanger.txt",
    shell:
        "Rscript {source_dir}/run_ADAM.R {input.adam_repo} {input.depscores} {output}"

rule run_ADAM_broad:
    input:
        adam_repo = source_dir + "/ADAM",
        depscores = data_dir + "/external_downloads/broad_binaryDepScores.tsv"
    output:
        data_dir + "/coreFitnessADAM_Broad.txt",
    shell:
        "Rscript {source_dir}/run_ADAM.R {input.adam_repo} {input.depscores} {output}"

rule ADAM_repository:
    output:
        repo = directory(source_dir + "/ADAM")
    shell:
        "git clone https://github.com/francescojm/ADAM {output.repo}"

rule DepScore_sanger_download:
    output:
        data_dir + "/external_downloads/sanger_binaryDepScores.tsv",
    shell:
        """
        wget -O {output}.zip \'https://cog.sanger.ac.uk/cmp/download/binaryDepScores.tsv.zip\'
        unzip {output}.zip && mv binaryDepScores.tsv {output} && rm {output}.zip
        """

rule DepScore_broad_download:
    output:
        data_dir + "/external_downloads/broad_binaryDepScores.tsv"
    shell:
        """
        wget -O {output}.zip \'https://cog.sanger.ac.uk/cmp/download/broad_binaryDepScores_190724.tsv.zip\'
        unzip {output}.zip && mv binaryDepScores.tsv {output} && rm {output}.zip
        """

rule bagel_download: # curated version also available through cancer dependency map AdAM github repository
    output:
        data_dir + "/external_downloads/coreFitness_BAGEL.tsv"
    shell:
        "wget -O {output} \'http://tko.ccbr.utoronto.ca/Data/core-essential-genes-sym_HGNCID\'"

rule ogee_download:
    output:
        data_dir + "/external_downloads/ogee_all.txt"
    shell:
        """
        wget -O {output}.gz \'http://ogee.medgenius.info/file_download/9606_all.txt.gz\'
        gzip -d {output}.gz
        """


#-------------------------------------------------------------------------------
rule flag_enriched_terms:
    input:
        gene_index =  data_dir + "/OT_data/gene_index.json",
        go = data_dir + "/OT_spreadsheets/GO_Enriched_Terms_Lists.tsv",
        react = data_dir + "/OT_spreadsheets/Reactome_Enriched_Terms_Lists.tsv"
    output:
        inter_dir + "/flagged_terms.json"
    shell:
        "python {source_dir}/flag_GO_React_terms.py -gene_index {input.gene_index} -go {input.go} -react {input.react} -o {output}"

rule critical_terms_download:
    params:
        gkey = config["enriched_terms"]["gkey"],
        go_gid = config["enriched_terms"]["go_gid"],
        reactome_gid = config["enriched_terms"]["reactome_gid"]
    output:
        go = data_dir + "/OT_spreadsheets/GO_Enriched_Terms_Lists.tsv",
        react = data_dir + "/OT_spreadsheets/Reactome_Enriched_Terms_Lists.tsv"
    shell:
        """
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.go_gid} -o {output.go}
        python {source_dir}/GoogleSpreadSheet.py -gkey {params.gkey} -gid {params.reactome_gid} -o {output.react}
        """
#===============================================================================
rule disease_associations:
    input:
        OT_associations = data_dir + "/OT_data/OT_associations.json",
        cosmic_evidence = data_dir + "/OT_data/cosmic_evidence.json",
        rare = data_dir + "/rare_diseases.txt"
    output:
        inter_dir + "/disease_associations.json"
    shell:
        "python {source_dir}/disease_associations.py -OT_associations {input.OT_associations} -cosmic {input.cosmic_evidence} -rare {input.rare} -o {output}"

#-------------------------------------------------------------------------------
rule rare_diseases:
    input:
        OT_associations = data_dir + "/OT_data/OT_associations.json",
        efo = data_dir + "/external_downloads/efo.obo"
    output:
        data_dir + "/rare_diseases.txt"
    shell:
        "python {source_dir}/rare_diseases.py -OT_associations {input.OT_associations} -efo {input.efo} -o {output}"

rule efo_obo_download:
    output:
        data_dir + "/external_downloads/efo.obo"
    shell:
        "wget -O {output} \'https://www.ebi.ac.uk/efo/efo.obo\'"

#===============================================================================
rule animal_data:
    input:
        data_dir + "/OT_data/gene_index.json"
    output:
        inter_dir + "/animal_data.json"
    shell:
        "python {source_dir}/animal_data.py -gene_index {input} -o {output}"

#===============================================================================
rule potential_off_targets:
    input:
        data_dir + "/external_downloads/ensembl_paralogues.tsv"
    output:
        inter_dir + "/high_perc_paralogues.json"
    shell:
        "python {source_dir}/paralogues.py -i {input} -o {output}"

rule ensembl_paralogues_download:
    output:
        data_dir + "/external_downloads/ensembl_paralogues.tsv"  # need to add check that file was downloaded in full; it breaks sometimes depending on ensembl api
    shell:
        "wget -O {output} \'http://www.ensembl.org/biomart/martservice?query=<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE Query><Query virtualSchemaName = \"default\" formatter = \"TSV\" header = \"0\" uniqueRows = \"0\" count = \"\" datasetConfigVersion = \"0.6\" ><Dataset name = \"hsapiens_gene_ensembl\" interface = \"default\" ><Filter name = \"with_hsapiens_paralog\" excluded = \"0\"/><Attribute name = \"ensembl_gene_id\" /> <Attribute name = \"hsapiens_paralog_ensembl_gene\" /> <Attribute name = \"hsapiens_paralog_orthology_type\" /><Attribute name = \"hsapiens_paralog_perc_id\" /><Attribute name = \"hsapiens_paralog_perc_id_r1\" /></Dataset></Query>\'"
#===============================================================================
# Open Targets google cloud files download

# snakemake GS functions not working for some reason for me...decided to use gsutil.
# I've left commented out snippet below in case someone can fix it:
# rule cosmic_evidence_download:
#     input:
#         GSRemoteProvider().remote(cosmic_evidence)
#     output:
#         data_dir + "/OT_data/cosmic_evidence.json"
#     shell:
#         "cat {input} | gunzip > {output}"

# elasticsearch indices:
# Currently pointing to ot-snapshots folder, add '| gunzip' to the shell commands if these are zipped & moved to the ot releases output folder
# Alternative elasticdump command (on running server) if indices not available:
# elasticdump --input=http://localhost:9200/19.09_gene-data --output=19.09_gene-data.json --type=data --limit 10000 --sourceOnly

rule gene_index_download:
    params:
        location=config['gene_index']
    output:
        data_dir + "/OT_data/gene_index.json"
    shell:
        #"gsutil cat {params.location} | gunzip > {output}"
        "gsutil cat {params.location} > {output}"

rule drug_index_download:
    params:
        location=config['drug_index']
    output:
        data_dir + "/OT_data/drug_index.json"
    shell:
        "gsutil cat {params.location} > {output}"

rule expression_index_download:
    params:
        location=config['expression_index']
    output:
        data_dir + "/OT_data/expression_index.json"
    shell:
        "gsutil cat {params.location} > {output}"

# other OT data files
rule gene_mapfile_download:
    params:
        location=config['gene_mapfile']
    output:
        data_dir + "/OT_data/gene_mapfile.json"
    shell:
        "gsutil cat {params.location} | gunzip | jq -c '.' > {output}"

rule OT_associations_download:
    params:
        location=config['OT_associations']
    output:
        data_dir + "/OT_data/OT_associations.json"
    shell:
        "gsutil cat {params.location} | gunzip > {output}"

rule cosmic_evidence_download:
    params:
        location=config['cosmic_evidence']
    output:
        data_dir + "/OT_data/cosmic_evidence.json"
    shell:
        "gsutil cat {params.location} | gunzip > {output}"

rule fda_aes_by_target_download:
    params:
        location=config['fda_aes_by_target']
    output:
        data_dir + "/OT_data/fda_aes_by_target.json"
    shell:
        "gsutil cat {params.location}/part* > {output}" # will probably not need the '/part*' eventually
