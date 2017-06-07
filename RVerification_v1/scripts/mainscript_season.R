#Verification for seasons

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

#Cargamos archivo, uno por estacion
DAT5_SEF <- read.table("24h/0p5/seasonal/SEF/ALL_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_SEC <- read.table("24h/0p5/seasonal/SEC/ALL_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_HUM <- read.table("24h/0p5/seasonal/HUM/ALL_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS5_SEF <- DAT5_SEF$OBSERVACION
FCT5_SEF <- DAT5_SEF$PRONOSTICO

OBS5_SEC <- DAT5_SEC$OBSERVACION
FCT5_SEC <- DAT5_SEC$PRONOSTICO

OBS5_HUM <- DAT5_HUM$OBSERVACION
FCT5_HUM <- DAT5_HUM$PRONOSTICO

#Estadisticas de verificacion
MOD5_SEF <- verify(OBS5_SEF,FCT5_SEF, frcst.type = "cont", obs.type = "cont")
MOD5_SEC <- verify(OBS5_SEC,FCT5_SEC, frcst.type = "cont", obs.type = "cont")
MOD5_HUM <- verify(OBS5_HUM,FCT5_HUM, frcst.type = "cont", obs.type = "cont")
summary(MOD5_SEF)
summary(MOD5_SEC)
summary(MOD5_HUM)

#Grafico cuantil-cuantil
conditional.quantile(FCT5_SEF,OBS5_SEF,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas frias",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
conditional.quantile(FCT5_SEC,OBS5_SEC,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas calidas",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
conditional.quantile(FCT5_HUM,OBS5_HUM,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 lluvias",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")


#Diagrama de Taylor
taylor.diagram(OBS5_SEF,FCT5_SEF,add=FALSE,col="brown",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_SEC,FCT5_SEC,add=TRUE,col="brown1",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_HUM,FCT5_HUM,add=TRUE,col="red",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RESOLUCION 0.25
#Cargamos archivo, uno por estacion
DAT25_SEF <- read.table("24h/0p25/seasonal/SEF/ALL_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_SEC <- read.table("24h/0p25/seasonal/SEC/ALL_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_HUM <- read.table("24h/0p25/seasonal/HUM/ALL_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS25_SEF <- DAT25_SEF$OBSERVACION
FCT25_SEF <- DAT25_SEF$PRONOSTICO

OBS25_SEC <- DAT25_SEC$OBSERVACION
FCT25_SEC <- DAT25_SEC$PRONOSTICO

OBS25_HUM <- DAT25_HUM$OBSERVACION
FCT25_HUM <- DAT25_HUM$PRONOSTICO

#Estadisticas de verificacion
MOD25_SEF <- verify(OBS25_SEF,FCT25_SEF, frcst.type = "cont", obs.type = "cont")
MOD25_SEC <- verify(OBS25_SEC,FCT25_SEC, frcst.type = "cont", obs.type = "cont")
MOD25_HUM <- verify(OBS25_HUM,FCT25_HUM, frcst.type = "cont", obs.type = "cont")
summary(MOD25_SEF)
summary(MOD25_SEC)
summary(MOD25_HUM)



#Diagrama de Taylor
taylor.diagram(OBS25_SEF,FCT25_SEF,add=TRUE,col="cyan",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS25_SEC,FCT25_SEC,add=TRUE,col="cornflowerblue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS25_HUM,FCT25_HUM,add=TRUE,col="blue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

#Grafico cuantil-cuantil
conditional.quantile(FCT25_SEF,OBS25_SEF,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas frias",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
conditional.quantile(FCT25_SEC,OBS25_SEC,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas calidas",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
conditional.quantile(FCT25_HUM,OBS25_HUM,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 lluvias",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
