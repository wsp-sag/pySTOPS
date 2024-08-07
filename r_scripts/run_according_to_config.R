install.packages("yaml")
library(yaml)

cwd <- getwd()
cwd = "C:\Users\USLP095001\code\pytstops\pySTOPS\r_scripts"
foo = yaml.load_file(paste0(cwd, "/config.yml"))

foo[[2]][2]
