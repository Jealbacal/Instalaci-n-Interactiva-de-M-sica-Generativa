import mediapipe as mp
import cv2
from pprint import pprint
import itertools
import copy
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import time

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

video = cv2.VideoCapture(0)
OSC_ADDRESS = "/mediapipe/hands"
client = udp_client.SimpleUDPClient("127.0.0.1", 7500)
client2 = udp_client.SimpleUDPClient("127.0.0.1", 8080)


def absolute_landmarks(width,height,landmarks):
    landmarks_abs=[]
    
    for landmark in landmarks:

        landmark_x = min (int (landmark.x * width), width -1)
        landmark_y = min (int(landmark.y * height), height -1)

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

    result=[(temp[i], temp[i + 1]) for i in range(0, len(temp), 2)]

    return result

def traducir(label):
    if label == 'palm':
        return 0
    elif label == 'fist':
        return 1
    elif label == 'l':
        return 2
    elif label == 'thumb up':
        return 3
    elif label == 'thumb down':
        return 4
    elif label == 'none':
        return 5


def send_hands(client: udp_client,
               detections: GestureRecognizerResult):
    if detections is None:
        client.send_message(OSC_ADDRESS, 85)
        return

    # create message and send
    #builder = OscMessageBuilder(address=OSC_ADDRESS)
    #builder.add_arg(len(detections))
    for detection in detections.gestures:
        traducido = traducir(detection[0].category_name)

        #builder.add_arg(traducido)
        client.send_message(OSC_ADDRESS, traducido)

    # msg = builder.build()
    # client.send(msg)
def numerics_gest(landmarks):

    if ((abs(landmarks[0][0] - landmarks[20][0]) < 0.2) and 
        ((abs(landmarks[0][0] - landmarks[16][0]) < 0.2)) and 
        ((abs(landmarks[0][0] - landmarks[12][0]) < 0.2)) and
        (abs(landmarks[7][0] - landmarks[4][0]) < 0.2)
       ) :
            return 1
    
    elif ((abs(landmarks[0][0] - landmarks[20][0]) < 0.2) and 
          ((abs(landmarks[0][0] - landmarks[16][0]) < 0.2)) and 
          ((abs(landmarks[0][0] - landmarks[12][0]) < 0.2))   
         ) :
            return 2
    
    elif ((abs(landmarks[0][0] - landmarks[20][0]) < 0.2) and 
          ((abs(landmarks[0][0] - landmarks[16][0]) < 0.2)) 
         ) :
            return 3
    
    elif ((abs(landmarks[17][0] - landmarks[4][0]) < 0.2) 
         ) :
            return 4
    
    else:
            return 5


# Create a image segmenter instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    # cv2.imshow('Show', output_image.numpy_view())
    # imright = output_image.numpy_view()
    #print(result.gestures)
    hand_landmarks = result.hand_landmarks
    try:
        
        for landmark in hand_landmarks:
           pprint( numerics_gest(normalize_landmarks(absolute_landmarks(output_image.width,output_image.height,landmark))))

            
        send_hands(client,result) 
        send_hands(client2,result)   
    except Exception as e:
        print(e)
    #pprint(result.hand_world_landmarks[0])
    #pprint(result.hand_landmarks[0])
    
    
    # cv2.imwrite('somefile.jpg', imright)


#model_path = '..\models\gesture_recognizer.task'

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='..\models\gesture_recognizer.task',delegate= 1),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result,
    num_hands=2)




timestamp = 0
# used to record the time when we processed last frame 
prev_frame_time = 0
  
# used to record the time at which we processed current frame 
new_frame_time = 0

with GestureRecognizer.create_from_options(options) as recognizer:
  # The recognizer is initialized. Use it here.
    while video.isOpened(): 
        # Capture frame-by-frame
        ret, frame = video.read()
        frame=cv2.resize(frame,(800,600))
        frame=cv2.flip(frame,1)

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
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 

        cv2.putText(frame,str(int(fps))+"FPS", (6,150), cv2.FONT_HERSHEY_SIMPLEX,1,(173, 255, 250),2,cv2.LINE_AA )
        cv2.putText(frame,str(timestamp)+"inf", (6,70), cv2.FONT_HERSHEY_SIMPLEX,1,(173, 255, 250),2,cv2.LINE_AA )

        cv2.imshow('MediaPipe Hands', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

video.release()
cv2.destroyAllWindows()
