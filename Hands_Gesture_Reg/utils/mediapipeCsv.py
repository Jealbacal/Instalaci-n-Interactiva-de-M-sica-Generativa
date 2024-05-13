import mediapipe as mp
import cv2
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from pprint import pprint
import csv
import os
import copy
import itertools

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green

img = cv2.imread('2jpg')


def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image


model_path = 'hand_landmarker.task'


BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
mp_drawing = mp.solutions.drawing_utils

# Create a hand landmarker instance with the image mode:
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2)


def singname_to_label(name):
    'funciones que le asigna un label al nombre del gesto (por ahora solo habra 18 gestos, estos basados en las imagenes encontradas por la database)'
    match name:
        case 'call':
            return 0
        case 'dislike':
            return 1
        case 'fist':
            return 2
        case 'four':
            return 3
        case 'like':
            return 4
        case 'mute':
            return 5
        case 'ok':
            return 6
        case 'one':
            return 7
        case 'palm':
            return 8
        case 'peace':
            return 9
        case 'peace_inverted':
            return 10
        case 'rock':
            return 11
        case 'stop':
            return 12
        case 'stop_inverted':
            return 13
        case 'three':
            return 14
        case 'three2':
            return 15
        case 'two_up':
            return 16
        case 'two_up_inverted':
            return 17
        case _:
            return None


def absolute_landmarks(image,landmarks):
    landmarks_abs=[]
    
    for landmark in landmarks:

        landmark_x = min (int (landmark.x * image.width), image.width -1)
        landmark_y = min (int(landmark.y * image.height), image.height -1)

        landmarks_abs.append([landmark_x,landmark_y])

    return landmarks_abs

def normalize_landmarks(landmark_abs):
    temp= copy.deepcopy(landmark_abs)

    base_x, base_y =0,0

    for index, landmark in enumerate(temp):
        if index == 0:
            base_x,base_y = landmark[0], landmark[1]
        
        temp[index][0] = temp[index][0] - base_x
        temp[index][1] = temp[index][1] - base_y

    temp = list(itertools.chain.from_iterable(temp))

    max_value = max(list(map(abs,temp)))

    def normalize(n):
        return n/max_value
    
    temp = list(map(normalize,temp))

    return temp


with HandLandmarker.create_from_options(options) as landmarker:
    landmark_list = []
    root = 'imagenes'
    for actual_dir, subdirs, files in os.walk(root):
        temp = actual_dir.split('\\')
        dir = (-1) if len(actual_dir.split('\\')
                          ) == 1 else actual_dir.split('\\')[1]
        sing_label = singname_to_label(dir)

        for file in files:
            if file.endswith(('.jpg', 'jpeg', 'png')):
                image_path = os.path.join(actual_dir, file)
                mp_image = mp.Image.create_from_file(image_path)
                hand_landmarker_result = landmarker.detect(mp_image)
                # pprint(hand_landmarker_result.hand_landmarks)
                if hand_landmarker_result.hand_landmarks:
                    landmark_list_abs = absolute_landmarks(mp_image,hand_landmarker_result.hand_landmarks[0])
                    landmark_list=normalize_landmarks(landmark_list_abs)

                    with open('landmarks.csv', 'a', newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([sing_label, *landmark_list])

    # landmark_list = []
    # mp_image = mp.Image.create_from_file(
    #     'imagenes/call/0d303909-120a-41e9-9005-e445e955982d.jpg')
    # hand_landmarker_result = landmarker.detect(mp_image)
    
    # pprint(normalize_landmarks(absolute_landmarks(mp_image,hand_landmarker_result.hand_landmarks[0])))

    # landmark_list = [coord for hand_landmark in hand_landmarker_result.hand_landmarks[0]
    #                  for coord in (hand_landmark.x, hand_landmark.y)]

    # pprint(landmark_list)

    # # annotated_image = draw_landmarks_on_image(
    # #     mp_image.numpy_view(), hand_landmarker_result)
    # # cv2.imshow('prueba', cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    # # cv2.waitKey(0)
    # # cv2.destroyAllWindows()
