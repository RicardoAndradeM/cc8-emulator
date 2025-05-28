from .keys import Key
from pygame.key import get_pressed
import pygame

class Keyboard:

    def __init__(self):
        self.keys = {
            Key.K_0 : False,
            Key.k_1 : False,
            Key.K_2 : False,
            Key.K_3 : False,
            Key.K_4 : False,
            Key.K_5 : False,
            Key.K_6 : False,
            Key.K_7 : False,
            Key.K_8 : False,
            Key.K_9 : False,
            Key.K_A : False,
            Key.K_B : False,
            Key.K_C : False,
            Key.K_D : False,
            Key.K_E : False,
            Key.K_F : False,
        }

        self.keysMaping = {
            Key.K_0 : pygame.K_x,
            Key.k_1 : pygame.K_1,
            Key.K_2 : pygame.K_2,
            Key.K_3 : pygame.K_3,
            Key.K_4 : pygame.K_q,
            Key.K_5 : pygame.K_w,
            Key.K_6 : pygame.K_e,
            Key.K_7 : pygame.K_a,
            Key.K_8 : pygame.K_s,
            Key.K_9 : pygame.K_d,
            Key.K_A : pygame.K_z,
            Key.K_B : pygame.K_c,
            Key.K_C : pygame.K_4,
            Key.K_D : pygame.K_r,
            Key.K_E : pygame.K_f,
            Key.K_F : pygame.K_v
        }

    def updateKeysPressed(self):
        keys_pressed = get_pressed()
        for key in self.keys:
            self.keys[key] = keys_pressed[self.keysMaping[key]]

    def keyIsPressed(self, key):
        return self.keys[key]
    
    # TODO: criar metodo para personalizar mapeamento de botões