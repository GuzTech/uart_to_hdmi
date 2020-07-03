from nmigen import *
from nmigen.build import Platform
from nmigen_boards.icebreaker import *

from pll import *
from uart_data import *
from pmod_hdmi import *


hdmi_pmod = [
    Resource("red", 0, Pins("8 2 7 1", dir="o", conn=(
        "pmod", 0)), Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("green", 0, Pins("10 4 9 3", dir="o", conn=(
        "pmod", 0)), Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("blue", 0, Pins("3 8 7 1", dir="o", conn=(
        "pmod", 1)), Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("hsync", 0, Pins("4", dir="o", conn=("pmod", 1)),
             Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("vsync", 0, Pins("10", dir="o", conn=("pmod", 1)),
             Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("de", 0, Pins("9", dir="o", conn=("pmod", 1)),
             Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("ck", 0, Pins("2", dir="o", conn=("pmod", 1)),
             Attrs(IO_STANDARD="SB_LVCMOS")),
]


class Top(Elaboratable):
    def __init__(self, num_pixels_x=128, num_pixels_y=120, scaling=1):
        self.num_pixels_x = num_pixels_x
        self.num_pixels_y = num_pixels_y
        self.num_pixels = num_pixels_x*num_pixels_y
        self.scaling = scaling

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # PLL

        clk_in = platform.request(platform.default_clk, dir='-')
        # , external_rst=platform.request("button"))
        pll = PLL(freq_in_mhz=12, freq_out_mhz=40, domain_name="pix")

        m.domains += pll.domain
        m.submodules += [pll]

        m.d.comb += pll.clk_pin.eq(clk_in)

        clk_counter = Signal()
        m.d.pix += clk_counter.eq(clk_counter - 1)

        sync = ClockDomain("sync")
        m.domains.sync = sync
        m.d.comb += [
            sync.rst.eq(ResetSignal("pix")),
            sync.clk.eq(clk_counter[0])
        ]

        # Peripherals
        m.submodules.uart = uart = UART_Data()
        m.submodules.hdmi = hdmi = PMOD_HDMI(
            self.num_pixels_x, self.num_pixels_y, self.scaling)  # scaling should be a power of 2

        # Framebuffer
        mem = Memory(width=8, depth=self.num_pixels)
        m.submodules.rd = rd = mem.read_port()
        m.submodules.wr = wr = mem.write_port()

        # Reading from the framebuffer
        m.d.pix += rd.addr.eq(hdmi.r_addr)
        m.d.pix += hdmi.color.eq(rd.data)

        # Writing to the framebuffer
        w_addr = Signal(range(self.num_pixels), reset=(self.num_pixels - 1))

        with m.If(uart.rx_strobe):
            with m.If(w_addr == (self.num_pixels - 1)):
                m.d.sync += w_addr.eq(0)
            with m.Else():
                m.d.sync += w_addr.eq(w_addr + 1)

        m.d.sync += wr.data.eq(uart.data)
        m.d.sync += wr.addr.eq(w_addr)
        m.d.comb += wr.en.eq(1)

        # HDMI

        hsync = platform.request("hsync")
        vsync = platform.request("vsync")
        red = platform.request("red")
        green = platform.request("green")
        blue = platform.request("blue")
        de = platform.request("de")
        ck = platform.request("ck")

        m.d.comb += [
            hsync.eq(hdmi.hsync),
            vsync.eq(hdmi.vsync),
            red.eq(hdmi.red),
            green.eq(hdmi.green),
            blue.eq(hdmi.blue),
            de.eq(hdmi.de)
        ]

        m.d.comb += ck.eq(ClockSignal("pix"))

        return m


if __name__ == "__main__":
    plat = ICEBreakerPlatform()
    plat.add_resources(hdmi_pmod)

    plat.build(Top(scaling=4), do_program=True)
