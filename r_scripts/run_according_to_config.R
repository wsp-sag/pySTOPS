#Sys.setenv(PATH = paste("C:/Rtools/bin", Sys.getenv("PATH"), sep=";"))
#Sys.setenv(BINPREF = "C:/Rtools/mingw_$(WIN)/bin/")

#install.packages("renv")
#library(renv)
#renv::restore()

install.packages("yaml")
library(yaml)

cwd <- getwd()
# should not need this line in the near futures
# hopefully R portable 

parameters = yaml.load_file(paste0(cwd, "/config.yml"))

# use gsub to comply with windows paths, just make it
input_dir <- gsub("\\\\", "/", parameters["input_dir"]) 
output_dir <- gsub("\\\\", "/", parameters["output_dir"])
tables <- parameters["tables_to_output"][[1]]

read_prn_path = paste0(cwd, "/STOPS.R")
source(read_prn_path)

process_table_path = paste0(cwd, "/STOPS_run.r")
source(process_table_path)

summary_calculations_path = paste0(cwd, "/STOPS_Calculations.r")
source(summary_calculations_path)

print("Post Process successfully exported:")
print(output_dir)


Sys.setenv(JAVA_HOME='C:/Program Files/Java/jre1.8.0_121')
Sys.getenv("JAVA_HOME")
