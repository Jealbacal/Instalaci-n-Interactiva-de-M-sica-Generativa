import itertools
import copy
import numpy as np
import cv2

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


def frame_negro(ventana_abierta:bool):

    if ventana_abierta:

        frame = np.zeros((600, 800, 3), dtype=np.uint8)

        # Definir el texto que quieres mostrar
        texto = "Para comenzar di 'Empieza'"

        # Definir la fuente, el tamaño del texto y el color
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)  # Blanco
        grosor = 2

        # Obtener el tamaño del texto para centrarlo
        (tamaño_texto, _) = cv2.getTextSize(texto, font, font_scale, grosor)
        posicion_texto = ((frame.shape[1] - tamaño_texto[0]) // 2, (frame.shape[0] + tamaño_texto[1]) // 2)

        # Poner el texto en el frame negro
        cv2.putText(frame, texto, posicion_texto, font, font_scale, color, grosor, lineType=cv2.LINE_AA)

        # Mostrar el frame
        cv2.imshow("Frame", frame)

        # Esperar a que el usuario presione una tecla para cerrar
        cv2.waitKey(1)

def frame_imagen():
    # Cargar la imagen
    imagen = cv2.imread("utils\Gestos.jpg")
    imagen = cv2.resize(imagen, (800, 600))
    # Comprobar que la imagen se ha cargado correctamente
    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    # Mantener el frame visible hasta que se cumpla la condición
        # Mostrar la imagen en una ventana llamada 'Frame'
    cv2.imshow("Frame", imagen)

    # Refresca la ventana
    cv2.waitKey(30000)

class ColaCircular:
    def __init__(self, size):
        self.size = size  
        self.queue = [None] * size
        self.front = 0  
        self.rear = -1  
        self.count = 0  
        self.total = 0 

    def insertar(self, valor):
        
        if self.count == self.size:
            valor_viejo = self.queue[self.front]
            self.total -= valor_viejo  
            self.front = (self.front + 1) % self.size  
        else:
            self.count += 1

        
        self.rear = (self.rear + 1) % self.size
        self.queue[self.rear] = valor
        self.total += valor  

    def calcular_media(self):
        if self.count == 0:
            return 0 
        return self.total / self.count