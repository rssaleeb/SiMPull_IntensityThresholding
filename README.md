# SiMPull_IntensityThresholding

Intensity-based detection of protein aggregates in a mixed monomer/oligomer population pulled-down by SiMPull and imaged by TIRF microscopy.

<b>1. Extract monomer-only signal</b> </br>
Use STAPull methodology and analysis to robustly identify monomeric signal (10.5281/zenodo.8279273). Process output CSVs using this python code which will extract descriptive information (including intensity) of all non-coincident (i.e. monomeric) events. This can be used identify a suitable threshold value.

<b>2. Event detection </b></br>
An ImageJ macro that thresholds data with a user-defined fixed value and uses the ComDet plugin for Fiji (https://github.com/ekatrukha/ComDet) to batch detect and report single channel puncta.

Additionally refer to STAPull analysis code (10.5281/zenodo.8279273) for helpful scripts to pre-process and align multi-channel 
