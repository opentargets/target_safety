library(data.table)
library(tidyverse)
library(jsonlite)

# Takes as input a pre-processed json file with the openFDA adverse event data (FAERS)
# and calculates the significance of each event occurring for each TARGET using a modified version of the openFDA's own LRT method (Monte Carlo simulations).
# (https://openfda.shinyapps.io/LRTest/_w_c5c2d04d/lrtmethod.pdf)

# Input files from command line arguments
args <- commandArgs(trailingOnly = TRUE)
if (length(args)==0) {
  stop("The following arguments need to be supplied:\n1) openFDA FAERS processed output json file(Open Targets pipeline, by target),\n2) output csv file name.\ne.g. Rscript openFDA_MonteCarlo_target.R fda_aes_by_target.json output.csv", call.=FALSE)
  }
openFDA_data_process_output <- args[1]
output_csv <- args[2]

# Read in processed output from openFDA adverse event data dump
FDAdata <- stream_in(file(openFDA_data_process_output))%>%
  distinct() %>%
  mutate(totalreports = A+B+C+D,
         pvector = uniq_report_ids_by_reaction/totalreports)

# Run Montel Carlo simulations to get critical value for each target id
# openFDA functions (modified for efficiency)
getCritVal <- function(R, n_j, n_i, n, Pvector, prob){
  I <- length(Pvector)
  Simulatej<-rmultinom(R,size=n_j,prob=Pvector)
  myLLRs <- t(sapply(1:length(Pvector), function(i){
    logLRnum(Simulatej[i, ], n_i[i], n_j, n)
  }))
  myLLRs <- myLLRs - n_j * log(n_j) + n_j * log(n)
  myLLRs[is.na(myLLRs)] <- 0
  mymax <- apply(myLLRs, 2, max)
  critval <- quantile(mymax,  probs = prob)
  return(critval)
}

logLRnum<-function(x, y, z, n){
  logLR <- x * (log(x) - log(y)) + (z-x) * (log(z - x) - log(n - y))
  return(logLR)
}

# one critval per target id
permutations <- 1000
prob <- 0.95
FDAdata <- FDAdata %>%
  group_by(target_id) %>%
  mutate(critval = getCritVal(permutations,
                              uniq_report_ids_by_target[1],
                              uniq_report_ids_by_reaction,
                              totalreports[1],
                              pvector,
                              prob)) %>%
  mutate(significant = llr > critval)

# keep only significant rows
FDAdata <- FDAdata[FDAdata$significant ==TRUE,] %>% drop_na()

# keep only the following columns
myvars <-c("target_id", "reaction_reactionmeddrapt", "A", "llr", "critval")
output <- FDAdata[myvars]
colnames(output ) <- c("target_id", "event", "report_count", "llr", "critval")

write.csv(output,file=output_csv,row.names=FALSE)
