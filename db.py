# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
from pony.orm import *
from config import *
from detect import detect_persons

db = Database()


class User(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')

    first_name = Required(unicode)
    last_name = Required(unicode)
    username = Required(unicode)

    sessions = Set('Session')


class Photo(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    sessions = Set('Session')

    width = Required(int)
    height = Required(int)

    file_origin = Required(unicode)
    file_path = Optional(unicode)
    file_id = Required(unicode)

    features = Set('Feature')
    overlays = Set('Overlay')


class Overlay(db.Entity):
    photo = Required(Photo)
    type = Required(int)

    name = Required(unicode)
    image = Required(unicode)

    width = Required(int)
    height = Required(int)


FEATURE_TYPE_FACE = 0
FEATURE_TYPE_EYE = 1
FEATURE_TYPE_NOSE = 2
FEATURE_TYPE_MOUTH = 3


class Feature(db.Entity):
    photo = Required(Photo)
    type = Required(int)

    x1 = Required(int)
    y1 = Required(int)

    x2 = Required(int)
    y2 = Required(int)

    width = Required(int)
    height = Required(int)

    parent = Optional('Feature', reverse='children')
    children = Set('Feature', reverse='parent')

    def get_type_title(self):
        if self.type == FEATURE_TYPE_FACE:
            return 'face'
        elif self.type == FEATURE_TYPE_EYE:
            return 'eye'
        elif self.type == FEATURE_TYPE_NOSE:
            return 'nose'
        elif self.type == FEATURE_TYPE_MOUTH:
            return 'mouth'

    def get_color(self):
        if self.type == FEATURE_TYPE_FACE:
            return 255, 0, 0
        elif self.type == FEATURE_TYPE_EYE:
            return 0, 255, 0
        elif self.type == FEATURE_TYPE_NOSE:
            return 0, 255, 255
        elif self.type == FEATURE_TYPE_MOUTH:
            return 0, 0, 255
        else:
            return 0, 0, 0


SESSION_STATUS_OPEN = 0
SESSION_STATUS_CLOSE = 1
SESSION_STATUS_CURRENT = 2


class Session(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    name = Required(unicode, unique=True)
    photo = Optional(Photo)
    user = Required(User)

    chat_id = Required(int)
    status = Required(int)


db.bind('postgres', user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME)
db.generate_mapping(create_tables=True)


@db_session
def create_feature(params, feature_type, photo, parent=None):
    x, y, width, height = map(int, params)

    return Feature(
        photo=photo, type=feature_type,
        x1=x, y1=y, x2=x + width, y2=y + height,
        width=width, height=height,
        parent=parent,
    )


@db_session
def photo_exists(file_id):
    return Photo.exists(file_id=file_id)


@db_session
def get_features(photo_id):
    return list(select(f for f in Feature if f.photo==Photo[photo_id]))


@db_session
def create_photo(user_id, photo_path, chat_id, width, height, file_id):
    user = User[user_id]
    session = Session.get(user=user, chat_id=chat_id)

    photo = Photo(
        width=width,
        height=height,
        file_origin=photo_path,
        file_id=file_id,
    )

    session.photo = photo

    for person in detect_persons(photo_path):
        parent = create_feature(person['face'], FEATURE_TYPE_FACE, photo)

        for eye in person['eyes']:
            create_feature(eye, FEATURE_TYPE_EYE, photo, parent=parent)

        for nose in person['noses']:
            create_feature(nose, FEATURE_TYPE_NOSE, photo, parent=parent)

        for mouth in person['mouths']:
            create_feature(mouth, FEATURE_TYPE_MOUTH, photo, parent=parent)


@db_session
def get_user_id(first_name, last_name):
    user = User.get(first_name=first_name, last_name=last_name)

    if user:
        return user.id


@db_session
def create_user(first_name, last_name, username):
    if not User.get(first_name=first_name, last_name=last_name):
        User(
            first_name=first_name,
            last_name=last_name,
            username=username,
        )


# session

@db_session
def create_session(name, chat_id, user_id):
    user = User[user_id]
    Session(name=name, user=user, chat_id=chat_id, status=SESSION_STATUS_CURRENT)


@db_session
def use_session(user_id, session_id):
    user = User[user_id]
    session = Session.get(user=user, status=SESSION_STATUS_CURRENT)
    session.status = SESSION_STATUS_OPEN

    Session[session_id].status = SESSION_STATUS_CURRENT


@db_session
def close_session(chat_id, user):
    session = Session.get(chat_id=chat_id, user=user)
    session.status = SESSION_STATUS_CLOSE


@db_session
def get_file_origin(photo_id):
    return Photo[photo_id].file_origin


@db_session
def get_current_photo_id():
    session_id = get_current_session_id()
    return Session[session_id].photo.id


@db_session
def get_current_session_id():
    return Session.get(status=SESSION_STATUS_CURRENT).id


@db_session
def get_session_by_name(name):
    return Session.get(name=name).id


@db_session
def get_session_list(user_id):
    return list(select(s for s in Session if s.user == User[user_id]))
