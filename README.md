# exrLayerMerger
 python utility to merge layers exr that has been separated into separate single layers exrs during the denoise proccess

# install

- Make sure you have python installed on your computer
- Download the repo and place the EXR_MERGE folder at this location : C:\Denoiser\ (create the Denoiser folder if it does not exist)
- Download a blender portable version at : https://www.blender.org/download/Blender2.82/blender-2.82a-windows64.zip/
- Unzip the contents of the folder into the C:\Denoiser\EXR_MERGE\blender_executable\ folder. The blender.exe needs to be accessible from this folder, it should not be at C:\Denoiser\EXR_MERGE\blender_executable\blender-2.82a-windows64\blender.exe
- Now you just have to copy and paste the exrLayerMerge_v001.py to the folder containing the subfolders of your filtered and separated exrs and double click it to run