#Verification for seasons

#This program for R takes verification-observation pair files from WRF forecasts and uses the verification R package to get statistics and plots. 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 11-Sep-2016

#------------------Requisites------------------------------------------------------------
#WRF/observations pairs made with mkPairs.sh program.
#The input file should be in ../24h/0p5/RESOLUTION/
#verification and plotrix packages must be instEMAed.  


#-----------------Version---------------------------------------------------------------
#v1.0 11/Sep/16 Program is created
#v2.0 Nov/16 Added Taylor diagrams with plotrix, improved labels on conditional quantile, translated to spanish

#----------------Known issues-----------------------------------------------------------
#for custom conditional_quantiles axis labels to work, the function must be modified to remove xlab and ylab.

#-----------------Local directories----------------------------------------------------- 


#-----------------BEGIN PROGRAM--------------------------------------------------------

#Load required libraries
library(verification)
library(plotrix)

source("conditional_quantile_esp.R")
#assignInNamespace("conditional_quantile",conditional_quantile,ns="verification")
#-------RED DE ESTACIONES EMA------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# RESOLUCION 0.5

#Cargamos archivo, uno por estacion
DAT5_SEF_EMA <- read.table("../24h/0p5/seasonal/SEF/EMA_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_SEC_EMA <- read.table("../24h/0p5/seasonal/SEC/EMA_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_HUM_EMA <- read.table("../24h/0p5/seasonal/HUM/EMA_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS5_SEF_EMA <- DAT5_SEF_EMA$OBSERVACION
FCT5_SEF_EMA <- DAT5_SEF_EMA$PRONOSTICO

OBS5_SEC_EMA <- DAT5_SEC_EMA$OBSERVACION
FCT5_SEC_EMA <- DAT5_SEC_EMA$PRONOSTICO

OBS5_HUM_EMA <- DAT5_HUM_EMA$OBSERVACION
FCT5_HUM_EMA <- DAT5_HUM_EMA$PRONOSTICO

#Estadisticas de verificacion
MOD5_SEF_EMA <- verify(OBS5_SEF_EMA,FCT5_SEF_EMA, frcst.type = "cont", obs.type = "cont")
MOD5_SEC_EMA <- verify(OBS5_SEC_EMA,FCT5_SEC_EMA, frcst.type = "cont", obs.type = "cont")
MOD5_HUM_EMA <- verify(OBS5_HUM_EMA,FCT5_HUM_EMA, frcst.type = "cont", obs.type = "cont")
summary(MOD5_SEF_EMA)
summary(MOD5_SEC_EMA)
summary(MOD5_HUM_EMA)


#Diagrama de Taylor
jpeg(file = "../plots/seasonal/TAYLOR_NET.jpg", width=700,height=700,units="px",quality=90)
taylor.diagram(OBS5_SEF_EMA,FCT5_SEF_EMA,add=FALSE,col="brown",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_SEC_EMA,FCT5_SEC_EMA,add=TRUE,col="brown1",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_HUM_EMA,FCT5_HUM_EMA,add=TRUE,col="red",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RESOLUCION 0.25
#Cargamos archivo, uno por estacion
DAT25_SEF_EMA <- read.table("../24h/0p25/seasonal/SEF/EMA_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_SEC_EMA <- read.table("../24h/0p25/seasonal/SEC/EMA_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_HUM_EMA <- read.table("../24h/0p25/seasonal/HUM/EMA_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS25_SEF_EMA <- DAT25_SEF_EMA$OBSERVACION
FCT25_SEF_EMA <- DAT25_SEF_EMA$PRONOSTICO

OBS25_SEC_EMA <- DAT25_SEC_EMA$OBSERVACION
FCT25_SEC_EMA <- DAT25_SEC_EMA$PRONOSTICO

OBS25_HUM_EMA <- DAT25_HUM_EMA$OBSERVACION
FCT25_HUM_EMA <- DAT25_HUM_EMA$PRONOSTICO

#Estadisticas de verificacion
MOD25_SEF_EMA <- verify(OBS25_SEF_EMA,FCT25_SEF_EMA, frcst.type = "cont", obs.type = "cont")
MOD25_SEC_EMA <- verify(OBS25_SEC_EMA,FCT25_SEC_EMA, frcst.type = "cont", obs.type = "cont")
MOD25_HUM_EMA <- verify(OBS25_HUM_EMA,FCT25_HUM_EMA, frcst.type = "cont", obs.type = "cont")
summary(MOD25_SEF_EMA)
summary(MOD25_SEC_EMA)
summary(MOD25_HUM_EMA)



#Diagrama de Taylor
taylor.diagram(OBS25_SEF_EMA,FCT25_SEF_EMA,add=TRUE,col="cyan",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS25_SEC_EMA,FCT25_SEC_EMA,add=TRUE,col="cornflowerblue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS25_HUM_EMA,FCT25_HUM_EMA,add=TRUE,col="blue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))




#-----------RED DE ESTACIONES REDMET--------------------------------------------------------------------------------------------------------------------------------------------------------------------

# RESOLUCION 0.5

#Cargamos archivo, uno por estacion
DAT5_SEF_RED <- read.table("../24h/0p5/seasonal/SEF/RED_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_SEC_RED <- read.table("../24h/0p5/seasonal/SEC/RED_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT5_HUM_RED <- read.table("../24h/0p5/seasonal/HUM/RED_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS5_SEF_RED <- DAT5_SEF_RED$OBSERVACION
FCT5_SEF_RED <- DAT5_SEF_RED$PRONOSTICO

OBS5_SEC_RED <- DAT5_SEC_RED$OBSERVACION
FCT5_SEC_RED <- DAT5_SEC_RED$PRONOSTICO

OBS5_HUM_RED <- DAT5_HUM_RED$OBSERVACION
FCT5_HUM_RED <- DAT5_HUM_RED$PRONOSTICO

#Estadisticas de verificacion
MOD5_SEF_RED <- verify(OBS5_SEF_RED,FCT5_SEF_RED, frcst.type = "cont", obs.type = "cont")
MOD5_SEC_RED <- verify(OBS5_SEC_RED,FCT5_SEC_RED, frcst.type = "cont", obs.type = "cont")
MOD5_HUM_RED <- verify(OBS5_HUM_RED,FCT5_HUM_RED, frcst.type = "cont", obs.type = "cont")
summary(MOD5_SEF_RED)
summary(MOD5_SEC_RED)
summary(MOD5_HUM_RED)


#Diagrama de Taylor
taylor.diagram(OBS5_SEF_RED,FCT5_SEF_RED,add=TRUE,col="brown",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_SEC_RED,FCT5_SEC_RED,add=TRUE,col="brown1",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS5_HUM_RED,FCT5_HUM_RED,add=TRUE,col="red",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RESOLUCION 0.25
#Cargamos archivo, uno por estacion
DAT25_SEF_RED <- read.table("../24h/0p25/seasonal/SEF/RED_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_SEC_RED <- read.table("../24h/0p25/seasonal/SEC/RED_SEC_TM.txt",sep = ",", header = TRUE, fill = FALSE)
DAT25_HUM_RED <- read.table("../24h/0p25/seasonal/HUM/RED_HUM_TM.txt",sep = ",", header = TRUE, fill = FALSE)


#Separando las dos columnas
OBS25_SEF_RED <- DAT25_SEF_RED$OBSERVACION
FCT25_SEF_RED <- DAT25_SEF_RED$PRONOSTICO

OBS25_SEC_RED <- DAT25_SEC_RED$OBSERVACION
FCT25_SEC_RED <- DAT25_SEC_RED$PRONOSTICO

OBS25_HUM_RED <- DAT25_HUM_RED$OBSERVACION
FCT25_HUM_RED <- DAT25_HUM_RED$PRONOSTICO

#Estadisticas de verificacion
MOD25_SEF_RED <- verify(OBS25_SEF_RED,FCT25_SEF_RED, frcst.type = "cont", obs.type = "cont")
MOD25_SEC_RED <- verify(OBS25_SEC_RED,FCT25_SEC_RED, frcst.type = "cont", obs.type = "cont")
MOD25_HUM_RED <- verify(OBS25_HUM_RED,FCT25_HUM_RED, frcst.type = "cont", obs.type = "cont")
summary(MOD25_SEF_RED)
summary(MOD25_SEC_RED)
summary(MOD25_HUM_RED)



#Diagrama de Taylor
taylor.diagram(OBS25_SEF_RED,FCT25_SEF_RED,add=TRUE,col="cyan",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))

taylor.diagram(OBS25_SEC_RED,FCT25_SEC_RED,add=TRUE,col="cornflowerblue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))


taylor.diagram(OBS25_HUM_RED,FCT25_HUM_RED,add=TRUE,col="blue",pch=19,pos.cor=TRUE,
               xlab="Desviacion Estandar (°C)",ylab="Desviacion Estandar (°C)",main="Diagrama de Taylor",show.gamma=TRUE,ngamma=3,
               gamma.col=8,sd.arcs=0,ref.sd=FALSE,sd.method="sample",
               grad.corr.lines=c(0.2,0.4,0.6,0.8,0.9),
               pcex=1,cex.axis=1,normalize=FALSE,mar=c(5,4,6,6))
dev.off()

#Grafico cuantil-cuantil
jpeg(file = "../plots/seasonal/SEF_RED_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_SEF_RED,OBS25_SEF_RED,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas frias RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/SEC_RED_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_SEC_RED,OBS25_SEC_RED,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas calidas RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/HUM_RED_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_HUM_RED,OBS25_HUM_RED,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 lluvias RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
#Grafico cuantil-cuantil
jpeg(file = "../plots/seasonal/SEF_EMA_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_SEF_EMA,OBS25_SEF_EMA,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas frias EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/SEC_EMA_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_SEC_EMA,OBS25_SEC_EMA,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 secas calidas EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/HUM_EMA_25.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT25_HUM_EMA,OBS25_HUM_EMA,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.25 lluvias EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
#Grafico cuantil-cuantil
jpeg(file = "../plots/seasonal/SEF_RED_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_SEF_RED,OBS5_SEF_RED,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas frias RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/SEC_RED_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_SEC_RED,OBS5_SEC_RED,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas calidas RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/HUM_RED_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_HUM_RED,OBS5_HUM_RED,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 lluvias RED",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
#Grafico cuantil-cuantil
jpeg(file = "../plots/seasonal/SEF_EMA_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_SEF_EMA,OBS5_SEF_EMA,bins = seq(-4,40,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas frias EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/SEC_EMA_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_SEC_EMA,OBS5_SEC_EMA,bins = seq(-2,46,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 secas calidas EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()
jpeg(file = "../plots/seasonal/HUM_EMA_50.jpg", width=850,height=750,units="px",quality=90)
conditional_quantile(FCT5_HUM_EMA,OBS5_HUM_EMA,bins = seq(0,42,2), main = "Grafico Cuantil-Cuantil WRF inicializado con 0.5 lluvias EMA",ylab = "Valor Observado (°C)", xlab = "Valor pronosticado (°C)")
dev.off()


#-------------------------------------------TABLAS DE CONTINGENCIA------------------------------------------------
#Primer paso es decidir los intervalos. Es util saber el maximo y minimo de obs y pronosticos 
MaxObs <- max(OBS25_SEF_RED)