# -*- coding: utf-8 -*-

import numpy as np
import cv2


face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_mcs_mouth.xml')
nose_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_mcs_nose.xml')

COLOR_FACE = 255, 0, 0
COLOR_EYE = 0, 255, 0
COLOR_NOSE = 0, 255, 255
COLOR_MONTH = 0, 0, 255

FEATURE_SCALE = 1.3
FEATURE_MIN_NEIGHBORS = 10


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

    def draw_rect(self, image, color, thickness=2):
        cv2.rectangle(image, self.point1, self.point2, color, thickness)

    def slice_image(self, image):
        return image[self.y1:self.y2, self.x1:self.x2]


class Person(object):
    def __init__(self):
        self.face = None
        self.eyes = []
        self.noses = []
        self.mouths = []

    def draw_rects(self, image):
        self.face.draw_rect(image, COLOR_FACE)

        for eye_rect in self.eyes:
            eye_rect.draw_rect(image, COLOR_EYE)

        for nose_rect in self.noses:
            nose_rect.draw_rect(image, COLOR_NOSE)

        for mouth_rect in self.mouths:
            mouth_rect.draw_rect(image, COLOR_MONTH)


def detect_feature(cascade, image):
    result = []
    feature_list = cascade.detectMultiScale(image, FEATURE_SCALE, FEATURE_MIN_NEIGHBORS)

    for feature in feature_list:
        feature_rect = Rectangle(*feature)
        result.append(feature_rect)

    return result


def detect_persons(image):
    persons = []

    image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = detect_feature(face_cascade, image_gray)

    for face_rect in face_list:
        person = Person()
        person.face = face_rect

        face_rect.draw_rect(image, COLOR_FACE)

        face_gray_image = face_rect.slice_image(image_gray)
        face_color_image = face_rect.slice_image(image)

        person.eyes = detect_feature(eye_cascade, face_gray_image)
        person.noses = detect_feature(nose_cascade, face_gray_image)
        person.mouths = detect_feature(mouth_cascade, face_gray_image)

        persons.append(person)
        person.draw_rects(face_color_image)

    return persons

# load input image in grayscale mode
img = cv2.imread('test.jpg')
detect_persons(img)


cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()