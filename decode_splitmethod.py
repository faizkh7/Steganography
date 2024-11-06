from PIL import Image

def bin_to_int(binary_str):
    return int(binary_str, 2)


def extract_bits(carrier_pixel):
    r, g, b = carrier_pixel
    r_bits = format(r, '08b')
    g_bits = format(g, '08b')
    b_bits = format(b, '08b')
    return r_bits[-2:], g_bits[-2:], b_bits[-2:]

def decode_image(carrier, width, height):
    carrier_pixels = carrier.load()
    decoded_image = Image.new('RGB', (width, height))
    decoded_pixels = decoded_image.load()

    carrier_index = 0

    for y in range(height):
        for x in range(width):
            r_bits = ""
            g_bits = ""
            b_bits = ""


            # Extract the last 2 bits from each of the 4 carrier pixels
            for _ in range(4):
                r, g, b = extract_bits(carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width])
                r_bits += r
                g_bits += g
                b_bits += b
                carrier_index += 1

            # Convert the collected bits back to integer RGB values
            r = bin_to_int(r_bits)
            g = bin_to_int(g_bits)
            b = bin_to_int(b_bits)

            # Set the pixel in the decoded image
            decoded_pixels[x, y] = (r, g, b)

    decoded_image.save('Exp1/decoded_image.png')

# Example Usage
carrier_url = 'Exp1/encoded_image.png'
carrier = Image.open(carrier_url)

width, height = 612, 418  # Replace with actual retrieval method

decode_image(carrier, width, height)
