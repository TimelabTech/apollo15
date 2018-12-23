# apollo15
Apollo 15 X-Ray All Sky Map (Variability Analysis)
Author: Ricardo Vallés Blanco (Timelab Technologies)

 All Sky XRFS Be Variability Analysis
 ========================================================

Variability is the variation of counts in time for the same "pixel" (RA & Dec coordinates).
The pixel has a fixed size, pixel diameter in degrees. For this study, sizes (2, 5, 10, 20)
were applied.

After the analysis the following contents were generated:

lcBeWithCoords.csv -> CSV file with the data from Be.dat matched with the coordinates (coords are interpolated with the data from ). This are the fields in the file: Time, Mode, Ch0, Ch1, Ch2, Ch3, Ch4, Ch5, Ch6, Ch7, Total, RA, DEC

Sco X-1.csv -> CSV file with the same format as lcBeWithCoords.csv but only with the data related to
the observations done to Sco X-1.

Cyg X-1.csv -> CSV file with the same format as lcBeWithCoords.csv but only with the data related to
the observations done to Cyg X-1.

pixSize2, pixSize5, pixSize10 and pixSize20 folders -> contains the files generated on the analysis for each pix size.

Each folder contains the following files:

skyOverlapCounts.png -> Image that represents the number of hits of each pixel for all the sky. The value of the number of hits per each pixel are represented in a color following the color scale in the image. Note: The axis values should be multiplied by pixSize in order to have the real coordinates.

variabilityMap.png -> Image where the Y represents a pixel coordinates and the X has the hit number for that coordinate. So value X,Y represents the total energy computed for that moment at that coordinate.

linePlot.png -> Just a multi line plot here each line represents the variation in time of the total energy captured for a given coordinate (pixel).

variability.csv -> CSV file with the data of the Be.dat file grouped by coordinates(pixel) and ordered in time ascendent. The fields are: RA, Dec, Time, Ch0, Ch1, Ch2, Ch3, Ch4, Ch5, Ch6, Ch7, Total
