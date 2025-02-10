Python Vision Assistant for LabView:

The project mainly focuses on implementing a vision assistant similar to the one provided by LabView's paid module. This is primarily to avoid the high cost of that module and because, after years of use, I've identified several issues with color and pattern detection, not to mention its lack of flexibility.

Version 1.0.0 includes the following features:

From Main.py:

We can open a window or load the pipeline. When opening the window, we can:
Load an image and patterns, enable axes for better control of the image.
Apply black and white filters, rotations, adaptive filters, and zoom.
The configuration can then be saved to apply it as a pipeline.

version 1.0.1 includes the following features:

Error in black and white convertion ---> SOLVED
Apply dilate filter
Apply erode filter

version 1.0.2 includes the fallowin features:

re structure project. Add color plane extraction

version 1.0.3 to 1.0.5 include:

colors operations

Status: Development

Contact: juancruznoya@mi.unc.edu.ar
