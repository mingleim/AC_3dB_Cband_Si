# -*- coding: utf-8 -*-
"""
   Updated adiabatic coupler

"""

from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.components.bezier import bezier
from gdsfactory.typings import CrossSectionSpec

def coupler_adiabatic_update(
    length1: float = 20.0,
    length2: float = 50.0,
    length3: float = 20.0,
    wg_sep: float = 1.0,
    input_wg_sep: float = 3.0,
    output_wg_sep: float = 3.0,
    dw: float = 0.1,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """Returns 50/50 adiabatic coupler.

    Design based on asymmetric adiabatic 3dB coupler designs, such as those.
    - https://doi.org/10.1364/CLEO.2010.CThAA2,
    - https://doi.org/10.1364/CLEO_SI.2017.SF1I.5
    - https://doi.org/10.1364/CLEO_SI.2018.STh4B.4

    input Bezier curves, with poles set to half of the x-length of the S-bend.
    1. is the first half of input S-bend where input widths taper by +dw and -dw
    2. is the second half of the S-bend straight with constant, unbalanced widths
    3. is the region where the two asymmetric straights gradually come together
    4. straights taper back to the original width at a fixed distance from one another
    5. is the output S-bend straight.

    Args:
        length1: region that gradually brings the two asymmetric straights together.
            In this region the straight widths gradually change to be different by `dw`.
        length2: coupling region, where asymmetric straights gradually
            become the same width.
        length3: output region where the two straights separate.
        wg_sep: Distance between center-to-center in the coupling region (Region 2).
        input_wg_sep: Separation of the two straights at the input, center-to-center.
        output_wg_sep: Separation of the two straights at the output, center-to-center.
        dw: Change in straight width.
            In Region 1, top arm tapers to width+dw/2.0, bottom taper to width-dw/2.0.
        cross_section: cross_section spec.

    """
    # Control points for input and output S-bends
    control_points_input_top = (
        (0, 0),
        (length1 / 2.0, 0),
        (length1 / 2.0, -input_wg_sep / 2.0 + wg_sep / 2.0),
        (length1, -input_wg_sep / 2.0 + wg_sep / 2.0),
    )

    control_points_input_bottom = (
        (0, -input_wg_sep),
        (length1 / 2.0, -input_wg_sep),
        (length1 / 2.0, -input_wg_sep / 2.0 - wg_sep / 2.0),
        (length1, -input_wg_sep / 2.0 - wg_sep / 2.0),
    )

    control_points_output_top = (
        (length1 + length2, -input_wg_sep / 2.0 + wg_sep / 2.0),
        (
            length1 + length2 + length3 / 2.0,
            -input_wg_sep / 2.0 + wg_sep / 2.0,
        ),
        (
            length1 + length2 + length3 / 2.0,
            -input_wg_sep / 2.0 + output_wg_sep / 2.0,
        ),
        (
            length1 + length2 + length3,
            -input_wg_sep / 2.0 + output_wg_sep / 2.0,
        ),
    )

    c = Component()

    x = gf.get_cross_section(cross_section)
    width = float(x.width)
    width_top = width + dw
    width_bot = width - dw
    x_top = x.copy(width=width_top)
    x_bot = x.copy(width=width_bot)
    
    """
     Update: coupler - add gap, change length = 1.0
             taper_top & taper_bot - add length = length2
    """
    coupler = c << gf.components.coupler_straight(gap=wg_sep, length=1.0, cross_section=x) 

    taper_top = c << gf.components.taper(length=length2,
        width1=width, width2=width_top, cross_section=cross_section
    ) 
    taper_bot = c << gf.components.taper(length=length2,
        width1=width, width2=width_bot, cross_section=cross_section
    )  

    taper_bot.connect("o1", coupler.ports["o1"])
    taper_top.connect("o1", coupler.ports["o2"])

    sbend_left_top = c << bezier(
        control_points=control_points_input_top, cross_section=x_top
    )
    sbend_left_bot = c << bezier(
        control_points=control_points_input_bottom, cross_section=x_bot
    )

    sbend_left_top.connect("o2", taper_top.ports["o2"])
    sbend_left_bot.connect("o2", taper_bot.ports["o2"])

    sbend_right = bezier(control_points=control_points_output_top, cross_section=x)
    sbend_right_top = c << sbend_right
    sbend_right_bot = c << sbend_right

    sbend_right_top.connect("o1", coupler.ports["o3"])
    sbend_right_bot.connect("o1", coupler.ports["o4"], mirror=True)
    
    """
     Update: Add two tapers (taper_in_top and taper_in_bot) to tranform 
     the input waveguide width from width (500nm) to width_top and width_bot
     
    """
    taper_in_top = c << gf.components.taper(length=15,
        width1=width, width2=width_top, cross_section=cross_section
    ) 
    taper_in_bot = c << gf.components.taper(length=15,
        width1=width, width2=width_bot, cross_section=cross_section
    ) 
    taper_in_top.connect("o2", sbend_left_top.ports["o1"])
    taper_in_bot.connect("o2", sbend_left_bot.ports["o1"])

    c.add_port("o1", port=taper_in_top.ports["o1"])
    c.add_port("o2", port=taper_in_bot.ports["o1"])
    c.add_port("o3", port=sbend_right_top.ports["o2"])
    c.add_port("o4", port=sbend_right_bot.ports["o2"])
    return c
