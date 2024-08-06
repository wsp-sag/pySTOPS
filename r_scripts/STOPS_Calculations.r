# Step 3. Calculate summaries from CUR tables
## Read summary excel file

Year <- c("CUR/","FUT/")
Scenario <- c(rep(c("HBW",
                    "All Other Purposes",
                    "Special Market 1",
                    "Special Market 1",
                    "Special Market 1",
                    "Special Market 1"
), each = 2), "New Transit Trips",
"Linked Transit TOP", " ", "PMT Difference", "VMT Difference")

rep <- (length(Scenario)-5)/2
Transit_Type <- c(rep(c("Non-Transit Dependents", "Transit Dependents"),times= rep), rep(c("-"),times= 5))
Summary_Table <- data.frame("Scenario" = Scenario,"Transit Type" = Transit_Type)

for (s in Year)
  {
  mainDir <- paste("C:/projects/30901990A_sorta/fta_temp/r56_r57_2019_reading/",s, sep="")
  setwd(mainDir)
  table_nos <- c("10.03", "10.04", "1021.03", "4.02", "4.03", "706.03", "769.03", "8.01", "958.03")
  table <- list()
  rows <- list()
  cols <- list()
  last_value <- list()
      for (i in 1:length(table_nos))
        {
         name <- paste("Table ", table_nos[i], ".csv", sep = "")
         t <- read.csv(name)
         r <- nrow(t)
         c <- ncol(t)

         for (k in 1:r)
           {
             if(t[k,1] == "Total")
              {
               last_row <- k
              }
            }
         m = t[last_row, c]
         table <- c(table, t)
         rows <- c(rows, r)
         cols <- c(cols, c)
         last_value <- c(last_value, as.integer(m))
         }
  names(last_value) <- table_nos
  HBW_NTD = last_value$`769.03`-last_value$`706.03`
  HBW_TD = last_value$`706.03`
  AOP_TD =last_value$`958.03`- HBW_TD
  AOP_NTD = last_value$`1021.03`- HBW_TD - HBW_NTD - AOP_TD
  SM1_NTD = 0
  SM1_TD = 0
  SM2_NTD = 0
  SM2_TD = 0
  SM3_NTD = 0
  SM3_TD = 0
  SM4_NTD = 0
  SM4_TD = 0
  NTT= last_value$`4.02`
  LTTOP = last_value$`4.03`
  PMT_Diff = last_value$`8.01`
  VMT_Diff = last_value$`8.01`/1.1
  values <- c(HBW_NTD,HBW_TD, AOP_NTD, AOP_TD,SM1_NTD,SM1_TD,SM2_NTD, SM2_TD, SM3_NTD,SM3_TD,SM4_NTD, SM4_TD, NTT,LTTOP,0, PMT_Diff, VMT_Diff)

  # Vehicle Assignment
  Peak <- read.csv("Table 10.03.csv") 
  Off_Peak <- read.csv("Table 10.04.csv") 
  r <- nrow(Peak)
  c <- ncol(Peak)
  
  for (k in 1:r)
  {
    if(Peak[k,1] == "Route_ID")
    {start_line <- k+1}
    else if(Peak[k,1] == "Total")
    {end_line <-k} 
  }
  g <- Peak[c(start_line : end_line), 1]
  VehAsg <- data.frame("Route_ID" = Peak[c(start_line : end_line), 1], 
                       "Route Name" = Peak[c(start_line : end_line), 2],
                       "No_Build_PEAK" = Peak[c(start_line : end_line), 7], 
                       "No_Build_OFF PEAK" = Off_Peak[c(start_line : end_line), 7],
                       "Build_PEAK" = Peak[c(start_line : end_line), 10], 
                       "Build_OFF PEAK" = Off_Peak[c(start_line : end_line), 10])  
  
#Create Data frames
  if(s == "CUR/")
    { Summary_Table <- data.frame(Summary_Table, "Current" = values)
      mainDir <- "C:/projects/30901990A_sorta/fta_temp/r56_r57_2019_reading/"
      setwd(mainDir)
      write.csv(VehAsg, "Vehicle Assignment (CUR).csv", na = "", row.names = FALSE, col.names = FALSE)
  }
    
  else if(s == "FUT/")
    {Summary_Table <- data.frame(Summary_Table, "Future" = values)
     mainDir <- "C:/projects/30901990A_sorta/fta_temp/r56_r57_2019_reading/"
     setwd(mainDir)
     write.csv(VehAsg, "Vehicle Assignment (FUT).csv", na = "", row.names = FALSE, col.names = FALSE) 
    }
  
}


print (Summary_Table)

## Create csv
mainDir <- "C:/projects/30901990A_sorta/fta_temp/r56_r57_2019_reading/"
setwd(mainDir)

write.csv(Summary_Table, "Calculations.csv", na = "", row.names = FALSE, col.names = FALSE)              
