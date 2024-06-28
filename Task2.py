# -*- coding: utf-8 -*-
"""
    Task: Genearte a simple integrated-photonic circuit to measure that beamsplitter in a lab
    
    PIC design: 2x2 imbalanced MZI
    
    Method: Splitting ratios of the 2x2 beamsplitter can be extrated by the meausred
    power extinction ratios between the two output ports; Insertion loss can be estimated by 
    backing out the GC spectra using the loopback structure.
    
    Essential lab test equipment:
        Optical probe station
        C-band Tunable laser
        Multi-channel (>=4) Optical powermeter
        Multi-channel (>=4) Fiber array unit (FAU)
    
"""
import gdsfactory as gf
from MZI_update import mzi2x2_2x2

c = mzi2x2_2x2(delta_length=100, length_AC = 140.0, gap_AC = 0.12, dw_AC = 0.12)
cc = gf.routing.add_fiber_array(
    component=c,
    optical_routing_type=2,
    grating_coupler=gf.components.grating_coupler_elliptical_te,
    with_loopback=True
)
cc.write_gds("demo.gds") 
cc.show() 