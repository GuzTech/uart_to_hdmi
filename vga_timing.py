from nmigen import *
from nmigen.build import Platform


class vga_timing(Elaboratable):
    def __init__(self):
        # Configuration
        # Hardcoded for 800x600 @ 60Hz
        self.H_VISIBLE_AREA = 800
        self.H_FRONT_PORCH = 40
        self.H_SYNC_PULSE = 128
        self.H_BACK_PORCH = 88
        self.H_TOTAL = self.H_VISIBLE_AREA + self.H_FRONT_PORCH + \
            self.H_SYNC_PULSE + self.H_BACK_PORCH
        self.H_SYNC_START = self.H_VISIBLE_AREA + self.H_FRONT_PORCH
        self.H_SYNC_END = self.H_TOTAL - self.H_BACK_PORCH

        self.V_VISIBLE_AREA = 600
        self.V_FRONT_PORCH = 1
        self.V_SYNC_PULSE = 4
        self.V_BACK_PORCH = 23
        self.V_TOTAL = self.V_VISIBLE_AREA + self.V_FRONT_PORCH + \
            self.V_SYNC_PULSE + self.V_BACK_PORCH
        self.V_SYNC_START = self.V_VISIBLE_AREA + self.V_FRONT_PORCH
        self.V_SYNC_END = self.V_TOTAL - self.V_BACK_PORCH

        # I/O
        self.hsync = Signal()
        self.vsync = Signal()
        self.draw = Signal()
        self.hcnt = Signal(range(self.H_TOTAL))
        self.vcnt = Signal(range(self.V_TOTAL))

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # Declare signals so that we don't have to type self.signal_name
        hcnt = self.hcnt
        vcnt = self.vcnt
        hsync = self.hsync
        vsync = self.vsync

        # Horizontal counter
        with m.If(hcnt == (self.H_TOTAL - 1)):
            m.d.pix += hcnt.eq(0)
        with m.Else():
            m.d.pix += hcnt.eq(hcnt + 1)

        # Vertical counter
        with m.If((hcnt == (self.H_TOTAL - 1)) & (vcnt == (self.V_TOTAL - 1))):
            m.d.pix += vcnt.eq(0)
        with m.Elif(hcnt == (self.H_TOTAL - 1)):
            m.d.pix += vcnt.eq(vcnt + 1)

        # Horizontal sync
        m.d.comb += hsync.eq((hcnt >= self.H_SYNC_START)
                             & (hcnt < self.H_SYNC_END))

        # Vertical sync
        m.d.comb += vsync.eq((vcnt >= self.V_SYNC_START)
                             & (vcnt < self.V_SYNC_END))

        # When can we actually draw?
        m.d.comb += self.draw.eq((hcnt < self.H_VISIBLE_AREA)
                                 & (vcnt < self.V_VISIBLE_AREA))

        return m
