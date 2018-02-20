nas <- read.csv("NasdaqReturns.csv")
nasm <- data.matrix(nas)[ ,4:123]
rownames(nasm) <- nas[,1]
nasmt <- t(nasm)

#compute vector ofd mean return of each stock
r <- c()
for (i in 1:nrow(nasm)){
  r[i] <- mean(nasm[i, ])
}

#compute covariance matrix
ncov <- cov(nasmt)

library(reshape2)
allcov <- melt(ncov)
allr <- melt(r)

library(RMySQL)
con <- dbConnect(RMySQL::MySQL(), dbname = 'nasdaq', username = 'root', password = 'root')
#dbListTables(con)
#df_result <- dbGetQuery(con, 'select * from cov')
#str(dbGetQuery(con, 'select * from corr'))

dbSendQuery(con, 'delete from portfolio')

for (i in 1:nrow(allcov)){
  s <- sprintf("insert into cov values ('%s', '%s', %s)",
               allcov[i,1], allcov[i,2], allcov[i,3])
  dbSendQuery(con, s)
}

  for (j in 1:length(r)){
  x <- sprintf("insert into r values ('%s', %s)", rownames(nasm)[j], r[j])
  dbSendQuery(con, x)
}


