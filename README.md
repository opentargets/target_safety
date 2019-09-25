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

2. To run **one** specific step:
```
snakemake specific_step
```
e.g. : `snakemake clinical_findings`

(To list all available steps (*rules*): `snakemake --list`)

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
  ...
  ```
  collect_drug_info
  known_target_safety
  known_target_safety_tables_download
  FDA_AEs_by_target
  significant_AEs_by_target_step2
  ```
- `tissue_expression`
  ...
- `biofunction_buckets`
  ...
  ```
  flag_essential_genes
  run_ADAM_sanger
  run_ADAM_broad
  ADAM_repository
  DepScore_sanger_download
  DepScore_broad_download
  bagel_download
  ogee_download
  flag_enriched_terms
  critical_terms_download
  ```
- `disease_associations`
  ...
  ```
  rare_diseases
  efo_obo_download
  ```
- `animal_data`
  ...
- `potential_off_targets_paralogues`
  ...
  ```
  ensembl_paralogues_download
  ```
- OT data downloads:
  ```
  gene_index_download
  drug_index_download
  expression_index_download
  gene_mapfile_download
  OT_associations_download
  cosmic_evidence_download
  fda_aes_by_target_download
  ```

  
