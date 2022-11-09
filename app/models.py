from django.db import models


TEST_TAGS = [
    { 'id': 0, 'name': 'C++'},
    { 'id': 1, 'name': 'C'},
    { 'id': 2, 'name': 'Ruby'},
    { 'id': 3, 'name': 'python'},
    { 'id': 4, 'name': 'OpenGL'},
    ]

TEST_QUESTIONS = [{ 
    'id': x, 
    'title': f'What is C++? {x}', 
    'text': f'Hey guys, I want to learn C++!!! But I don\'t know what does it mean((( {x}', 
    'avatar': f'img/avatar-{x % 4 + 1}.png', 
    'likes': 256 * (x % 3 + 1), 
    'answers_count': x, 
    'tags': [TEST_TAGS[x % len(TEST_TAGS)], TEST_TAGS[(x + 1) % len(TEST_TAGS)]] 
    } for x in range(100) ]


TEST_ANSWERS = [{ 
    'id': x, 
    'text': f'Just use python. lol {x}', 
    'avatar': f'img/avatar-{x % 4 + 1}.png', 
    'likes': -x, 
    'is_correct': (x + 2) % 4 == 0
    } for x in range(10) ]

TEST_PROFILE = {
    "id": 0,
    "name": "Mihail",
    "login": "microintex",
    "email": "lm@mail.ru",
    "nickname": "LM",
    "avatar": "img/avatar-4.png",
}