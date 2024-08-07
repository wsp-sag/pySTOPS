## Load packages
x <- c("readr", "tidyr", "data.table", "XLConnect")
if (length(setdiff(x, rownames(installed.packages()))) > 0) {
  install.packages(setdiff(x, rownames(installed.packages())))  
}
lapply(x, library,  character.only = TRUE)
rm(x)

#Set Work Directory
gettable <- function(input_dir, ouput_dir, tab){
 setwd(input_dir)
  fname = list.files(pattern = "*.prn$")
  for (fn in fname) { 
    setwd(input_dir)
    ## For each prn, read.
    con <- file(fn, "rt")
    lines <- readLines(con, skipNul = TRUE)
    close(con)
    
    ## Create sub dir for outputs
    scenario <- gsub("*.prn","", fn)
    if(file.exists(file.path(output_dir, scenario))){
    unlink(file.path(output_dir, scenario), recursive = TRUE)
    }
   dir.create(file.path(output_dir, scenario))
   setwd(file.path(output_dir, scenario))
   
    
    ## Extract desired sections with tables 
    flag <- FALSE
    for (ln in lines){
      flag_s <- ifelse(grepl("Table  ", ln), TRUE, FALSE)
      flag_e <- ifelse(grepl("-------------------------------------------------------------------------------------------------------------------------------------" , ln), TRUE, FALSE)
      
      ### Detect start of a table
      if(flag_s){
        tabnum <- gsub("Table\\s*","",ln)
        if(tabnum %in% tab){
          flag <- TRUE
          tabname <- paste(ln, ".txt", sep = "")
        }
      }
      ### Write table until the end
      if(flag){
        if(flag_e){
         flag <- FALSE
          ### Check if has read all tables
          if(grepl(dplyr::last(tab),tabname)){
            break
          }
        }
        else{write(ln, tabname, append = TRUE)
        }
     }
   }
    rm(ln,lines, flag, flag_e, flag_s, fn, con)
    setwd(output_dir)
  }
  
  print("Finished extracting tables")


################################################################################################
  
  # TXT to csv table
  # Set format for each table
  format4 <- c("13.01", "13.02")
  format5 <- c("2.03","2.05", "4.01", "4.02", "4.03", "5.03", "8.01", "97.01", "181.01","265.01", "349.01", "426.01", "429.01","433.01", "434.01", "510.01", "517.01", "601.01", 
               "685.01", "769.01", "769.03", "853.01", "853.03", "937.01", "937.03", "1021.01", "1021.03")
  format6 <- c("11.04")
  format7 <- c("9.01", "10.01","12.01", "518.01", "686.01","854.01", "1022.01")
  format9 <- c("10.03","10.04")
  format10 <- c("2.04")
  
  # Process all tables under directory
  dirs <- list.dirs(output_dir)
  for(dr in dirs[0:length(dirs)]){
    setwd(dr)
    fname = list.files(pattern = "txt")
    for (fn in fname) {  
      scenario <- sub("Table\\s*(.*)\\.txt","\\1", fn)
      tabname <- paste("Table ", scenario, ".csv", sep = "")
      ## Skip rows for different tables and read. HARD CODED NUMBER.
      if(scenario %in% format4) {
        skipn = 4
      } else if (scenario %in% format5) {
        skipn = 5
      } else if (scenario %in% format6) {
        skipn = 6
      } else if (scenario %in% format7) {
        skipn = 7
      } else if (scenario %in% format9) {
        skipn = 9
      } else if (scenario %in% format10) {
        skipn = 10
      } else {
        skipn = 5
        print(paste(tabname, "may not be created correctly. Reason: No available parameter."))
      }

      wids <- fwf_empty(fn,skip = skipn,  skip_empty_rows = TRUE, n=11)
      df <- read_fwf(fn, wids, skip_empty_rows = TRUE)
 
      ##skipn <- grep("===", df$X1)[1]
      ##if(skipn!=5){
        ##wids <- fwf_empty(fn,skip = skipn,  skip_empty_rows = TRUE, n=11)
        ##df <- read_fwf(fn, wids, skip_empty_rows = TRUE)   
      ##}
      
      ## Format table
      df <- df[rowSums(is.na(df)) != ncol(df),]
      df <- df[ grep("===", df$X1, invert = TRUE) , ]
      
      if(scenario %in% c("2.04", "2.05")){
        df$X1 <- gsub(":", "", df$X1)
      }
      if(scenario %in% c("10.01", "10.03", "10.04")){
        df <- separate(df, col = X1, into = c("Route ID", "Route Name"), sep = "--", remove = TRUE, fill = "right")
      }
      if(scenario == "11.04"){
        df[] <- lapply(df, gsub, pattern="\\|", replacement="")
        df <- df[ grep("---", df$X1, invert = TRUE) , ]
      }
      df[,1] <- apply(df[,1], 2,function(x)trimws(x,"r"))
      
      #write.csv(df, tabname, na = "", row.names = FALSE, col.names = FALSE)
      write.table(df, file = tabname, sep = ",", na = "", row.names = FALSE, col.names = FALSE)
    }
  }
  print("CSV Tables are ready!")
}

################################################################################





