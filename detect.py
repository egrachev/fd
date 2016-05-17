# -*- coding: utf-8 -*-

import numpy as np
import cv2


face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('cascades/haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('cascades/haarcascade_mcs_mouth.xml')
nose_cascade = cv2.CascadeClassifier('cascades/haarcascade_mcs_nose.xml')

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

        self.width = width
        self.height = height

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

    def resize(self, overlay, width):
        ratio = float(width) / overlay.shape[1]
        dim = (int(width), int(overlay.shape[0] * ratio))
        result = cv2.resize(overlay, dim, interpolation=cv2.INTER_AREA)

        return result

    def draw_eyes(self, image, overlay):
        pass

    def draw_nose(self, image, overlay):
        nose = self.noses[0]

        overlay_resized = self.resize(overlay, nose.width)
        overlay_height, overlay_width, channels = overlay_resized.shape

        # center
        roi_x1 = nose.x1 + abs(nose.width - overlay_width) / 2
        # roi_y1 = nose.y1 + abs(nose.height - overlay_height) / 2
        roi_y1 = nose.y2 - overlay_height

        roi = image[roi_y1:roi_y1 + overlay_height, roi_x1:roi_x1 + overlay_width]

        # Now create a mask of logo and create its inverse mask also
        overlay_gray = cv2.cvtColor(overlay_resized, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(overlay_gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Now black-out the area of logo in ROI
        image_bg = cv2.bitwise_and(roi, roi, mask=mask)

        # Take only region of logo from logo image.
        overlay_fg = cv2.bitwise_and(overlay_resized, overlay_resized, mask=mask_inv)

        # Put logo in ROI and modify the main image
        image[roi_y1:roi_y1 + overlay_height, roi_x1:roi_x1 + overlay_width] = cv2.add(image_bg, overlay_fg)

    def draw_mouth(self, image, overlay):
        pass

    def draw_rects(self, image):
        self.face.draw_rect(image, COLOR_FACE)

        for eye_rect in self.eyes:
            eye_rect.draw_rect(image, COLOR_EYE)

        for nose_rect in self.noses:
            nose_rect.draw_rect(image, COLOR_NOSE)

        for mouth_rect in self.mouths:
            mouth_rect.draw_rect(image, COLOR_MONTH)


def detect_feature(cascade, image, rel_x=0, rel_y=0):
    result = []
    feature_list = cascade.detectMultiScale(image, FEATURE_SCALE, FEATURE_MIN_NEIGHBORS)

    for feature in feature_list:
        x, y, width, height = feature

        if rel_x or rel_y:
            x += rel_x
            y += rel_y

        feature_rect = Rectangle(x, y, width, height)
        result.append(feature_rect)

    return result


def detect_persons(image):
    persons = []

    image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = detect_feature(face_cascade, image_gray)

    for face_rect in face_list:
        person = Person()
        person.face = face_rect

        image_gray_face = face_rect.slice_image(image_gray)

        person.eyes = detect_feature(eye_cascade, image_gray_face, face_rect.x1, face_rect.y1)
        person.noses = detect_feature(nose_cascade, image_gray_face, face_rect.x1, face_rect.y1)
        person.mouths = detect_feature(mouth_cascade, image_gray_face, face_rect.x1, face_rect.y1)

        persons.append(person)
        person.draw_rects(image)

    return persons

img = cv2.imread('test.jpg')
persons = detect_persons(img)
person = persons[0]
overlay = cv2.imread('mustache.png')
person.draw_nose(img, overlay)

cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.imshow('img', img)

cv2.waitKey(0)
cv2.destroyAllWindows()
