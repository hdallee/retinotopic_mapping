# retinotopic_mapping package  

by Jun Zhuang  
&copy; 2016 Allen Institute  
email: junz&lt;AT&gt;alleninstitute&lt;DOT&gt;org  

For a more thorough introduction and explanation of the module please 
see our [documentation](http://retinotopic-mapping.readthedocs.io/).

The retinotopic mapping package is a self-contained module
for performing automated segmentation of the mouse
visual cortex. The experimental setup and analysis routine was
modified from Garrett et al. 2014 (1), and closely follows
the protocols and procedures documented in Juavinett et al. 2016
(2).

The code base contains several stimulus routines which are
highly customizable and designed to give the user significant
flexibility and control in creative experimental design. There
are two distinct but connected aspects to the package:

1. an online experimental component comprised of the
`MonitorSetup`, `StimulusRoutines`, and
`DisplayStimulus` modules

2. an offline automated analysis component provided
by the `RetinotopicMapping` module

The analysis takes visual altitude and azimuth maps of mouse cortex as inputs, calculates the visual 
sign of each pixel and auto-segments the cortical surface into primary visual cortex and multiple higher
visual cortices. Ideally, the visual altitude and azimuth maps can be generated by fourier analysis of
population cortical responses to periodic sweeping checker board visual stimuli (3, 4). 

The package also provides some useful plotting functions to visualize the results.

Please check the jupyter notebook in the '\examples' folder for a documented that takes an experimental
data set generated from the `StimulusRoutine.py` module and then performs an automated visual segmentation
of the mouse cortex using the `Retinotopic.py` module

https://github.com/zhuangjun1981/retinotopic_mapping/blob/master/retinotopic_mapping/examples/retinotopic_mapping_example.ipynb

### Contributors:
* Jun Zhuang @zhuang1981
* John Yearseley @yearsj
* Derric Williams @derricw

#### Language:

1. python 2.7


#### Install:
```
cd <package_path>
python setup.py install
```


#### Dependencies:

1. numpy, version 1.10.4 or later
2. scipy, version 0.17.0 or later
3. OpenCV-Python, version 2.4.8 or later
4. scikit-image, version 0.12.3 or later
5. matplotlib, version 1.5.1 or later
6. tifffile, version 0.7.0 or later
7. PsychoPy, version 1.7 or later
8. PyDAQmx, version 1.2 or later 
   * requires National Instruments DAQmx driver, version 15.0 or later

#### References:

1. Garrett ME, Nauhaus I, Marshel JH, Callaway EM (2014) Topography and areal organization of mouse visual cortex. J Neurosci 34:12587-12600.

2. Juavinett AL, Nauhaus I, Garrett ME, Zhuang J, Callaway EM (2017). Automated identification of mouse visual areas with intrinsic signal imaging. Nature Protocols. 12: 32-43.

3. Kalatsky VA, Stryker MP (2003) New paradigm for optical imaging: temporally encoded maps of intrinsic signal. Neuron 38:529-545.

4. Marshel JH, Kaye AP, Nauhaus I, Callaway EM (2012) Anterior-posterior direction opponency in the superficial mouse lateral geniculate nucleus. Neuron 76:713-720.

5. Sereno MI, Dale AM, Reppas JB, Kwong KK, Belliveau JW, Brady TJ, Rosen BR, Tootell RB (1995) Borders of multiple visual areas in humans revealed by functional magnetic resonance imaging. Science 268:889-893.

6. Sereno MI, McDonald CT, Allman JM (1994) Analysis of retinotopic maps in extrastriate cortex. Cereb Cortex 4:601-620.


#### Issues:

1. Most image analysis parameters are defined as number of pixels, not microns.
2. Works in windows, but not fully tested on Mac and Linux.