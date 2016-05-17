# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pony.orm import *


db = Database()


class User(db.Entity):
    date_create = Required(datetime)
    first_name = Required(unicode)
    last_name = Required(unicode)
    username = Required(unicode)


class FaceImage(db.Entity):
    date_create = Required(datetime)

    width = Required(int)
    height = Required(int)

    file_origin = Required(unicode)
    file_path = Required(unicode)
    file_token = Required(unicode)

    features = Set('Feature')
    overlays = Set('Overlay')


class Overlay(db.Entity):
    type = Required(int)

    name = Required(unicode)
    image = Required(unicode)

    width = Required(int)
    height = Required(int)


class Feature(db.Entity):
    type = Required(int)

    x1 = Required(int)
    y1 = Required(int)

    x2 = Required(int)
    y2 = Required(int)

    width = Required(int)
    height = Required(int)


class Session(db.Entity):
    date_create = Required(datetime)
    face_image = Required(FaceImage)
    user = Required(User)

    chat_token = Required(int)
    status = Required(int)


# @db_session
# def print_person_name(person_id):
#     p = Person[person_id]
#     print p.name


# PostgreSQL
# db.bind('postgres', user='', password='', host='', database='')
# db.generate_mapping(create_tables=True)
