import cv2
import os

cam = cv2.VideoCapture(r"C:\Users\jesus\Videos\video_1.mkv")
ouput_dir = r"C:\Users\jesus\Pictures\none\\"

frameno = 0
while(True):
   ret,frame = cam.read()
   if ret:
      # if video is still left continue creating images
      name = str(frameno) + '.jpg'
      print ('new frame captured...' + name)

      cv2.imwrite(ouput_dir+name, frame)
      frameno += 1
   else:
      break

cam.release()
cv2.destroyAllWindows()