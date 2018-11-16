* *TEC_A15_attitude.txt*: Contains the nine elements of the rotation
    matrix to transform coordinates FROM J2000 to Vehicle frame.
* *TEC_A15_state_point.txt*: Contains the interpolated position and
    velocity during TEC along with the pointing in RA/DEC of the X-Ray
    Spectrometer.
* *TEC_thetaphi_sme.txt*: Contains the theta/phi angles for the Sun,
    Moon and Earth during TEC.


(*) Important note: I need to check the influence of using combined data
from J2000 and B1972 coordinates as it seems to be happening, should not
be high but might be relevant for a case in which a source is in the
limit of the FOV, but they should be good enough to produce meaningful
results and routines. Once I have solved the B1972 issue I will
re-export the data in the same format so that you can just re-run your
plots or computations.

