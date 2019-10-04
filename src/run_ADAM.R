library(data.table)

# The following script is a copy of the demoScript.R of the AdAM repository
# slightly modified to get the required input from the commandline arguments and write the output into a file.

args <- commandArgs(trailingOnly = TRUE)
if (length(args)==0) {
  stop("The following arguments need to be supplied:\n1) ADAM repository folder (from https://github.com/francescojm/ADAM),\n2) binary dependency score matrix.\ne.g. Rscript run_ADAM.R src/ADAM binary_dep_scores.tsv", call.=FALSE)
  }
ADAM <- args[1]
binaryDepScores <- args[2]
output <- args[3]

source_code <- paste0(ADAM,'/R/ADAM.R')
source(source_code )
#load in binary depletion matrix
data<-as.data.frame(fread(binaryDepScores,header=TRUE))
row.names(data) <- data$Gene
data$Gene <- NULL

# Generate the profiles of number of fitness genes across number of cell lines from observed data and
# corresponding comulative sums.
pprofile<-ADAM.panessprofile(depMat=data,display=FALSE)

# Generate a set of random profiles of number of genes depleted for a number of cell lines and corresponding
# cumulative sums by perturbing observed data.
nullmodel<-ADAM.generateNullModel(depMat=data,ntrials = 1000,display=FALSE)

#load a reference set of essential genes
reffile <- paste0(ADAM,'/data/curated_BAGEL_essential.rdata')
load(reffile)

# Calculate log10 odd ratios of observed/expected profiles of cumulative number of fitness genes in fixed number of cell lines
# Observed values are from the ADAM.panessprofile function and expected are the average of random set from ADAM.generateNullModle
EO<-ADAM.empiricalOdds(observedCumSum = pprofile$CUMsums,simulatedCumSum =nullmodel$nullCumSUM )

# Calculate True positive rates for fitness genes in at least n cell lines in the observed dependency matrix,
# with positive cases from a reference set of essential genes
TPR<-ADAM.truePositiveRate(data,curated_BAGEL_essential)


# Calculate minimum number of cell lines a gene needs to be a fitness gene in order to be considered
# as a core-fitness gene
crossoverpoint<-ADAM.tradeoffEO_TPR(EO,TPR$TPR,test_set_name = 'curated BAGEL essential')

#coreFitnessGenes is the list of genes predicted as core-fitness by AdAM.
coreFitnessGenes<-rownames(data)[rowSums(data)>=crossoverpoint]

coreFitnessGenes<- as.data.frame(coreFitnessGenes)
write.table(coreFitnessGenes, file=output,quote=FALSE, row.names = FALSE)
