from nmigen import *
from nmigen.build import Platform

from uart import *


class UART_Data(Elaboratable):
    def __init__(self):
        self.data = Signal(8)
        self.rx_strobe = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        serial = platform.request("uart")
        m.submodules.uart = uart = UART(
            serial, clk_freq=20_000_000, baud_rate=1_000_000)

        m.d.comb += self.rx_strobe.eq(uart.rx_ready)
        m.d.comb += uart.rx_ack.eq(self.rx_strobe)

        with m.If(self.rx_strobe):
            m.d.sync += self.data.eq(uart.rx_data)

        return m
