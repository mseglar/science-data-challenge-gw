# CTAO Science Data Challenge: GW–GRB Tiling Simulation 🔭🌌

This repository contains code to run **tiling simulations for the CTAO Science Data Challenge**, aimed at producing **IACT observations** of a **mock gravitational-wave (GW) event** from a **binary neutron star (BNS) merger** with an associated **gamma-ray burst (GRB) emission** 🚀💥.

The pipeline simulates CTAO follow-up observations by generating observation tiles over the GW localization region, enabling realistic scheduling and coverage studies for IACT observations in the context of **multi-messenger astrophysics** 🌍✨.

Requirements for the code: 
- The code uses **`tilepy`** as a baseline framework and extends it to support the specific requirements of the CTAO Science Data Challenge 🧩🛠️.

- This code is part of the CTAO Science Data Challenge on GW follow-ups by CTAO. The full code to reproduce the data products obtained for the SDC can be found in https://github.com/astrojarred/gravitational-waves-CTAO-SDC.  There, the mock GCNs and the GRB emission models can be found. In addition, tilings are evaluated by the sensipy code to obtain the significance detections. 

- The simulated input is based on the subset of BNS-GRB simulations obtained in the context of the paper 'Chasing Gamma-Ray Signals from Binary Neutron Star Coalescences with the Cherenkov Telescope Array: Prospects and Observing Strategies', CTAO Consortium paper, 2026 (submission in Feb 2026). 

## Example of usage

The tiling observations are obtained launching the following command, for e.g. sdcID = 405: 
python ./RunTiling.py 405 -c alpha -i path_to_BNS_simulations_repo -o ./output/  -params ./config/sdc.ini -ct sdc -t fixed 
