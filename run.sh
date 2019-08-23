#!/bin/bash


django-admin startproject webpage
cd webpage
pythons manage.py startapp mng
python manage.py runserver 0.0.0.0:8000