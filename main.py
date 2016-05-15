import numpy as np
import cv2


class Rectangle(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x1 = x
        self.y1 = y

        self.x2 = x + width
        self.y2 = y + height

    @property
    def point1(self):
        return self.x1, self.y1

    @property
    def point2(self):
        return self.x2, self.y2

    def draw(self, image, color, thickness=2):
        cv2.rectangle(image, self.point1, self.point2, color, thickness)

    def slice_image(self, image):
        return image[self.y1:self.y2, self.x1:self.x2]


class Person(object):
    def __init__(self):
        self.face = None
        self.eyes = []
        self.noses = None
        self.mouths = None


face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_mcs_mouth.xml')
nose_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_mcs_nose.xml')

COLOR_FACE = 255, 0, 0
COLOR_EYE = 0, 255, 0
COLOR_MONTH = 0, 0, 255
COLOR_NOSE = 0, 255, 255


def detect_feature()

def detect_persons(image):
    persons = []

    image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = face_cascade.detectMultiScale(image_gray, 1.3, 5)

    for face in face_list:
        person = Person()

        face_rect = Rectangle(*face)
        person.face = face_rect

        face_rect.draw(image, COLOR_FACE)

        face_gray_image = face_rect.slice_image(image_gray)
        face_color_image = face_rect.slice_image(image)

        eyes = eye_cascade.detectMultiScale(face_gray_image, 1.3, 10)
        for eye in eyes:
            eye_rect = Rectangle(*eye)
            eye_rect.draw(image, COLOR_EYE)

            person.eyes.append(Rectangle(*eye))

        mouth = mouth_cascade.detectMultiScale(face_gray_image, 1.3, 10)
        for mouth_x, mouth_y, mouth_width, mouth_height in mouth:
            cv2.rectangle(face_color_image, (mouth_x, mouth_y), (mouth_x + mouth_width, mouth_y + mouth_height), COLOR_MONTH, 2)

        nose = nose_cascade.detectMultiScale(face_gray_image, 1.3, 10)
        for nose_x, nose_y, nose_width, nose_height in nose:
            cv2.rectangle(face_color_image, (nose_x, nose_y), (nose_x + nose_width, nose_y + nose_height), COLOR_NOSE, 2)

        persons.append(person)

    return persons

# load input image in grayscale mode
img = cv2.imread('test.jpg')
detect_persons(img)


cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()