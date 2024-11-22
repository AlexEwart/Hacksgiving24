import cv2


class webcamBackend:
    def __init__(self):
        # Initialize the camera (0 is for default webcam)
        self.last_frame = None
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open video stream or file")
        self.streaming = True  # Flag to control streaming

    def initialize_camera(self):
        # Initialize the camera only if it's not already streaming
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.streaming = self.cap.isOpened()
            if not self.streaming:
                print("Error: Could not open video stream or file")
        return self.streaming

    def get_video_feed(self):
        """Generator that yields frames for the video feed."""
        while self.streaming:
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not capture frame")
                break

            # Encode the frame as JPEG
            ret, jpeg = cv2.imencode(".jpg", frame)
            if not ret:
                print("Error: Failed to encode frame")
                break

            # Convert to bytes and yield in the correct format
            self.last_frame = jpeg.tobytes()

            # Create a multipart response to stream the video feed
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + self.last_frame + b"\r\n\r\n"
            )

        # Yield the last frame to freeze it on stop
        while self.last_frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + self.last_frame + b"\r\n\r\n"
            )

    def stop_webcam(self):
        self.streaming = False  # Set streaming flag to False to stop the feed

    def start_webcam(self):
        self.initialize_camera()
        self.streaming = True
        return self.streaming

    def get_single_image(self):
        # Capture frame-by-frame
        ret, frame = self.cap.read()
        ret, jpeg_image = cv2.imencode(".jpg", frame)
        return jpeg_image.tobytes()
