from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""

import pygame
import os
import openai
import re
from os import path

from llama_index.node_parser import SimpleNodeParser
from llama_index import ServiceContext, set_global_service_context
from llama_index.llms import OpenAI
from llama_index.prompts import PromptTemplate
from llama_index import VectorStoreIndex, SimpleDirectoryReader

key = "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"
os.environ["OPENAI_API_KEY"] = key
openai.api_key = os.environ["OPENAI_API_KEY"]

documents = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
    
def load_data():
    response = query_engine.query("Create a unique quiz question and answer from the content. Put Q in front of the question, A in front of the answer.")
    print(response)

    q_and_a = (str(response)).split("A: ")
    return q_and_a

def load_data_questions():
    response = query_engine.query("Create a list of quiz questions and answers from the content. Put Q in front of the question, A in front of the answer.")
    print(response)

    #res = [sub.split("A: ") for sub in response]
    #print(str(res))
    
    #q_and_a = (str(response)).split("A: ")
    #return q_and_a

def check_answer(q, a):
    response = query_engine.query(f"Given question {q}, is the answer {a} correct?")
    return str(response)

pygame.init()
#clock = pygame.time.Clock()

screen = pygame.display.set_mode((1000, 1000), 0, 32)

load_data_questions()

all_sprites = pygame.sprite.Group()

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
img_dir = path.join(path.dirname(__file__), 'explosion')
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey((255, 255, 255))
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
        
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
                


question_rect = pygame.Rect(100, 100, 500, 100)
input_rect = pygame.Rect(100, 250, 500, 100)

color = pygame.Color('lightskyblue3')
#pygame.draw.rect(screen, color, input_rect)
#base_font = pygame.freetype.Font(None, 32)

ques_ans = load_data()

width = screen.get_width()
height = screen.get_height()
user_text = "A: "

font = pygame.font.SysFont("Comic Sans MS", 14)
ai_text_surface = font.render(ques_ans[0], True, (255, 255, 255))
user_text_surface = font.render(user_text, True, (255, 255, 255))

ans_button = font.render('answer' , True , color)
next_button = font.render('next', True, color)

done = False
while done == False:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            done = True
              
        #checks if a mouse is clicked
        if ev.type == pygame.MOUSEBUTTONDOWN:
            #if the mouse is clicked on the
            # button the game is terminated
            if 500 <= mouse[0] <= 640 and height/2 <= mouse[1] <= height/2+40:
                ai_text_surface = font.render(check_answer(ques_ans[0], user_text), True, (0, 60, 20))
                expl = Explosion((mouse[0], mouse[1]), 'lg')
                all_sprites.add(expl)
            elif 250 <= mouse[0] <= 400 and height/2 <= mouse[1] <= height/2+40:
                # Get next question
                ques_ans = load_data_again()
                ai_text_surface = font.render(ques_ans[0], True, (255, 255, 255))
                user_text = "A: "

        # Get user input
        if ev.type == pygame.KEYDOWN:
            # Check for backspace
            if ev.key == pygame.K_BACKSPACE:
                # get text input from 0 to -1 i.e. end.
                user_text = user_text[:-1]
                user_text_surface = font.render(user_text, True, (255, 255, 255))
  
            # Unicode standard is used for string
            # formation
            else:
                user_text += ev.unicode
                user_text_surface = font.render(user_text, True, (255, 255, 255))
                
    if (done == False):
        # fills the screen with a color
        screen.fill((0, 0, 0))
      
        # stores the (x,y) coordinates into
        # the variable as a tuple
        mouse = pygame.mouse.get_pos()

        pygame.draw.rect(screen, color, question_rect)
        pygame.draw.rect(screen, color, input_rect)

        all_sprites.update()
        
        # superimposing the text onto our button
        screen.blit(ans_button, (500,height/2))
        screen.blit(next_button, (250,height/2))
        screen.blit(ai_text_surface, (question_rect.x+5, question_rect.y+5))
        screen.blit(user_text_surface, (input_rect.x+5, input_rect.y+5))

        all_sprites.draw(screen)
        
        # updates the frames of the game
        pygame.display.update()


##with st.echo(code_location='below'):
##    total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
##    num_turns = st.slider("Number of turns in spiral", 1, 100, 9)
##
##    Point = namedtuple('Point', 'x y')
##    data = []
##
##    points_per_turn = total_points / num_turns
##
##    for curr_point_num in range(total_points):
##        curr_turn, i = divmod(curr_point_num, points_per_turn)
##        angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
##        radius = curr_point_num / total_points
##        x = radius * math.cos(angle)
##        y = radius * math.sin(angle)
##        data.append(Point(x, y))
##
##    st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
##        .mark_circle(color='#0068c9', opacity=0.5)
##        .encode(x='x:Q', y='y:Q'))
