import mediapipe as mp
import cv2
from pprint import pprint
from functions import *
import numpy as np
import statistics as st
from collections import deque

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import time
from huggingsound import SpeechRecognitionModel
import speech_recognition as sr
import io
import tempfile
import os



class Sender ():

    def __init__(self,ip,port):
        self.client = udp_client.SimpleUDPClient(ip, port)  
        self.OSC_ADDRESS1 = "/mediapipe/handsR"
        self.OSC_ADDRESS2 = "/mediapipe/posR"
        self.OSC_ADDRESS3 = "/mediapipe/handsL"
        self.OSC_ADDRESS4 = "/mediapipe/posL"
        self.buffer_size = 3 
        self.gest_buffer_1 = deque(maxlen=self.buffer_size)
        #self.hand_buffer_1= deque(maxlen=buffer_size)
        self.numerics_buffer_1 = deque(maxlen=self.buffer_size)
        self.gest_buffer_2 = deque(maxlen=self.buffer_size)
        #self.hand_buffer_2= deque(maxlen=self.buffer_size)
        self.numerics_buffer_2 = deque(maxlen=self.buffer_size)

        

    
    def send_hands_right(
    self, gest:int, numerics: int
    ):
        
        msg = OscMessageBuilder(address=self.OSC_ADDRESS1)
        msg.add_arg(gest)
        #msg.add_arg(handedness)
        # msg.add_arg(int(coord[0]))
        # msg.add_arg(int(coord[1]))
        msg.add_arg(numerics)
        msg = msg.build()

   

        self.client.send(msg)

    def send_hands_left(
    self, gest:int,  numerics: int
    ):
        
        msg = OscMessageBuilder(address=self.OSC_ADDRESS3)
        msg.add_arg(gest)
        msg.add_arg(numerics)
        msg = msg.build()

        

        self.client.send(msg)

    def send_coords_right(self,coord:list):
        msg = OscMessageBuilder(address=self.OSC_ADDRESS2)
        msg.add_arg(int(coord[0]))
        msg.add_arg(int(coord[1]))
        msg = msg.build()

        self.client.send(msg)

    def send_coords_left(self,coord:list):
        msg = OscMessageBuilder(address=self.OSC_ADDRESS4)
        msg.add_arg(int(coord[0]))
        msg.add_arg(int(coord[1]))
        msg = msg.build()

        self.client.send(msg)


    def update_buffer_right(self,gest:int,numerics:int):

        self.gest_buffer_1.append(gest)
        #self.hand_buffer.append(hadedness)
        self.numerics_buffer_1.append(numerics)
        #self.coord_buffer.append(coord)

        if len(self.gest_buffer_1) == self.buffer_size:
            #avg_coord = np.mean(self.coord_buffer, axis=0).tolist()
            mode_gest = st.mode(self.gest_buffer_1)
            #mode_hand = st.mode(self.hand_buffer)
            mode_numeric = st.mode(self.numerics_buffer_1)

            self.send_hands_right(mode_gest,mode_numeric)
            
            self.gest_buffer_1.clear()
            #self.coord_buffer.clear()
            #self.hand_buffer_1.clear()
            self.numerics_buffer_1.clear()

    def update_buffer_left(self,gest:int,numerics:int):

        self.gest_buffer_2.append(gest)
        #self.hand_buffer.append(hadedness)
        self.numerics_buffer_2.append(numerics)
        #self.coord_buffer.append(coord)

        if len(self.gest_buffer_2) == self.buffer_size:
            #avg_coord = np.mean(self.coord_buffer, axis=0).tolist()
            mode_gest = st.mode(self.gest_buffer_2)
            #mode_hand = st.mode(self.hand_buffer)
            mode_numeric = st.mode(self.numerics_buffer_2)

            self.send_hands_left(mode_gest,mode_numeric)
            
            self.gest_buffer_2.clear()
            #self.coord_buffer.clear()
            #self.hand_buffer_1.clear()
            self.numerics_buffer_2.clear()



class Inference ():

    def __init__(self,sender):
        self.recognizer = None
        self.sender = sender
        self.exception_count = 0
        self.max_consecutive_exceptions = 7500
        self.setup_inference()
  

    def setup_inference(self):
        BaseOptions = mp.tasks.BaseOptions
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        

        options = GestureRecognizerOptions(
            base_options=BaseOptions(
                model_asset_path="utils\gesture_recognizer.task" 
            ),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result,  
            num_hands=2,
            min_hand_detection_confidence=0.2,
        )

        self.video = cv2.VideoCapture(0)
        self.timestamp = 0
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
        self.inference_run(options,self.timestamp,self.prev_frame_time,self.new_frame_time)   
    
    def inference_run (self,options,timestamp,prev_frame_time,new_frame_time):
        
        
        frame_imagen()
        with self.GestureRecognizer.create_from_options(options) as recognizer:
    # The recognizer is initialized. Use it here.
            cv2.destroyAllWindows()
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
                    clientEmission = udp_client.SimpleUDPClient("127.0.0.1", 7501)
                    clientEmission.send_message("/mediapipe/amplitude",-60.00)
                    break

                if self.exception_count >= self.max_consecutive_exceptions:
                    print("Max consecutive exceptions reached, breaking the loop.")
                    clientEmission = udp_client.SimpleUDPClient("127.0.0.1", 7501)  
                    clientEmission.send_message("/mediapipe/amplitude",-60.00)
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
                absolute = absolute_landmarks(
                    output_image.width, output_image.height, hand_landmarks[i]
                )
                numerics = numerics_gest(normalize_landmarks(absolute))
                gest = traducir(gestures[i][0].category_name)
                label =  1 if handedness[i][0].category_name == 'Right' else 0
                coordenadas = []

                coordX = (absolute[9][0])
                coordY = (abs(absolute[9][1] - output_image.height))
                coordenadas.append(coordX)
                coordenadas.append(coordY)
                

                if label == 1:
                    self.sender.update_buffer_right(gest,numerics)
                    self.sender.send_coords_right(coordenadas)

                else:
                    self.sender.update_buffer_left(gest,numerics)
                    self.sender.send_coords_left(coordenadas)

                self.exception_count = 0

        except Exception as e:
            #print(f"Exception occurred: {e}, consecutive count: {self.exception_count}")
            self.exception_count +=1


if __name__ == '__main__':
        
    model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")

    r = sr.Recognizer()
    
    with sr.Microphone(sample_rate=16000) as source:
        print("Puedes hablar")
        ventana_abierta = True


        while True:

            ventana_abierta = True
            frame_negro(ventana_abierta)
            audio = r.listen(source,phrase_time_limit=0.40)
            data = io.BytesIO(audio.get_wav_data())

            # Save the audio data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(data.getbuffer())
                temp_audio_file_path = temp_audio_file.name

            # Perform the transcription
                transcriptions = model.transcribe([temp_audio_file_path])

                transcription = transcriptions[0].get('transcription', '')

                print(transcriptions)
                # Print the transcriptions
                if transcription == 'empieza':
                    ventana_abierta = False 
                    cv2.destroyAllWindows()

                    sender = Sender ("127.0.0.1", 7500)
                    clientEmission = udp_client.SimpleUDPClient("127.0.0.1", 7501)  
                    clientEmission.send_message("/mediapipe/amplitude",-6.00)
                    inference = Inference(sender)
                elif transcription == 'termina':
                    break
        # Clean up the temporary file
            os.remove(temp_audio_file_path)    



