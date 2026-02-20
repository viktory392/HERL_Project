import cv2

class Camera:
    def __init__(self):
        pass

    def get_image(self) -> str:
        """Gets one still image from the camera."""
        # initialize camera
        cam_port = 0
        cam = cv2.VideoCapture(cam_port)

        # read input using the camera 
        result, image = cam.read()
        
        # If image will detected without any error, show result 
        image_file_name = "image.png"
        if result:
            # show result: frame name and image
            cv2.imshow("image", image) 
            cv2.imwrite(image_file_name, image) 
            cv2.waitKey(0) 
            cv2.destroyWindow("window")
        else:
            print("No image detected, try again")
        cam.release()
        return image_file_name

