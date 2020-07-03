# UART to HDMI in nMigen

This repository contains an [nMigen](https://github.com/nmigen/nmigen) implementation of project that fills a frame buffer over UART and outputs it over HDMI. It runs on the [iCEBreaker](https://1bitsquared.com/collections/fpga/products/icebreaker) FPGA board, and uses the [12bpp HDMI PMOD](https://1bitsquared.com/collections/fpga/products/pmod-digital-video-interface) board.

## Prerequisites
* [nMigen](https://github.com/nmigen/nmigen)
* [yosys](https://github.com/YosysHQ/yosys)
* [nextpnr-ice40](https://github.com/YosysHQ/nextpnr)

## How to use
I have only tested this on Linux, so I don't know how to do this exactly on other OSes.

1. Connect the iCEBreaker board to your computer.
2. Run `python top.py`. This will synthesize and program the iCEBreaker board.
3. Check which device name the iCEBreaker board was assigned: `ls /dev/ttyUSB*`. On my PC it's `/dev/ttyUSB1`.
3. Run `minicom -D /dev/ttyUSB1 -b 1000000` (where `/dev/ttyUSB1` is the number of your USB device).
4. Quit minicom: `CTRL+A`, `q`, and `ENTER`.
5. Run `cat images/marisa.raw > /dev/ttyUSB1`.

Running minicom is necessary to set the baud speed to 1000000. It is possible to set the baud rate using `stty -F /dev/ttyUSB1 1000000`, but on my PC I get distorted images. Your mileage may vary.

## Configuration information
The default configuration outputs at 800x600 @ 60Hz, and uses 8 bits per pixel (RGB332). Since the iCEBreaker board does not have enough built-in memory, it uses a virtual resolution of 128x120 pixels, and scales each pixel by 4. The HDMI PMOD board can use 12 bits per pixel, but then we would have to decrease the virtual resolution.

Several example images are provided (`isabelle.raw`, `marisa.raw`, `marisa2.raw`, `mr.raw`, and `meiling.raw`). You can create your own images using GIMP for example. With the default configuration, just take a 128x120 image with 8bpp RGB layout, save it in raw (e.g. `file.data`) format. Then you can use the `converter.py` Python script to convert it to RGB332 format:

`python converter.py <num_pixels_x> <num_pixels_y> <input_file> <output_file>`

So for example:

`python converter.py 128 120 file.data file.raw`