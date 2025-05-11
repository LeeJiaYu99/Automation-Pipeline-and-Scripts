import cv2
from ultralytics import YOLO
import datetime
import os
import json
import time

def detect_person(frame):
    """
    Function to return whether person is detected in the frame (using YOLOv8 model)
    """
    model = YOLO('yolov8x.pt')

    results = model.predict(frame, classes=[0])

    if results[0].__len__() > 0:
        return True
    else:
        return False
    
def check_frame(stream_url, camera):
    """
    Record relevant frames and stop recording when no more relevant.
    """
    # Define output path
    output_dir = f"/app/recording/{camera}/"
    os.makedirs(output_dir, exist_ok=True)

    # Open stream
    cap = cv2.VideoCapture(stream_url)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if not cap.isOpened():
        print("Cannot open video stream")
        return
    
    recording = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        capture = detect_person(frame)
        if capture:
            if not recording:
                time_now = datetime.datetime.now().strftime("%d%m%Y_%H%M")
                output_file = os.path.join(output_dir, f"{camera}_{time_now}.avi")
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))
                recording = True
            out.write(frame)
        elif recording:
            recording = False
            out.release()

    # Release resources
    cap.release()
    if recording:
        out.release()
    cv2.destroyAllWindows()

def main():
    camera_id = "1001"
    camera_path = "rtmp://monitoring.com/live/stream"
    check_frame(camera_path, camera_id)

if __name__ == "__main__":
    while True:
        main()
