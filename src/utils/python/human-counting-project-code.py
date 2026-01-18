import cv2
import imutils
import numpy as np
import argparse

# Constants
MAX_FRAME_WIDTH = 800
DETECT_STRIDE = (4, 4)
DETECT_PADDING = (8, 8)
DETECT_SCALE = 1.03
OUTPUT_FRAME_SIZE = (600, 600)
VIDEO_FPS = 10

# Initialize HOG descriptor globally for better performance
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect(frame):
    bounding_box_cordinates, weights = HOGCV.detectMultiScale(
        frame, winStride=DETECT_STRIDE, padding=DETECT_PADDING, scale=DETECT_SCALE
    )
    
    person = 1
    for x, y, w, h in bounding_box_cordinates:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f'person {person}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        person += 1
    
    cv2.putText(frame, 'Status : Detecting', (40, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f'Total Persons : {person - 1}', (40, 70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    cv2.imshow('output', frame)

    return frame

def process_frame(frame):
    """Resize frame to max width while maintaining aspect ratio."""
    return imutils.resize(frame, width=min(MAX_FRAME_WIDTH, frame.shape[1]))


def detectByPathVideo(path, writer):
    video = cv2.VideoCapture(path)
    check, frame = video.read()
    if not check:
        print('Video Not Found. Please Enter a Valid Path (Full path of Video Should be Provided).')
        return

    print('Detecting people...')
    while video.isOpened():
        check, frame = video.read()

        if check:
            frame = process_frame(frame)
            frame = detect(frame)
            
            if writer is not None:
                writer.write(frame)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        else:
            break
    video.release()
    cv2.destroyAllWindows()

def detectByCamera(writer):   
    video = cv2.VideoCapture(0)
    print('Detecting people...')

    try:
        while True:
            check, frame = video.read()
            if not check:
                break

            frame = process_frame(frame)
            frame = detect(frame)
            if writer is not None:
                writer.write(frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    finally:
        video.release()
        cv2.destroyAllWindows()

def detectByPathImage(path, output_path):
    image = cv2.imread(path)
    if image is None:
        print(f'Image Not Found: {path}')
        return

    image = process_frame(image)
    result_image = detect(image)

    if output_path is not None:
        cv2.imwrite(output_path, result_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
def humanDetector(args):
    image_path = args["image"]
    video_path = args['video']
    camera = args["camera"].lower() == 'true'

    writer = None
    if args['output'] is not None and image_path is None:
        writer = cv2.VideoWriter(args['output'], cv2.VideoWriter_fourcc(*'MJPG'), VIDEO_FPS, OUTPUT_FRAME_SIZE)

    if camera:
        print('[INFO] Opening Web Cam.')
        detectByCamera(writer)
    elif video_path is not None:
        print('[INFO] Opening Video from path.')
        detectByPathVideo(video_path, writer)
    elif image_path is not None:
        print('[INFO] Opening Image from path.')
        detectByPathImage(image_path, args['output'])
    else:
        print('[ERROR] Please provide either an image, video, or enable camera.')

    if writer is not None:
        writer.release()

def argsParser():
    arg_parse = argparse.ArgumentParser(description='Human Detection and Counting using HOG Descriptor')
    arg_parse.add_argument("-v", "--video", default=None, help="Path to video file")
    arg_parse.add_argument("-i", "--image", default=None, help="Path to image file")
    arg_parse.add_argument("-c", "--camera", default=False, help="Set to 'true' to use webcam")
    arg_parse.add_argument("-o", "--output", type=str, default=None, help="Path to save output video/image")
    args = vars(arg_parse.parse_args())

    return args


if __name__ == "__main__":
    args = argsParser()
    humanDetector(args)

