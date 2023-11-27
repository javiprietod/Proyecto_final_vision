import cv2
from picamera2 import Picamera2
from pyglet.window import key
from time import perf_counter

def stream_video():
    picam = Picamera2()
    picam.preview_configuration.main.size=(320, 180)
    picam.preview_configuration.main.format="RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()
    #keys = key.KeyStateHandler()
    idx = 0
    t1 = perf_counter()
    while True:
        frame = picam.capture_array()
        cv2.imshow("picam", frame) # ESTO A LO MEJOR HAY QUE HACERLO AL FINAL PARA EL TRACKER
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #if keys[key.SPACE]:
        if perf_counter()-t1 > 5:
            cv2.imwrite(f'patterns/img{idx}.jpg', frame)
            idx += 1
            t1 = perf_counter()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    stream_video()