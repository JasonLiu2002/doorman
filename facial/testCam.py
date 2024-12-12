import cv2

if __name__ == '__main__':
    cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    
    if result:
        cv2.imshow("test", image)
        cv2.imwrite("test.png", image)
        cv2.waitKey(0)
        cv2.destroyWindow("test")
    
    else:
        print("No image detected. Please! try again")