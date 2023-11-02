# rewrite_biosim4_py
Try to rewrite biosim4 in python with full functionality

## Original directory structure

From directory: D:\Programming\biosim4-main (Root Directory)

C++ Source File: D:\Programming\biosim4-main\src (Main C++ logic files)

Test files: D:\Programming\biosim4-main\tests (Test app)

Tools: D:\Programming\biosim4-main\tools (Plotting tools)

Images: D:\Programming\biosim4-main\images (Generated images along with the simulation)

Logs: D:\Programming\biosim4-main\logs (Generated logs along with the simulation)

## History

23.10.28

Created the project and github repo.

Rewrite plotting tools.

23.10.29

Minor fixes in “tests” directory.

Completed RNG.py for (random.cpp/.h)

Completed basicType.py for (basicType.cpp/.h)
Start working on params.py (params.cpp/.h)

23.11.01

Finished first iteration of params.cpp/.h, we now have params.py
Start working on sensors-actions.h

Finished first iteration of sensors-actions.h, we now have sensors-actions.py
created grid.py, indiv.py, simulator.py
Start working on grid.cpp/.h

23.11.02
minor fixes
fix issue of not generating by max min in RNG.py, fix of same path added to sys.path in import loop 
