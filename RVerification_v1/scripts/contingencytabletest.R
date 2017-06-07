#Verification for CATEGORIES, using contingency tables

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
#------------------------------------------------------------------------------------------------------------------
#                                                 RESOLUCION 0.25
#------------------------------------------------------------------------------------------------------------------
#Cargamos archivo de datos
DAT25 <- read.table("../24h/0p25/seasonal/SEF/RED_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)

#Separando las dos columnas
OBS25 <- DAT25$OBSERVACION
FCT25 <- DAT25$PRONOSTICO

#-------------------------------------------TABLAS DE CONTINGENCIA------------------------------------------------
#Primer paso es decidir los intervalos. Es util saber el maximo y minimo de obs y pronosticos 
MaxObs <- max(OBS25)
MinObs <- min(OBS25)
MaxFCT <- max(FCT25)
MinFCT <- min(FCT25)

MinClim <- 8.5
MeanClim <- 15.5
MaxClim <- 22

a <- floor(MinObs) - 40  
b <- floor(MinObs) - 30
c <- floor(MinObs) - 20
d <- floor(MinObs) - 10

#Vamos a convertir los valores continuos en valores discretos
ObsDisc <- quantile2disc(OBS25,c(MinObs,MinClim,MeanClim,MaxClim,MaxObs))
Obsd <- ObsDisc$new
Obsm <- ObsDisc$mids

#Ahora cambiamos los valores discretos por categorias:
Obsd <- replace(Obsd,Obsd>floor(Obsm[4]),d)
Obsd <- replace(Obsd,Obsd>floor(Obsm[3]),c)
Obsd <- replace(Obsd,Obsd>floor(Obsm[2]),b)
Obsd <- replace(Obsd,Obsd>floor(Obsm[1]),a)

Obsd <- replace(Obsd,Obsd==a,1)
Obsd <- replace(Obsd,Obsd==b,2)
Obsd <- replace(Obsd,Obsd==c,3)
Obsd <- replace(Obsd,Obsd==d,4)

Obsd25 <- Obsd

FctDisc <- quantile2disc(FCT25,c(MinFCT,MinClim,MeanClim,MaxClim,MaxFCT))
Fctd <- FctDisc$new 
Fctm <- FctDisc$mids
Fctd <- replace(Fctd,Fctd>floor(Fctm[4]),d)
Fctd <- replace(Fctd,Fctd>floor(Fctm[3]),c)
Fctd <- replace(Fctd,Fctd>floor(Fctm[2]),b)
Fctd <- replace(Fctd,Fctd>floor(Fctm[1]),a)

Fctd <- replace(Fctd,Fctd==a,1)
Fctd <- replace(Fctd,Fctd==b,2)
Fctd <- replace(Fctd,Fctd==c,3)
Fctd <- replace(Fctd,Fctd==d,4)

Fctd25 <- Fctd

#--------------------------------------VERIFICACION----------------------------------------------------------------
VER25 <- verify(Obsd25,Fctd25,obs.type = "cat", frcst.type = "cat")
summary(VER25)

#------------------------------------------------------------------------------------------------------------------
#                                                 RESOLUCION 0.50
#------------------------------------------------------------------------------------------------------------------
#Cargamos archivo de datos
DAT50 <- read.table("../24h/0p5/seasonal/SEF/RED_SEF_TM.txt",sep = ",", header = TRUE, fill = FALSE)

#Separando las dos columnas
OBS50 <- DAT50$OBSERVACION
FCT50 <- DAT50$PRONOSTICO

#-------------------------------------------TABLAS DE CONTINGENCIA------------------------------------------------
#Primer paso es decidir los intervalos. Es util saber el maximo y minimo de obs y pronosticos 
MaxObs <- max(OBS50)
MinObs <- min(OBS50)
MaxFCT <- max(FCT50)
MinFCT <- min(FCT50)

MinClim <- 8.5
MeanClim <- 15.5
MaxClim <- 22

a <- floor(MinObs) - 40  
b <- floor(MinObs) - 30
c <- floor(MinObs) - 20
d <- floor(MinObs) - 10

#Vamos a convertir los valores continuos en valores discretos
ObsDisc <- quantile2disc(OBS50,c(MinObs,MinClim,MeanClim,MaxClim,MaxObs))
Obsd <- ObsDisc$new
Obsm <- ObsDisc$mids

#Ahora cambiamos los valores discretos por categorias:
Obsd <- replace(Obsd,Obsd>floor(Obsm[4]),d)
Obsd <- replace(Obsd,Obsd>floor(Obsm[3]),c)
Obsd <- replace(Obsd,Obsd>floor(Obsm[2]),b)
Obsd <- replace(Obsd,Obsd>floor(Obsm[1]),a)

Obsd <- replace(Obsd,Obsd==a,1)
Obsd <- replace(Obsd,Obsd==b,2)
Obsd <- replace(Obsd,Obsd==c,3)
Obsd <- replace(Obsd,Obsd==d,4)

Obsd50 <- Obsd

FctDisc <- quantile2disc(FCT50,c(MinFCT,MinClim,MeanClim,MaxClim,MaxFCT))
Fctd <- FctDisc$new 
Fctm <- FctDisc$mids
Fctd <- replace(Fctd,Fctd>floor(Fctm[4]),d)
Fctd <- replace(Fctd,Fctd>floor(Fctm[3]),c)
Fctd <- replace(Fctd,Fctd>floor(Fctm[2]),b)
Fctd <- replace(Fctd,Fctd>floor(Fctm[1]),a)

Fctd <- replace(Fctd,Fctd==a,1)
Fctd <- replace(Fctd,Fctd==b,2)
Fctd <- replace(Fctd,Fctd==c,3)
Fctd <- replace(Fctd,Fctd==d,4)

Fctd50 <- Fctd

#--------------------------------------VERIFICACION----------------------------------------------------------------
VER50 <- verify(Obsd50,Fctd50,obs.type = "cat", frcst.type = "cat")
summary(VER50)
