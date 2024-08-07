#install.packages("yaml")
library(yaml)

cwd <- getwd()
# should not need this line in the near futures
# hopefully R portable 
cwd = "C:/Users/USLP095001/code/pytstops/pySTOPS/r_scripts"

parameters = yaml.load_file(paste0(cwd, "/config.yml"))

# use gsub to comply with windows paths, just make it
#input_dir <- gsub("\\\\", "/", parameters["input_dir"]) 
#output_dir <- gsub("\\\\", "/", parameters["output_dir"])
#tables <- parameters["tables_to_output"]

input_dir <- "C:/Users/USLP095001/code/pytstops/pySTOPS/r_scripts/example_input"
output_dir <- "C:/Users/USLP095001/code/pytstops/pySTOPS/r_scripts/example_output"
tables <- c("4.02", "4.03", "8.01", "10.03", "10.04", "706.03", "769.03", "958.03", "1021.03")

read_prn_path = paste0(cwd, "/STOPS.R")
source(read_prn_path)

process_table_path = paste0(cwd, "/STOPS_run.r")
source(process_table_path)

summary_calculations_path = paste0(cwd, "/STOPS_Calculations.r")
source(summary_calculations_path)
