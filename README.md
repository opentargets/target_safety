# target_safety
Code for target safety pipeline

## Usage

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

4. Run pipeline:
- For **full run**:
```
snakemake
```
- To run **one** specific step:
  ```
  snakemake specific_step
  ```
  e.g. : `snakemake clinical_findings`
  
  To list available steps (**rules**): `snakemake --list`
  ```
  all
  clinical_findings
  collect_drug_info
  known_target_safety
  known_target_safety_tables_download
  FDA_AEs_by_target
  significant_AEs_by_target_step2
  tissue_expression
  biofunction_buckets
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
  disease_associations
  rare_diseases
  efo_obo_download
  animal_data
  potential_off_targets_paralogues
  ensembl_paralogues_download
  gene_mapfile_download
  OT_associations_download
  cosmic_evidence_download
  ```

  
