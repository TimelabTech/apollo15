# apollo15
Apollo 15 X-Ray All Sky Map
Author: Ricardo Vallés Blanco (ESAC)

 Steps for generating All Sky Map with Aladin
 ========================================================

 1 - Edit Python/constants.py and setup your All Sky generation run.

 2 - Run "python Python/allSkyFitsGen.py"

 3 - Go to Aladin

    3.0 - Tool->Generate a HiPS based on...->An image collection...
    3.1 - Set the Source path (Absolute path)
          Also set the target path and data name (HiPS name)
    3.2 - Set Specifical HDU numbers = 0
          and select "Fadding efects on overlaying borders"
    3.3 - Click Next

    3.4 - Select short(8bits), and Keep Original BITPIX
    3.5 - Select the desired angular resolution
    3.6 - Click START

    3.6 - Go to Aladin->Image->Pixel Contrast&Map
            Choose a color range function and adjust the color range
    3.7 - HipsGen: Select "Cut params imported from current view"
            or "Manual cut" and set ColorRangeMin - ColorRangeMax
    3.8 - Select PNG
    3.9 - Select computing method: Average
   3.10 - Click on "Build"
   3.11 - Click Next

   3.12 - Set up a path
   3.13 - Click "Generate"


    NOTE: I recommend restart Aladin before each HiPS generation.


  4: Steps for generating an RGB All Sky Map with Aladin
  ========================================================

  After generating at least three HiPS you can merge them in a RGB HiPS
  In order to do it follow the next steps:

  4.0 - Load the HiPS in the Aladin Stack
  4.1 - Load the MOC file of each loaded HiPS
  4.2 - Select the MOC´s planes and go to Coverage->Logical Operations
  4.3 - Select union or intersection and click on Create
  4.4 - Remove previous MOCs planes but not the just created one
  4.5 - Go to Aladin->Image->Pixel Contrast&Map
          Choose a color range function and adjust the color range for each HiPS
  4.6 - Set the order and opacity of each HiPS
  4.7 - Tool->Generate a HiPS based on...->An image collection...
  4.8 - Goto Generate RGB step
  4.9 - Assign a color to each HiPS and set the output folder (existing empty folder)
 4.10 - Choose Median and PNG, then click START
