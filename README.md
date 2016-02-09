# Population Dot Map
Python port of a racial dot map done in Processing forked from
[https://github.com/unorthodox123/RacialDotMap] (https://github.com/unorthodox123/RacialDotMap)

All dotmap*.py files can be used to create png tiles. It starts from the shapefile and goes to the png creation except where noted.

*dotmap_serial.py* is the serial version for map tile creation.

*dotmap_mpi_level.py* is a MPI version 1 for map tile creation.

*dotmap_mpi_quadkey.py* is a MPI version 2 for map tile creation.

*dotmap_multiprocessing.py* is a multiprocessing version for map tile creation. 

*dotmap_mpi_reduce.py* performs a MPI mapreduce example. It uses a Vermont population file as an example.

*globalmaptiles.py* has been modified from fork to work with *dotmap.py* and to make functions more understandable and explicit.

*createtile.py* contains the actual map tile creation code.



