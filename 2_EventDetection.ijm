// Purpose: Count pulled down aggregates using intensity-based thresholding

// USER INPUTS ///////////////////////////////////////////////

filePrefix = "RS_STAPull-SR_StressMarq_"; //Provide experiment name used as file prefix by ONI Nanoimager
greenID = "AF488-trans.tif"; // Provide filename suffix for green channel images
redID = "AF647.tif"; // Provide filename suffix for red channel images
FOV_num = 25; // Number of fields of view per condition

stopSlice = 10; // Max projection of frames used for analysis, define here the number of frames to include

// Set threshold particle size (number of pixels) for species detection
green_particlesize = 4;
red_particlesize = 4;

// Set threshold intensity (SD above mean of ComDet-filtered image) for species detection
green_threshold = 1;
red_threshold = 1;

greenMon = 1149; // Input value 3 SD above mean intensity of monomeric events
redMon = 1935; // Input value 3 SD above mean intensity of monomeric events


// MAIN CODE ////////////////////////////////////////////////

// Set up working environment
setBatchMode("show");
run("Clear Results");

// Prompt user to provide select data folder (which contains subfolders per condition within which are all FOVs, channels are in separate files)
dir = getDir("Indicate overarching results folder to process");

// Create list of all subfolders
folderList = getFileList(dir);

//Create save directory
File.makeDirectory(dir + "Analysis/");

// For each subfolder
for (i = 0; i < lengthOf(folderList); i++) { 
	
	// Extract folder name
	currentFolder = substring(folderList[i], 0, indexOf(folderList[i], "/"));
	
	// Create matching save subdirectory
	File.makeDirectory(dir + "Analysis/" + folderList[i]);

	// For each FOV within the folder (excluding the results folder)
	for (j = 0; j < FOV_num; j++) {
	
		if (folderList[i] != "Analysis/") {	
			
			// Open each channel and Z-project		
			run("Bio-Formats Importer", "open=[" + dir + folderList[i] + filePrefix + currentFolder + "_posXY" + j + "_channels_t0_posZ0_" + greenID + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
			rename("green");
			run("Z Project...", "stop=" + stopSlice +" projection=[Max Intensity]");
			run("Subtract...", "value=" + greenMon);
			close("green");
			
			run("Bio-Formats Importer", "open=[" + dir + folderList[i] + filePrefix + currentFolder + "_posXY" + j + "_channels_t0_posZ0_" + redID + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
	   		rename("red");
	   		run("Z Project...", "stop=" + stopSlice +" projection=[Max Intensity]");
	   		run("Subtract...", "value=" + redMon);
	   		close("red");
			
			// Create channel duplicates and transform one with respect to the other as a control for chance coincidence
			selectWindow("MAX_green");
			run("Duplicate...", "title=MAX_green_transform duplicate");
			selectWindow("MAX_red");
	   		run("Duplicate...", "title=MAX_red_transform duplicate");
			run("Flip Horizontally");
			run("Flip Vertically");
	
			// Merge and rename channels
	   		run("Merge Channels...", "c1=MAX_red c2=MAX_green create");
	   		rename("test");
	   		run("Merge Channels...", "c1=MAX_red_transform c2=MAX_green_transform create");
	   		rename("transform");

	   		// For test case, detect particles and compute intensity, size and channel coincidence using the ComDet plug-in
	   		selectWindow("test");
	   		run("Detect Particles", "calculate max=2 plot rois=Ovals add=Nothing summary=Reset ch1i ch1a=" + red_particlesize + " ch1s=" + red_threshold + " ch2i ch2a=" + green_particlesize + " ch2s=" + green_threshold); 
			
			// Save results and close results windows
			selectWindow("test");
			saveAs("Tiff", "" + dir + "Analysis/" + folderList[i] + "posXY" + j + "_Test-Results.tif"); // This file contains the image file with detected particles indicated in overlay
			close("posXY" + j + "_Test-Results.tif");
			
			selectWindow("Results");
			saveAs("Results", dir + "Analysis/" + folderList[i] + "posXY" + j + "_descriptors.csv"); // This file contains intensity/size descriptors of all detections
			close("posXY" + j + "_descriptors.csv");
			
			selectWindow("Summary");
			saveAs("Results", dir + "Analysis/" + folderList[i] + "posXY" + j + "_Test-Results.csv"); // This file contains the total number of particles detected and the channel coincidence
			close("posXY" + j + "_Test-Results.csv");
			
			run("Clear Results");

			// For transform control, detect particles and compute channel coincidence using the ComDet plug-in
			selectWindow("transform");
	   		run("Detect Particles", "calculate max=2 plot rois=Ovals add=Nothing summary=Reset ch1i ch1a=" + red_particlesize + " ch1s=" + red_threshold + " ch2i ch2a=" + green_particlesize + " ch2s=" + green_threshold); 
			
			// Save results and close results windows
			selectWindow("transform");
			saveAs("Tiff", "" + dir + "Analysis/" + folderList[i] + "posXY" + j + "_Transform-Results.tif"); // This file contains the image file with detected particles indicated in overlay
			close("posXY" + j + "_Transform-Results.tif");
			
			selectWindow("Summary");
			saveAs("Results", dir + "Analysis/" + folderList[i] + "posXY" + j + "_Transform-Results.csv"); // This file contains the total number of particles detected and the channel coincidence
			close("posXY" + j + "_Transform-Results.csv");
			
			run("Clear Results");
			run("Close All");
			
			run("Collect Garbage");
		}

	}

}

