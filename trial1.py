import cv2
import numpy as np
import hashlib
import random

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def int_to_bin(value):
    return format(value, '08b')

def embed_bits(carrier_pixel, bits):
    r, g, b = carrier_pixel
    r = (r & 0b11111100) | int(bits[0:2], 2)
    g = (g & 0b11111100) | int(bits[2:4], 2)
    b = (b & 0b11111100) | int(bits[4:6], 2)
    return (r, g, b)

def scatter_image(image, video_frames, seed):
    random.seed(seed)
    img_height, img_width, _ = image.shape
    frame_count = len(video_frames)
    
    scattered_positions = []
    used_positions = set()
    
    for i in range(img_height):
        for j in range(img_width):
            r, g, b = image[i, j]
            r_bits = int_to_bin(r)
            g_bits = int_to_bin(g)
            b_bits = int_to_bin(b)

            for k in range(4):
                while True:
                    frame_idx = random.randint(0, frame_count - 1)
                    x = random.randint(0, video_frames[frame_idx].shape[1] - 1)
                    y = random.randint(0, video_frames[frame_idx].shape[0] - 1)
                    if (frame_idx, x, y) not in used_positions:
                        used_positions.add((frame_idx, x, y))
                        scattered_positions.append((frame_idx, x, y, r_bits[k*2:(k+1)*2] + g_bits[k*2:(k+1)*2] + b_bits[k*2:(k+1)*2]))
                        break
    
    return scattered_positions

def embed_image_in_video(image_path, video_path, output_path, passkey):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Couldn't read video stream from file '{video_path}'")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Original video FPS: {fps}")
    
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    print(f"Total frames read from input video: {len(frames)}")
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Couldn't read image from file '{image_path}'")
        return
    
    img_height, img_width, _ = image.shape
    
    seed = hash_passkey(passkey)
    scattered_positions = scatter_image(image, frames, seed)
    
    for frame_idx, x, y, bits in scattered_positions:
        frames[frame_idx][y, x] = embed_bits(frames[frame_idx][y, x], bits)
    
    height, width, layers = frames[0].shape
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:    
        out.write(frame)
    out.release()
    
    print(f"Total frames written to output video: {len(frames)}")
    
    # Verify FPS of the final video
    cap_out = cv2.VideoCapture(output_path)
    if cap_out.isOpened():
        final_fps = cap_out.get(cv2.CAP_PROP_FPS)
        print(f"Final video FPS: {final_fps}")
    cap_out.release()

def extract_bits(carrier_pixel):
    r, g, b = carrier_pixel
    r_bits = format(r, '08b')
    g_bits = format(g, '08b')
    b_bits = format(b, '08b')
    return r_bits[-2:], g_bits[-2:], b_bits[-2:]

def bin_to_int(binary_str):
    return int(binary_str, 2)

def extract_image_from_video(video_path, passkey, img_height, img_width):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Couldn't read video stream from file '{video_path}'")
        return None
    
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    image = np.zeros((img_height, img_width, 3), dtype=np.uint8)

    seed = hash_passkey(passkey)
    scattered_positions = scatter_image(image, frames, seed)
    
    extracted_image = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    
    r_bits = ""
    g_bits = ""
    b_bits = ""
    flag = 0

    for frame_idx, x, y, bits in scattered_positions:
        flag+=1
        
        r, g, b = extract_bits(frames[frame_idx][y, x])
        r_bits += r
        g_bits += g
        b_bits += b
        
        if flag == 4:
            r = bin_to_int(r_bits)
            g = bin_to_int(g_bits)
            b = bin_to_int(b_bits)

            if y < img_height and x < img_width:
                extracted_image[y, x] = (r, g, b)
            r_bits = ""
            g_bits = ""
            b_bits = ""
            flag = 0
    
    return extracted_image

# Embed the image into the video
embed_image_in_video('CSDF/Exp1/passenger.jpg', 'CSDF/Exp1/video.mp4', 'CSDF/Exp1/output_video.mkv', 'faizkhan')

# Extract the image from the video
img_height, img_width = 418, 612  # Hardcoded dimensions of the original image
extracted_image = extract_image_from_video('CSDF/Exp1/output_video.mkv', 'faizkhan', img_height, img_width)

if extracted_image is not None:
    cv2.imwrite('CSDF/Exp1/extracted_passenger.jpg', extracted_image)