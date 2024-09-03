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
    if label == "none":
        return 0
    elif label == "palm":
        return 1
    elif label == "fist":
        return 2
    elif label == "l":
        return 3
    elif label == "thumb up":
        return 4
    elif label == "thumb down":
        return 5
    

def numerics_gest(landmarks):

    if (
        (abs(landmarks[0][0] - landmarks[20][0]) < 0.2)
        and ((abs(landmarks[0][0] - landmarks[16][0]) < 0.2))
        and ((abs(landmarks[0][0] - landmarks[12][0]) < 0.2))
        and ((abs(landmarks[11][0] - landmarks[4][0]) < 0.2))
        and (abs(landmarks[8][0] - landmarks[0][0]) >= 0.3 )
    ):
        
        return 1

    elif (
        (abs(landmarks[0][0] - landmarks[20][0]) < 0.2)
        and ((abs(landmarks[1][0] - landmarks[16][0]) < 0.2))
        and ((abs(landmarks[15][0] - landmarks[4][0]) < 0.2)
        and (abs(landmarks[8][0] - landmarks[0][0]) >= 0.6 )
        and (abs(landmarks[12][0] - landmarks[0][0]) >= 0.6 ))
    ):
        return 2

    elif ((abs(landmarks[4][0] - landmarks[20][0]) < 0.2)
          and (abs(landmarks[8][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[12][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[16][0] - landmarks[0][0]) >= 0.6 )
        
    ):
        return 3

    elif ((abs(landmarks[17][0] - landmarks[4][0]) < 0.3)
          and (abs(landmarks[8][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[12][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[16][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[20][0] - landmarks[0][0]) >= 0.6 )):
        return 4

    elif ((abs(landmarks[4][0] - landmarks[0][0]) >= 0.6)
          and (abs(landmarks[8][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[12][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[16][0] - landmarks[0][0]) >= 0.6 )
          and (abs(landmarks[20][0] - landmarks[0][0]) >= 0.6 )):
        return 5   
    else:
        print("meñique:")
        print(abs(landmarks[0][0] - landmarks[20][0]) )
        print("anular:")
        print(abs(landmarks[0][0] - landmarks[16][0]))
        print("medio")
        print(abs(landmarks[0][0] - landmarks[12][0]) )
        print("pulgar")
        print(abs(landmarks[11][0] - landmarks[4][0]) )
        print("indice")
        print(abs(landmarks[8][0] - landmarks[0][0]) )
        return 0
        
        