# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
from pony.orm import *
from config import *


db = Database()


class User(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')

    first_name = Required(unicode)
    last_name = Required(unicode)
    username = Required(unicode)

    sessions = Set('Session')


class FaceImage(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    sessions = Set('Session')

    width = Required(int)
    height = Required(int)

    file_origin = Required(unicode)
    file_path = Optional(unicode)
    file_token = Required(unicode)

    features = Set('Feature')
    overlays = Set('Overlay')


class Overlay(db.Entity):
    face_image = Required(FaceImage)
    type = Required(int)

    name = Required(unicode)
    image = Required(unicode)

    width = Required(int)
    height = Required(int)


class Feature(db.Entity):
    face_image = Required(FaceImage)
    type = Required(int)

    x1 = Required(int)
    y1 = Required(int)

    x2 = Required(int)
    y2 = Required(int)

    width = Required(int)
    height = Required(int)


SESSION_STATUS_OPEN = 0
SESSION_STATUS_CLOSE = 1
SESSION_STATUS_CURRENT = 2


class Session(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    name = Required(unicode, unique=True)
    face_image = Optional(FaceImage)
    user = Required(User)

    chat_token = Required(int)
    status = Required(int)


db.bind('postgres', user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME)
db.generate_mapping(create_tables=True)


@db_session
def get_user_id(first_name, last_name):
    return User.get(first_name=first_name, last_name=last_name).id


@db_session
def create_photo(user_id, photo_path, chat_id, width, height, file_id):
    user = User[user_id]
    session = Session.get(user=user, chat_token=chat_id)

    face_image = FaceImage(
        width=width,
        height=height,
        file_origin=photo_path,
        file_token=file_id,
    )

    session.face_image = face_image


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
    Session(name=name, user=user, chat_token=chat_id, status=SESSION_STATUS_CURRENT)


@db_session
def use_session(user_id, session_id):
    user = User[user_id]
    session = Session.get(user=user, status=SESSION_STATUS_CURRENT)
    session.status = SESSION_STATUS_OPEN

    Session[session_id].status = SESSION_STATUS_CURRENT


@db_session
def close_session(chat_id, user):
    session = Session.get(chat_token=chat_id, user=user)
    session.status = SESSION_STATUS_CLOSE


@db_session
def get_session_by_name(name):
    return Session.get(name=name).id


@db_session
def get_session_list(user_id):
    user = User[user_id]
    return list(Session.select(user=user))
