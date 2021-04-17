"""
 File name   : util.py
 Description : description

 Date created : 11.04.2021
 Author:  Ihar Khakholka
"""


class SaveCallback:
    def __init__(self, path):
        self.path = path

    def __call__(self, html):
        with open(self.path, 'w', encoding='utf8') as f:
            f.write(html)