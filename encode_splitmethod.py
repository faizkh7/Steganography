from PIL import Image
import csv 

def int_to_bin(value):
    return format(value, '08b')

def embed_bits(carrier_pixel, bits):
    r, g, b = carrier_pixel
    r = (r & 0b11111100) | int(bits[0:2], 2)
    g = (g & 0b11111100) | int(bits[2:4], 2)
    b = (b & 0b11111100) | int(bits[4:6], 2)
    return (r, g, b)

def encode_image(carrier, passenger):
    carrier_pixels = carrier.load()
    passenger_pixels = passenger.load()
    
    width, height = passenger.size
    carrier_index = 0

    for y in range(height):
        for x in range(width):
            r, g, b = passenger_pixels[x, y]
            r_bits = int_to_bin(r)
            g_bits = int_to_bin(g)
            b_bits = int_to_bin(b)

            # Embed each 2 bits into 4 carrier pixels
            carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width] = embed_bits(carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width], r_bits[:2]+g_bits[:2]+b_bits[:2])
            
            carrier_index += 1
            
            carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width] = embed_bits(carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width], r_bits[2:4]+g_bits[2:4]+b_bits[2:4])
            
            carrier_index += 1
            
            carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width] = embed_bits(carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width], r_bits[4:6]+g_bits[4:6]+b_bits[4:6])
            
            carrier_index += 1
            
            carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width] = embed_bits(carrier_pixels[carrier_index % carrier.width, carrier_index // carrier.width], r_bits[6:]+g_bits[6:]+b_bits[6:])
            
            carrier_index += 1

    carrier.save('Exp1/encoded_image.png')



carrier_url = 'Exp1/carrier.jpg'
passenger_url = 'Exp1/passenger.jpg'
final = 'Exp1/final.jpg'
log_f = 'Exp1/log2.csv'
carrier = Image.open(carrier_url)
width1, height1 = carrier.size

passenger = Image.open(passenger_url)
width2, height2 = passenger.size

print(width1, height1)
print(width2, height2)

if width1 >= 4*width2 and height1 >= 4*height2:
    print("Carrier image is large enough to contain the passenger image.")
    encode_image(carrier, passenger)
else:
    print("Carrier image is too small to contain the passenger image.")


