from pathlib import Path
from detect import detect
import threading
import time

# this code will crop anime pics down to just the face

img_loc_gen = Path("./clean").glob("*.*")

Path.mkdir(Path("./cropped"), exist_ok=True)

WORKERS = 50


def crop(img_loc_gen):

    count = 1
    while True:
        try:
            detect(str(next(img_loc_gen)))
            print(count)
            count += 1
        except StopIteration:
            print("end of images")
            break
        except ValueError:
            time.sleep(0.005)


for i in range(0, WORKERS):
    threading.Thread(target=crop, args=[img_loc_gen]).start()

