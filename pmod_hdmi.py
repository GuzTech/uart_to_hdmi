from nmigen import *
from nmigen.build import Platform
from math import ceil, log2

from vga_timing import *


class PMOD_HDMI(Elaboratable):
    def __init__(self, num_pixels_x, num_pixels_y, scaling=1):
        # I/O
        self.red = Signal(4)
        self.green = Signal(4)
        self.blue = Signal(4)
        self.hsync = Signal()
        self.vsync = Signal()
        self.de = Signal()
        self.r_addr = Signal(range(num_pixels_x * num_pixels_y))
        self.color = Signal(8)

        # Configuration
        self.num_pixels_x = num_pixels_x
        self.num_pixels_y = num_pixels_y
        self.scaling = ceil(log2(scaling))

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # Warning: vga_timing is fixed at 800x600 @ 60Hz
        m.submodules.vga_timing = timing = vga_timing()

        m.d.comb += [
            self.hsync.eq(timing.hsync),
            self.vsync.eq(timing.vsync),
            self.de.eq(timing.draw),
        ]

        # We know that if the horizontal and vertical counters are smaller that our virtual resolution of
        # (num_pixels_x, num_pixels_y), then we are allowed to draw, so we don't check that here.
        with m.If((timing.vcnt[self.scaling:] < self.num_pixels_y) & (timing.hcnt[self.scaling:] < self.num_pixels_x)):
            m.d.pix += self.r_addr.eq(
                (timing.vcnt[self.scaling:] * self.num_pixels_x) + timing.hcnt[self.scaling:])
        with m.Else():
            m.d.pix += self.r_addr.eq(0)

        with m.If(timing.draw):
            m.d.pix += [
                self.red[1:4].eq(self.color[0:3]),
                self.green[1:4].eq(self.color[3:6]),
                self.blue[2:4].eq(self.color[6:8])
            ]
        with m.Else():
            m.d.pix += [
                self.red.eq(0),
                self.green.eq(0),
                self.blue.eq(0)
            ]

        return m
