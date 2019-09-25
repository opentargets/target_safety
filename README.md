# target_safety
Code for target safety pipeline

## Usage

### Setup

1. Set up local environment with dependencies. 
```
conda env create -n target_safety --file environment.yaml
```
Additional dependencies not available through conda: `gzip` & `gsutil`.

2. Edit configuration file `config.yaml` to update the input/output file locations as well as the required input GoogleSheets information.

3. Authenticate google cloud storage.
```
gcloud auth login
```

### Run pipeline

1. For **final output** run:
`snakemake` or `snakemake target_safety`

This produces the output json file called `target_safety.json` in the output folder. This json file includes all information collected for each of the Open Targets safety buckets (TODO: include documentation link). It is an OT target annotation file and uses ENSEMBL gene ids as keys.

2. To run **one** step specify that rule, e.g. for the `clinical_findings` step:
```
snakemake clinical_findings
```
*(To list all available steps (rules): `snakemake --list`)*

There are 6 main intermediate steps that produce corresponding json files in the intermediate output folder (location defined in the configuration file `config.yaml`):
```
clinical_findings
tissue_expression
biofunction_buckets
disease_associations
animal_data
potential_off_targets_paralogues
```
- `clinical_findings`

  Calls the script `clinical_buckets.py` to collect clinical findings information relevant to target safety by calling functions from `drug_info.py`, `known_target_safety.py`, `helpers.py` & processing the output from `openFDA_MonteCarlo_target.R`. Produces a json file called `clinical_findings.json` in the intermediate output folder.
  
  For a detailed look at each of the 'buckets' in this section you can run each step separately to produce more intermediate output files separately (these files are in most cases not produced unless their respective rule is called directly using snakemake). The corresponding rules are the following:
  
  - `collect_drug_info`: Calls the script `drug_info.py` which parses the Open Targets drug index to get the following information for each target: (i) number of drugs targeting this target in each clinical phase, (ii) withdrawn drugs and black box warning flags for drugs that target each target. It can also query the openFDA API to retrieve the contents of the black box warning if available (defaults to FALSE). Produces the file `drug_info.json` in the intermediate output folder (not produced unless rule explicitly called).
  
  - `known_target_safety`: Calls the script `known_target_safety.py` which parses the manually curated spreadsheets (from OT google drive) with targets with known safety risk information. Produces the file `known_target_safety.json` in the intermediate output folder (not produced unless rule explicitly called).
    
  - `significant_AEs_by_target_MonteCarlo`: Calls the script `openFDA_MonteCarlo_target.R` that takes as input a pre-processed json file with the openFDA adverse event data (FAERS) (Open Targets filters applied, see documentation) and calculates the significance of each event occurring for each **target** using a modified version of the openFDA's own LLR method (TODO: add link). Produces the file `significant_AEs_by_target.csv` in the data folder (always produced, as it is required for the `clinical_findings` section).
  
  - `FDA_AEs_by_target`: Calls the script `FDA_AEs_per_target.py` that reformats the csv output from the rule `significant_AEs_by_target_MonteCarlo` into a json file with ENSEMBL gene ids as keys and sorts the events by the event log-likelihood ratio (llr) in descending order. Produces the file `adverse_effects_per_target.json` in the intermediate output folder (not produced unless rule explicitly called).

- `tissue_expression`

  Calls the script `tissue_expression.py` which parses the Open Targets expression index to flag high expression (*level=3*) in one of the organs marked as important for preliminary safety studies (*endocrine gland, exocrine gland, intestine, sense organ, heart, kidney, lung, reproductive organ, immune organ, brain*) (list to be refined).  Produces a json file called `high_tissue_expression` in the intermediate output folder.
- `biofunction_buckets`
  
  ...
  - `flag_essential_genes`
  - `run_ADAM_sanger`
  - `run_ADAM_broad`
  - `ADAM_repository`
  - `flag_enriched_terms`

- `disease_associations`
  ...
  - `rare_diseases`
  
- `animal_data`

  ...
- `potential_off_targets`

  ...
  
- Input data download rules:
  ```
  gene_index_download
  drug_index_download
  expression_index_download
  gene_mapfile_download
  OT_associations_download
  cosmic_evidence_download
  fda_aes_by_target_download
  known_target_safety_tables_download
  critical_terms_download
  efo_obo_download
  ensembl_paralogues_download  
  DepScore_sanger_download
  DepScore_broad_download
  bagel_download
  ogee_download 
  ```

  
