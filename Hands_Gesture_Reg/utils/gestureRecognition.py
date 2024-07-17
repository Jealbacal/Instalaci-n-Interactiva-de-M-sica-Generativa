import mediapipe as mp
import cv2
from pprint import pprint
from functions import *
import numpy as np
import statistics as st
from collections import deque

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import threading
import time




class Sender ():

    def __init__(self,ip,port):
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.OSC_ADDRESS = "/mediapipe/hands"
        buffer_size = 10
        self.gest_buffer = deque(maxlen=buffer_size)
        self.hand_buffer = deque(maxlen=buffer_size)
        self.coord_buffer = deque(maxlen=buffer_size)
        self.numerics_buffer = deque(maxlen=buffer_size)

        

    
    def send_hands(
    self, gest:int, handedness: int, coord: list, numerics: int
    ):
        
        msg = OscMessageBuilder(address=self.OSC_ADDRESS)
        msg.add_arg(gest)
        msg.add_arg(handedness)
        msg.add_arg(int(coord[0]))
        msg.add_arg(int(coord[1]))
        msg.add_arg(numerics)
        msg = msg.build()

        self.client.send(msg)


    def update_buffer(self,gest:int,hadedness:int,coord:list,numerics:int):

        self.gest_buffer.append(gest)
        self.hand_buffer.append(hadedness)
        self.numerics_buffer.append(numerics)
        self.coord_buffer.append(coord)

        if len(self.gest_buffer) == 10:
            avg_coord = np.mean(self.coord_buffer, axis=0).tolist()
            mode_gest = st.mode(self.gest_buffer)
            mode_hand = st.mode(self.hand_buffer)
            mode_numeric = st.mode(self.numerics_buffer)

            self.send_hands(mode_gest,mode_hand,avg_coord,mode_numeric)
            
            self.gest_buffer.clear()
            self.coord_buffer.clear()
            self.hand_buffer.clear()
            self.numerics_buffer.clear()



class Inference ():

    def __init__(self,sender):
        self.recognizer = None
        self.sender = sender
        self.setup_inference()
  

    def setup_inference(self):
        BaseOptions = mp.tasks.BaseOptions
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        

        options = GestureRecognizerOptions(
            base_options=BaseOptions(
                model_asset_path="utils/gesture_recognizer.task"  # Corregido el separador de ruta
            ),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result,  # Corregido: pasar referencia a la función
            num_hands=2,
        )

        self.video = cv2.VideoCapture(0)
        self.timestamp = 0
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
        self.inference_run(options,self.timestamp,self.prev_frame_time,self.new_frame_time)   
    
    def inference_run (self,options,timestamp,prev_frame_time,new_frame_time):

        with self.GestureRecognizer.create_from_options(options) as recognizer:
    # The recognizer is initialized. Use it here.
            while self.video.isOpened():
                # Capture frame-by-frame
                ret, frame = self.video.read()
                frame = cv2.resize(frame, (800, 600))
                # frame=cv2.flip(frame,1)

                if not ret:
                    print("Ignoring empty frame")
                    break

                timestamp += 1
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                # Send live image data to perform gesture recognition
                # The results are accessible via the `result_callback` provided in
                # the `GestureRecognizerOptions` object.
                # The gesture recognizer must be created with the live stream mode.
                new_frame_time = time.time()
                recognizer.recognize_async(mp_image, timestamp)
                fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time

                cv2.putText(
                    frame,
                    str(int(fps)) + "FPS",
                    (6, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (173, 255, 250),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    str(timestamp) + "inf",
                    (6, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (173, 255, 250),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow("MediaPipe Hands", frame)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

        self.video.release()
        cv2.destroyAllWindows()
        

    def print_result(
    self,result, output_image: mp.Image, timestamp_ms: int
    ):
        # cv2.imshow('Show', output_image.numpy_view())
        # imright = output_image.numpy_view()

        #print(result.gestures)
        hand_landmarks = result.hand_landmarks
        gestures = result.gestures
        handedness = result.handedness
        try:
            absolute = []
            numerics = 0
            gest,label = -1,-1
            for i in range (0,2):
                print (hand_landmarks[i][0])
                absolute = absolute_landmarks(
                    output_image.width, output_image.height, hand_landmarks[i]
                )
                numerics = numerics_gest(normalize_landmarks(absolute))
                print(numerics)
                print(gestures[i][0].category_name)
                gest = traducir(gestures[i][0].category_name)
                label =  1 if handedness[i][0].category_name == 'Right' else 0
                self.sender.update_buffer (gest,label, absolute[9], numerics)

        except Exception as e:
            print(e)


if __name__ == '__main__':
        
    sender = Sender ("127.0.0.1", 7500)
    inference = Inference(sender)

    

