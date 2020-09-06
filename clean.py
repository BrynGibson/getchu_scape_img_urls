from pathlib import Path
from shutil import copyfile
import threading
import time
from PIL import Image

# this code is for opening all images and verifying that they are infact an image and not corrupt, also will filter out
# getchu placeholder images which are 1x1 white pixels


img_loc_gen = Path("./images").glob("*.*")
clean_loc = Path("./clean")

Path.mkdir(clean_loc, exist_ok=True)


def test(img_loc_gen):

    while True:
        try:
            img_loc = str(next(img_loc_gen))
            dest_loc = str(clean_loc) + "/" + img_loc.split('\\')[1]
            with Image.open(img_loc) as img: # open the image file
                img.verify() # verify that it is, in fact an image
                width, height = img.size
                if width > 1 and height > 1: # verify that the image is greater than 1 px
                    copyfile(img_loc, dest_loc)
        except StopIteration:
            print("end of images")
            break
        except ValueError:
            time.sleep(0.005)
        except (IOError, SyntaxError) as e:
            print(f'bad file {img_loc}, e: {e}')


for i in range(0, 50):
    threading.Thread(target=test, args=[img_loc_gen]).start()