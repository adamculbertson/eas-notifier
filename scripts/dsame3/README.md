# dsame3
This is a heavily stripped down and modified version of [dsame3](https://github.com/jamieden/dsame3). It only contains the bare minimum necessary to run the in the container, as well as a helper Python script (`pipe.py`) that is not in the original.  

The original script has issues with buffering and has too much complexity, so I toned it down a lot. In addition, all the dependency checks that were in the original are now done via the Dockerfile.