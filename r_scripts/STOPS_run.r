# Step 1. Get input ready

#Rename the PRN files to "CUR" if current year and "FUT" if future year

# Supported tables including "2.03","2.04", "2.05", "4.01", "4.02", "4.03", "5.03", "8.01", "9.01", "10.01", "10.03", "10.04", "11.04", 
# "12.01", "13.01", "13.02", "97.01", "181.01", "265.01", "349.01", "433.01", "517.01", "601.01", "685.01", "769.01", "769.03", "853.01", 
# "853.03", "937.01", "937.03", "1021.01", "1021.03"

## Type the location of prn file and desired table numbers.
mainDir <- "C:/Users/ATTURU/Documents/projects/27612.2720_sorta_cig/fta_temp/r6_hamilton_alt1/"
tab <- c("4.02", "4.03", "8.01", "10.03", "10.04", "706.03", "769.03", "958.03", "1021.03")

## Source R function
source("C:/Users/ATTURU/Documents/projects/27612.2720_sorta_cig/fta_temp/STOPS.R")

## Extract tables
gettable(mainDir,tab)

# Step 2. Combine all CSV into one XLSX
## Create output spreadsheet
setwd(mainDir)
output <- paste(mainDir, "/Summary.xlsx", sep = "")
wb <- loadWorkbook(output, create=TRUE)
fname = list.files(pattern = ".prn")

## Read current/future scenario CSV
for(fn in fname){
setwd(mainDir)
scenario <- gsub(".prn","", fn)
dir <- paste(mainDir, scenario, sep = "/")
setwd(dir)
  
CSVname <- list.files(pattern = ".csv")
tabname <- lapply(CSVname, function(x) paste(scenario, x))
tabname <- lapply(tabname, function(x) gsub(".csv", "",x))
names(CSVname) <- tabname

## Write CSV to workbook 
for (nm in tabname) {
    ## ingest the CSV file
    temp_DT <- fread(CSVname[[nm]])
    
    ## Create the sheet where the file will be outputed to 
    createSheet(wb, name=nm)
    
    ## output the csv contents
    writeWorksheet(object=wb, data=temp_DT, sheet=nm, header=TRUE, rownames=NULL)
  } 
  ## If you see warning message saying JAVA running out of space, that's because R studio can only use space allocated to the software. 
  ## Solution is to clean the environment and close R studio. Re-run step 2 only.
  
saveWorkbook(wb)
}

  
