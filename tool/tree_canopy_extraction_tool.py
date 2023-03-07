#########################################################################
# Tree Canopy Extraction Using LIDAR and NDVI for 3D Map Tree Masking
# Author: Aaron Taveras
# Date Created: 3/4/2017, Updated 3/2/2023
# Debugging only works with Python 3.x, ArcGIS Pro, and Spatial Analyst installed
#########################################################################

import sys #include system specific parameters and functions
import os #include os library

import arcpy, string #include ArcGIS Python library
from arcpy import env #include ArcGIS Python Environment module
from arcpy.sa import* #include ArcGIS Spatial Analyst module

#########################################################################
## Create folder for intermediate processing files
#########################################################################

InterFolder=r"C:/Temp/Ext_Tool_Temp" #follow this path to locate processing files
if not os.path.exists(InterFolder):
    os.makedirs(InterFolder)

#########################################################################
## Mini function to send the print messages to the right output
## Input: Message-string to be printed
#########################################################################

def MyPrint(Message):
    if (RunningInArcPro): arcpy.AddMessage(Message)
    else: print(Message)

#########################################################################
## Determine if we are running within ArcGIS Pro (as a tool) or not
#########################################################################

RunningInArcPro=False #assume we are not running as a tool in ArcGIS Pro

if (len(sys.argv))>1: #if parameters are present, run in ArcGIS Pro as a tool
    RunningInArcPro=True

#########################################################################
## Setup default parameters and then get the parameters from the argument
## List if we are running as a tool in ArcGIS Pro.
#########################################################################

MyPrint("""###############################################
Input and output File paths
###############################################""")

#########################################################################
# All input paths
#########################################################################

HhInput="C:/Temp/hh.img" #input path for highest hit lidar raster
BeInput="C:/Temp/be.img" #input path for bare earth lidar raster
NAIP="C:/Temp/naip.img" #input path for 4-band NAIP image

#########################################################################
# All output paths
#########################################################################

NonGroundOutput="C:/Temp/Ext_Tool_Temp/non_ground.img" #default output path for non-ground raster
HeightReclassOutput="C:/Temp/Ext_Tool_Temp/hgtrecout.img" #default output path for non-ground height raster
red="C:/Temp/Ext_Tool_Temp/red.img" #default output path for visual red band image
nir="C:/Temp/Ext_Tool_Temp/nir.img" #default output path for NIR band image
ndvi="C:/Temp/Ext_Tool_Temp/ndvi.img" #default output path for NDVI raster
ndviReclassOutput="C:/Temp/Ext_Tool_Temp/ndvirecout.img" #default output path reclassified NDVI raster
CanopyOutput="C:/Temp/Ext_Tool_Temp/canopyout.img" #default output path for final canopy raster

#########################################################################
# If running in a tool, get the parameters from the ArcGIS Pro tool GUI
#########################################################################

if (RunningInArcPro): #if running in a tool, get the parameters from the ArcGIS Pro tool GUI
    HhInput=arcpy.GetParameterAsText(0) #sets parameter for highest hit input in ArcGIS Pro
    BeInput=arcpy.GetParameterAsText(1) #sets parameter for bare earth input in ArcGIS Pro
    NAIP=arcpy.GetParameterAsText(2) #sets parameters for NIR image input in ArcGIS Pro
    CanopyOutput=arcpy.GetParameterAsText(3) #sets parameter for canopy product output in ArcGIS Pro
    LowHeightValueInput=arcpy.GetParameterAsText(4) #sets parameter for height value input in ArcGIS Pro
    LowNDVIValueInput=arcpy.GetParameterAsText(5) #sets parameter for NDVI value input in ArcGIS Pro

#########################################################################
# Prints all parameters for debugging
#########################################################################

MyPrint("HhInput: "+HhInput)
MyPrint("BeInput: "+BeInput)
MyPrint("NAIP: "+NAIP)
MyPrint("NonGroundOutput: "+NonGroundOutput)
MyPrint("red: "+red)
MyPrint("nir: "+nir)
MyPrint("ndvi: "+ndvi)
MyPrint("CanopyOutput: "+CanopyOutput)

#########################################################################
## Run the script repeatedly without deleting the intermediate files
#########################################################################

arcpy.env.overwriteOutput=True

#########################################################################
## Main code (All processing scripts)
#########################################################################

MyPrint("#-----Begining processing-----#") #prints message to ArcGIS Pro dialog that processing has begun

MyPrint("""###############################################
Creating non-ground raster
###############################################""")

try:
    arcpy.gp.Minus_sa(HhInput,BeInput,NonGroundOutput) #subtract bare earth raster from highest hit raster

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed to create non-ground raster-----#") #prints message to ArcGIS Pro dialog

MyPrint("""###############################################
Reclassifying non-ground heights
###############################################""")

LowHeightValue=LowHeightValueInput #creates an input variable for parameter (4) - default: 5

try:
    arcpy.gp.Reclassify_sa(NonGroundOutput,"Value","0 "+LowHeightValue+" NODATA;"+LowHeightValue+" 500 1",HeightReclassOutput,"NODATA") #reclassify non-ground heights

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed to reclassify slope-----#") #prints message to ArcGIS Pro dialog

MyPrint("""###############################################
Extracting visual red and NIR bands from image
###############################################""")

try:
    red=arcpy.CopyRaster_management(NAIP+"\Layer_1",red,"#","#","0","NONE","NONE","#","NONE","NONE") #extract visual red band from image
    nir=arcpy.CopyRaster_management(NAIP+"\Layer_4",nir,"#","#","0","NONE","NONE","#","NONE","NONE") #extract NIR band from image

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed image band Extraction-----#") #prints message to ArcGIS Pro dialog

MyPrint("""###############################################
Calculating NDVI
###############################################""")

try:
    Num=arcpy.sa.Float(Raster(nir)-Raster(red)) #subtract NIR band from red band
    Denom=arcpy.sa.Float(Raster(nir)+Raster(red)) #add NIR band from red band
    Calc=arcpy.sa.Divide(Num, Denom)*100+100 #divide prerequisite results and calculate range
    Calc.save(ndvi) #save NDVI result

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed to calculate NDVI-----#") #prints message to ArcGIS Pro dialog

MyPrint("""###############################################
Reclassifying NDVI
###############################################""")

LowNDVIValue=LowNDVIValueInput #creates an input variable for parameter (5) - default: 120

try:
    #reclassify NDVI
    arcpy.gp.Reclassify_sa(ndvi,"Value","0 "+LowNDVIValue+" NODATA;"+LowNDVIValue+" 200 1",ndviReclassOutput,"NODATA") #reclassify NDVI

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed to reclassify ndvi-----#") #prints message to ArcGIS Pro dialog

MyPrint("""###############################################
Intersecting LIDAR and NDVI datasets - Canopy Raster
###############################################""")

try:
    #intersecting rasters
    Intersect=arcpy.sa.Float(Raster(HeightReclassOutput)*Raster(ndviReclassOutput)) #intersect height reclass raster from ndvi reclass raster
    Intersect.save(CanopyOutput) #save intersect result (canopy raster)

    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Completed successfully-----#") #prints message to ArcGIS Pro dialog
except:
    MyPrint(arcpy.GetMessages()) #prints ArcGIS Pro dialog processing messages
    MyPrint("#-----Failed to intersect LIDAR and NDVI-----#") #prints message to ArcGIS Pro dialog
