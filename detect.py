import cv2
import os.path
from PIL import Image

# this code is taken from https://github.com/nagadomi/lbpcascade_animeface
# it has been edited to to increase the rectangle around the detected face and to crop the images
# and copy them to ./cropped/img_name.extension


def detect(filename, cascade_file=r"C:\Users\sloth\Desktop\anime-crop\lbpcascade_animeface\lbpcascade_animeface.xml"):


    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)

    cascade = cv2.CascadeClassifier(cascade_file)
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # detecting faces
    faces = cascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor=1.1,
                                     minNeighbors=5,
                                     minSize=(24, 24))

    top_shift_scale = 0.5  # param
    x_scale = 0.25  # param

    count = 1

    for (x, y, w, h) in faces:

        y_shift = int(h * top_shift_scale)
        x_shift = int(w * x_scale)

        # cv2.rectangle(image, (x - x_shift, y - y_shift), (x + w + x_shift, y + h), (0, 0, 255), 2)

        im = image[y - y_shift:y + h, x - x_shift:x + w + x_shift]

        # reordering colours for PIL
        im = im[:, :, ::-1]

        crop_image = Image.fromarray(im)

        if count == 1:
            output_loc = "./cropped/" + filename.split("\\")[1]
        else:
            output_loc = "./cropped/" + str(count) + filename.split("\\")[1]

        crop_image.save(fp=output_loc)
        count += 1

    #     for (x, y, w, h) in faces:
    #         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    #cv2.imshow("AnimeFaceDetect", im)
    #cv2.waitKey(0)
