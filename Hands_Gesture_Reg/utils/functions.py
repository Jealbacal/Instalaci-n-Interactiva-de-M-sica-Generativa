import itertools
import copy

def absolute_landmarks(width, height, landmarks):
    landmarks_abs = []

    for landmark in landmarks:

        landmark_x = min(int(landmark.x * width), width - 1)
        landmark_y = min(int(landmark.y * height), height - 1)

        landmarks_abs.append([landmark_x, landmark_y])

    return landmarks_abs


def normalize_landmarks(landmark_abs):
    temp = copy.deepcopy(landmark_abs)

    base_x, base_y = 0, 0

    for index, landmark in enumerate(temp):
        if index == 0:
            base_x, base_y = landmark[0], landmark[1]

        temp[index][0] = temp[index][0] - base_x
        temp[index][1] = temp[index][1] - base_y

    temp = list(itertools.chain.from_iterable(temp))

    max_value = max(list(map(abs, temp)))

    def normalize(n):
        return n / max_value

    temp = list(map(normalize, temp))

    result = [(temp[i], temp[i + 1]) for i in range(0, len(temp), 2)]

    return result


def traducir(label):
    if label == "palm":
        return 0
    elif label == "fist":
        return 1
    elif label == "l":
        return 2
    elif label == "thumb up":
        return 3
    elif label == "thumb down":
        return 4
    elif label == "none":
        return 5
    

def numerics_gest(landmarks):

    if (
        (abs(landmarks[0][0] - landmarks[20][0]) < 0.2)
        and ((abs(landmarks[0][0] - landmarks[16][0]) < 0.2))
        and ((abs(landmarks[0][0] - landmarks[12][0]) < 0.2))
        and (abs(landmarks[7][0] - landmarks[4][0]) < 0.2)
    ):
        return 1

    elif (
        (abs(landmarks[1][0] - landmarks[20][0]) < 0.2)
        and ((abs(landmarks[1][0] - landmarks[16][0]) < 0.2))
        and ((abs(landmarks[19][0] - landmarks[4][0]) < 0.2))
    ):
        return 2

    elif (abs(landmarks[0][0] - landmarks[20][0]) < 0.2) and (
        (abs(landmarks[0][0] - landmarks[16][0]) < 0.2)
    ):
        return 3

    elif abs(landmarks[13][0] - landmarks[4][0]) < 0.3:
        return 4

    else:
        return 5   