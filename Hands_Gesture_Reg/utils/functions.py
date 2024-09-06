import itertools
import copy
import numpy as np

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
    
def calcular_distancia(p1x, p1y, p2x, p2y):
    return np.sqrt((p1x - p2x)**2 + (p1y - p2y)**2) #p1 x 

def numerics_gest(landmarks):
    
    # Gesto 1: Solo el índice levantado
    if (
        (calcular_distancia(landmarks[0][0], landmarks[0][1], landmarks[20][0], landmarks[20][1]) < 0.3)  # Meñique cerca de la palma
        and (calcular_distancia(landmarks[0][0],landmarks[0][1], landmarks[16][0] , landmarks[16][1]) < 0.3)  # Anular cerca de la palma
        and (calcular_distancia(landmarks[0][0],landmarks[0][1], landmarks[12][0], landmarks[12][1]) < 0.3)  # Medio cerca de la palma
        and (calcular_distancia(landmarks[11][0],landmarks[11][1], landmarks[4][0],landmarks[4][1]) < 0.3)  # Pulgar doblado
        and (calcular_distancia(landmarks[8][0],landmarks[8][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Índice extendido
    ):
        return 1

    # Gesto 2: Índice y medio levantados
    elif (
        (calcular_distancia(landmarks[0][0],landmarks[0][1], landmarks[20][0],landmarks[20][1]) < 0.3)
        and (calcular_distancia(landmarks[0][0], landmarks[0][1],landmarks[16][0] , landmarks[16][1]) < 0.3)  # Anular y meñique doblados
        and (calcular_distancia(landmarks[15][0],landmarks[15][1], landmarks[4][0],landmarks[4][1]) < 0.3)  # Pulgar doblado
        and (calcular_distancia(landmarks[8][0],landmarks[8][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Índice extendido
        and (calcular_distancia(landmarks[12][0], landmarks[12][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Medio extendido
    ):
        return 2

    # Gesto 3: Índice, medio y anular levantados
    elif (
        (calcular_distancia(landmarks[4][0],landmarks[4][1], landmarks[20][0],landmarks[20][1]) < 0.3)  # Pulgar y meñique doblados
        and (calcular_distancia(landmarks[8][0],landmarks[8][1], landmarks[0][0] ,landmarks[0][1]) >= 0.6)  # Índice extendido
        and (calcular_distancia(landmarks[12][0], landmarks[12][1], landmarks[0][0], landmarks[0][1]) >= 0.6)  # Medio extendido
        and (calcular_distancia(landmarks[16][0] , landmarks[16][1] , landmarks[0][0],landmarks[0][1]) >= 0.6)  # Anular extendido
    ):
        return 3

    # Gesto 4: Índice, medio, anular y meñique levantados
    elif (
        (calcular_distancia(landmarks[17][0],landmarks[17][1], landmarks[4][0],landmarks[4][1]) < 0.3)  # Pulgar doblado
        and (calcular_distancia(landmarks[8][0],landmarks[8][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Índice extendido
        and (calcular_distancia(landmarks[12][0], landmarks[12][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Medio extendido
        and (calcular_distancia(landmarks[16][0] , landmarks[16][1] , landmarks[0][0],landmarks[0][1]) >= 0.6)  # Anular extendido
        and (calcular_distancia(landmarks[20][0],landmarks[20][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Meñique extendido
    ):
        return 4

    # Gesto 5: Todos los dedos levantados
    elif (
        (calcular_distancia(landmarks[4][0],landmarks[4][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Pulgar extendido
        and (calcular_distancia(landmarks[8][0],landmarks[8][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Índice extendido
        and (calcular_distancia(landmarks[12][0], landmarks[12][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Medio extendido
        and (calcular_distancia(landmarks[16][0] , landmarks[16][1] , landmarks[0][0],landmarks[0][1]) >= 0.6)  # Anular extendido
        and (calcular_distancia(landmarks[20][0],landmarks[20][1], landmarks[0][0],landmarks[0][1]) >= 0.6)  # Meñique extendido
    ):
        return 5
    else:
        return 0    
        