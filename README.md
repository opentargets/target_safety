# target_safety
Code for target safety pipeline in Open Targets. 

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

1. For **complete output**, run:
`snakemake` or `snakemake target_safety`

This produces the Open Targets target safety annotation file called `target_safety.json` in the output folder. This json file includes all information collected for each of the OT safety buckets (TODO: include documentation link). It is produced by calling the script `target_safety.py` which merges the output from the six different scripts `clinical_buckets.py`, `tissue_expression.py`, `bio_function_buckets.py`, `disease_associations.py`, `animal_data.py` and `paralogues.py` into a single json that uses ENSEMBL gene ids as keys.   

2. To run **one** step specify that rule, e.g. for the `clinical_findings` step:
```
snakemake clinical_findings
```
*(To list all available steps (rules): `snakemake --list`)*

There are 6 main intermediate rules that produce corresponding json files in the intermediate output folder (define location in the configuration file `config.yaml`):
```
clinical_findings
tissue_expression
biofunction_buckets
disease_associations
animal_data
potential_off_targets_paralogues
```
- `clinical_findings`

  Calls the script `clinical_buckets.py` to collect clinical findings information relevant to target safety by calling functions from `drug_info.py`, `known_target_safety.py`, `FDA_AEs_per_target.py` & processing the output from `openFDA_MonteCarlo_target.R`. Produces a json file called `clinical_findings.json` in the intermediate output folder.
  
  For a detailed look at each of the 'buckets' in this section you can run each step separately to produce more intermediate output files separately (these files are in most cases not produced unless their respective rule is called directly using snakemake). The corresponding rules are the following:
  
  - `collect_drug_info`: Calls the script `drug_info.py` which parses the Open Targets drug index to get the following information for each target: (i) number of drugs targeting this target in each clinical phase, (ii) withdrawn drugs and (iii) black box warning flags for drugs that target each target. It can also query the openFDA API to retrieve the contents of the black box warning if available (defaults to FALSE). Produces the file `drug_info.json` in the intermediate output folder (not produced unless rule explicitly called).
  
  - `known_target_safety`: Calls the script `known_target_safety.py` which parses the manually curated spreadsheets (from OT google drive) with targets with known safety risk information. Produces the file `known_target_safety.json` in the intermediate output folder (not produced unless rule explicitly called).
    
  - `significant_AEs_by_target_MonteCarlo`: Calls the script `openFDA_MonteCarlo_target.R` that takes as input a pre-processed json file with the openFDA adverse event data (FAERS) (Open Targets filters applied, see relevant [documentation](https://github.com/opentargets/platform-etl-openfda-faers)) and calculates the significance of each event occurring for each **target** using a modified version of the openFDA's own [LRT method](https://openfda.shinyapps.io/LRTest/_w_c5c2d04d/lrtmethod.pdf). Produces the file `significant_AEs_by_target.csv` in the data folder (always produced, as it is required for the `clinical_findings` section).
  
  - `FDA_AEs_by_target`: Calls the script `FDA_AEs_per_target.py` that reformats the csv output from the rule `significant_AEs_by_target_MonteCarlo` into a json file with ENSEMBL gene ids as keys and sorts the events by the event log-likelihood ratio (llr) in descending order. Produces the file `adverse_effects_per_target.json` in the intermediate output folder (not produced unless rule explicitly called).

- `tissue_expression`

  Calls the script `tissue_expression.py` which parses the Open Targets expression index to flag high expression (*level=3*) in one of the organs marked as important for preliminary safety studies (*endocrine gland, exocrine gland, intestine, sense organ, heart, kidney, lung, reproductive organ, immune organ, brain*) (list to be refined).  Produces a json file called `high_tissue_expression.json` in the intermediate output folder.
- `biofunction_buckets`

  Calls the script `bio_function_buckets.py` to collect biological function information for the target that might be relevant to its safety as a drug target. It calls functions from `essential_genes.py` and `flag_GO_React_terms.py` and produces a json file called `biofunction.json` in the intermediate output folder. 
  
  Similar to the `clinical_findings` rule, you can run each step separately to produce more intermediate output files separately. The corresponding rules are the following:
  
  - `flag_essential_genes`: Calls the script `essential_genes.py` which combines the lists of essential genes derived from the [Cancer Dependency Map](https://score.depmap.sanger.ac.uk) (output from script `run_ADAM.R`), the  [Toronto Knockout Library](http://tko.ccbr.utoronto.ca/) (simple download of BAGEL list) and [OGEE](http://ogee.medgenius.info/browse/) (script consolidates results from all human datasets in the same manner as OGEE). Produces a json file called `essential_genes.json` in the intermediate output folder (not produced unless rule explicitly called).
  
  - `run_ADAM_sanger`: Calls the script `run_ADAM.py` (which uses functions from the [AdAM](https://github.com/francescojm/ADAM) repository) to calculate which genes should be flagged as core fitness using the [Sanger binary dependency scores matrix](https://score.depmap.sanger.ac.uk/downloads). Produces the txt file `coreFitnessADAM_Sanger.txt` with this list of essential genes (always produced, required for `biofunction_buckets`).
  
  - `run_ADAM_broad`: Calls the script `run_ADAM.py` (which uses functions from the [AdAM](https://github.com/francescojm/ADAM) repository) to calculate which genes should be flagged as core fitness using the [Broad binary dependency scores matrix](https://score.depmap.sanger.ac.uk/downloads). Produces the txt file `coreFitnessADAM_Broad.txt` with this list of essential genes (always produced, required for `biofunction_buckets`).
  
  - `flag_enriched_terms`: Calls the script `flag_GO_React_terms.py` which collects the lists of the enriched (GSE) GO and Reactome terms that are associated with different target safety questions from the OT spreadsheets (OT google drive) and then it parses the OT gene index to flag a gene if it is annotated with one of these terms. Produces a json file called `flagged_terms.json` in the intermediate output folder (not produced unless rule explicitly called).

- `disease_associations`: 

  Calls the script `disease_associations.py` which parses the Open Targets associations file and the list of rare diseases (output from `rare_diseases.py`) to collect the following information on the diseases which are highly associated (>= 0.75 overall association score, direct associations only) with each target: (i) therapeutic areas these diseases belong to, (ii) whether they are marked as a rare disease. It also parses the OT cosmic evidence file to flag targets that are marked as cancer genes from [COSMIC](https://cancer.sanger.ac.uk/cosmic). Produces a json file called `disease_associations.json` in the intermediate output folder.

  - `rare_diseases`: Calls the script `rare_diseases.py` which first parses the EFO obo file to find diseases whose EFO terms belong to the Orphanet ontology as well, or have an Orphanet cross-reference. It then parses the OT associations file to mark as rare the Orphanet terms that have at least one type of evidence from EVA or Genomics England in Open Targets. Produces the list of rare diseases (EFO terms) in a txt file called `rare_diseases.txt` in the data folder (always produced, required for `disease_associations`). 
  
- `animal_data`
  
  Calls the script `animal_data.py` to parse the OT gene index and extract the following information: (i) The mouse model MGI ids for any available knockout mouse models for this target, (ii) For which among the species among the 'clinically relevant species list' (currently *human, mouse, pig, dog, macaque, rat, guinea pig, rabbit and chimpanzee*; list needs refinement) do we have ortholog information already in Open Targets. 
  
- `potential_off_targets`

  Calls the script `paralogues.py` and parses the file of all the ENSEMBL human paralogues to extract information for paralogues with a >= 80% identity (either of the query target gene, or of the paralogue)
  
  
- Input data download rules:
  - OT data in json format: Need access to Open Targets Google Gloud, rules use `gsutil`:
      ```
      gene_index_download
      drug_index_download
      expression_index_download
      gene_mapfile_download
      OT_associations_download
      cosmic_evidence_download
      fda_aes_by_target_download
      ```
  - OT Google Spreadsheet data: rules use `GoogleSpreadSheet.py`. Spreadsheet google key and gid need to be defined in the configuration file. 
      ```
      known_target_safety_tables_download
      critical_terms_download
      ```
  - External downloads: non-OT data, rules use simple `wget`.
      ```
      efo_obo_download
      ensembl_paralogues_download  
      DepScore_sanger_download
      DepScore_broad_download
      bagel_download
      ogee_download 
      ```

  
