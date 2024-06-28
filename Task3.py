# -*- coding: utf-8 -*-
"""
    Task: Genearte a simple design of experiment to target the 50:50 splitting ratio at 1550 nm
    
    Parameters to create the device variants:
        1. Gap - distance between the two tapers in the mode evolution region 
        2. Coupling_length - length of mode evolution region
        3. dW - width different between the input waveguides
    
    PIC blocks: 1. 2x2 imbalanced MZI
                2. cutback strcuture (12 devices)
                3. GC loopbacks for 4 channel FAU calibration

"""

import gdsfactory as gf
from Coupler_adiabatic_update import coupler_adiabatic_update
from MZI_update import mzi2x2_2x2

# Create gds space
c = gf.Component()

# Variant list
Gap = [0.12, 0.16, 0.18]
Coupling_length = [140, 160, 200]
dW = [0.1, 0.12, 0.14]
delta_L_MZI = 150
Shift_y_cutback = -40
Shift_y_gccali = -110-delta_L_MZI
Shift_x_gccali = -220
Shift_y_block = Shift_y_gccali-100

for iVariant in range(0, len(Gap)):
    # Single device
    a = coupler_adiabatic_update(length2=Coupling_length[0], wg_sep=Gap[iVariant], dw=dW[0])
    
    # MZI
    m = gf.routing.add_fiber_array(
        component = mzi2x2_2x2(delta_length=delta_L_MZI, length_AC=Coupling_length[0], \
                               gap_AC=Gap[iVariant], dw_AC=dW[0]),
        optical_routing_type=2,
        grating_coupler=gf.components.grating_coupler_elliptical_te,
        with_loopback=False
    )
    m = c << m
    
    # Cutbacks
    b = gf.components.cutback_2x2(component=a, cols=1, rows=3, port1='o1', \
                                  port2='o2', port3='o3', port4='o4', \
                                      mirror=False, cross_section='strip')
    bb = gf.routing.add_fiber_array(
        component = b,
        optical_routing_type=2,
        grating_coupler=gf.components.grating_coupler_elliptical_te,
        with_loopback=False
    )
    bb = c << bb
    
    # GC calibration (it can be placed once if footprint is limited)
    g = gf.components.grating_coupler_loss_fiber_array4(pitch=127, \
                                                        grating_coupler=gf.components.grating_coupler_elliptical_te)
    g = c << g
    
    # Move cells
    Shift_x_cutback = Coupling_length[0]+350
    m.dmovey(Shift_y_block*iVariant)
    bb.dmove([Shift_x_cutback,Shift_y_cutback+Shift_y_block*iVariant])
    g.dmove([Shift_x_gccali,Shift_y_gccali+Shift_y_block*iVariant])

c.write_gds("demo.gds") 
c.show()

