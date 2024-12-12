import socket
import numpy as np
import matplotlib.pyplot as plt
import os

WRITE_IMAGE_PATH = "../img"
def request_image():
    """
    :return: (H x W x 3) (RGB) np.ndarray representing the image
             captured on the doorbell, or None if no image was captured
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 9925))
        sock.sendall('E'.encode('utf-8'))

        sock.settimeout(1)

        message_chunks = []
        while True:
            try:
                data = sock.recv(1024)
            except socket.timeout:
                continue
            if not data:
                break
            message_chunks.append(data)

        encoded_im = b''.join(message_chunks)
        if encoded_im == b'No image was captured from the camera.':
            print(encoded_im.decode('utf-8'))
            return None
        image, height, width = encoded_im.split(b'!~!')
        height = int.from_bytes(height, 'little')
        width = int.from_bytes(width, 'little')

        return np.flip(np.frombuffer(image, dtype=np.uint8)
                       .reshape((height, width, 3)), axis=2)

def save_image(img):
    if img is not None:
        plt.imshow(img)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join('../', 'CapturedImages/')

        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        name = "capturedImage"
        plt.savefig(results_dir + name)
# For testing purposes
if __name__ == "__main__":
    image = request_image()
    if image is not None:
        plt.imshow(image)
        plt.show()
