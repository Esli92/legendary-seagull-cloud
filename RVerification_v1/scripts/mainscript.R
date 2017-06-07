#Verification

#This program for R takes verification-observation pair files from WRF forecasts and uses the verification R package to get statistics and plots. 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 11-Sep-2016

#------------------Requisites------------------------------------------------------------
#WRF/observations pairs made with mkPairs.sh program.
#The input file should be in 24h/0p5/RESOLUTION/
#verification and plotrix packages must be installed.  


#-----------------Version---------------------------------------------------------------
#v1.0 11/Sep/16 Program is created
#v2.0 Nov/16 Added Taylor diagrams with plotrix, improved labels on conditional quantile, translated to spanish

#----------------Known issues-----------------------------------------------------------
#for custom conditional.quantiles axis labels to work, the function must be modified to remove xlab and ylab.

#-----------------Local directories----------------------------------------------------- 


#-----------------BEGIN PROGRAM--------------------------------------------------------

#Load required libraries
library(verification)
library(plotrix)

# RESOLUCION 0.5

#Cargamos archivo 
DAT5 <- read.table("24h/0p5/05/monthlyPairs/MER_TM_m05.txt",sep = ",", header = TRUE, fill = FALSE)
#Un solo archivo individual
#DAT5 <- read.table("24h/0p5/05/ObsFct_Pairs_TM_XAL_39_5_15.txt",sep = ",", header = TRUE, fill = FALSE)

#Separando las dos columnas
OBS5 <- DAT5$OBSERVACION
FCT5 <- DAT5$PRONOSTICO

#Estadisticas de verificacion
MOD5 <- verify(OBS5,FCT5, frcst.type = "cont", obs.type = "cont")

summary(MOD5)

#Grafico cuantil-cuantil
conditional.quantile(FCT5,OBS5,bins = seq(10,30,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")

cor05 <- cor(OBS5,FCT5,use = "all.obs",method = "pearson")

#Diagrama de Taylor
taylor.diagram(OBS5,FCT5,add=FALSE,col="red",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RESOLUCION 0.25
#Cargamos el archivo
DAT25 <- read.table("24h/0p25/05/monthlyPairs/MER_TM_m05.txt",sep = ",", header = TRUE, fill = FALSE)
#Individual
#DAT25 <- read.table("24h/0p25/05/ObsFct_Pairs_TM_XAL_39_5_15.txt",sep = ",", header = TRUE, fill = FALSE)
OBS25 <- DAT25$OBSERVACION
FCT25 <- DAT25$PRONOSTICO

#Estadisticas de verificacion
MOD25 <- verify(OBS25,FCT25, frcst.type = "cont", obs.type = "cont")

summary(MOD25)

cor25 <- cor(OBS25,FCT25,use = "all.obs",method = "pearson")

#Diagrama de taylor, debe ir antes del Q-Q plot
taylor.diagram(OBS25,FCT25,add=TRUE,col="blue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

#Q-Q plot para esta resolucion.
conditional.quantile(FCT25,OBS25,bins = seq(10,30,2), main = "Grafico Cuantil-Cuantil para Temperatura con WRF inicializado con 0.25",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
