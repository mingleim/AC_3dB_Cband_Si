# -*- coding: utf-8 -*-
"""
    Task: Genearte a GDS of an Si-based 2x2 50:50 beamsplitter 
    
"""
from Coupler_adiabatic_update import coupler_adiabatic_update

c = coupler_adiabatic_update(length1=20, length2=150, length3=20, wg_sep=0.2)
c.write_gds("demo.gds")  
