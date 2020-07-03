import sys
import struct

if(len(sys.argv) != 5):
    print("Usage: python converter.py <num_pixels_x> <num_pixels_y> <input file> <output file>\n")
else:
    num_pixels_x = int(sys.argv[1])
    num_pixels_y = int(sys.argv[2])
    print(num_pixels_x)
    has_alpha_channel = False

    infile = open(sys.argv[3], "rb")
    data = infile.read()
    data_len = len(data)
    if((data_len != (num_pixels_x * num_pixels_y * 4)) or
            (data_len != (num_pixels_x * num_pixels_y * 3))):
        AssertionError(
            "File size does not match given resolution, or does not use 8bpp.")

    if(data_len == (num_pixels_x * num_pixels_y * 4)):
        has_alpha_channel = True

    outfile = open(sys.argv[4], "wb")

    infile.seek(0)

    for y in range(num_pixels_y):
        for x in range(num_pixels_x):
            r = (int.from_bytes(infile.read(1), 'little') >> 5) & 0x7
            g = (int.from_bytes(infile.read(1), 'little') >> 5) & 0x7
            b = (int.from_bytes(infile.read(1), 'little') >> 6) & 0x3

            if(has_alpha_channel):
                # Alpha channel, we don't use this
                _ = infile.read(1)

            pixel = (b << 6) | (g << 3) | r
            outfile.write(pixel.to_bytes(1, 'little'))

    infile.close()
    outfile.close()
