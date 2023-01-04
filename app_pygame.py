import pygame
import math
import numpy as np
import random

class App:
    def __init__(self):
        self.h = 1080
        self.w = 1920

        self.win = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Traffic Light")

        # settings
        self.wanted_cars = 100
        self.green_time = 100
        self.yellow_time = 30
        self.timer = 400
        self.active_light = 0
        self.is_yellow = False
        self.skip_0 = 22
        self.skip_1 = 22
        self.skip_2 = 22
        self.skip_3 = 22
        self.skip_4 = 22

        self.violation_timer = 1000
        self.wanted_violation = 1 # 0 = No violation, 1 = car, 2 = pedestrian
        self.wanted_vehicles_in_violation = 1
        self.veh_in_violation = 0
        self.red_crossing = False
        self.crash_happening = False
        self.crash_timer = 0
        self.resolve_timer = 100

        # groups
        self.car_group = pygame.sprite.RenderPlain()
        self.heli_group = pygame.sprite.RenderPlain()

        # colors
        self.dark_red = (60,0,0)
        self.dark_green = (0,60,0)
        self.dark_yellow = (60,60,0)
        self.red = (255,0,0)
        self.green = (0,255,0)
        self.yellow = (255,255,0)
        self.vehicle_type_traffic = pygame.transform.scale(pygame.image.load("images/bike_symbol.png"),(30, 30))
        self.ped_symbol_go = pygame.transform.scale(pygame.image.load("images/ped_symbol_go.png"),(30, 30))
        self.ped_symbol_stop = pygame.transform.scale(pygame.image.load("images/ped_symbol_stop.png"),(30, 30))
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)

        self.main()


    def background(self):
        self.win.blit( pygame.transform.scale(pygame.image.load("images/intersection.png"),(self.w, self.h)),(0,0))
        # Traffic light 0
        rectangle = pygame.Rect(1110,730, 40, 110)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (1130, 750), 15)
        pygame.draw.circle(self.win, self.dark_yellow, (1130, 785), 15)
        pygame.draw.circle(self.win, self.dark_green, (1130, 820), 15)

        # Traffic light 1
        rectangle = pygame.Rect(1350,280, 110, 40)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (1370, 300), 15)
        pygame.draw.circle(self.win, self.dark_yellow, (1405, 300), 15)
        pygame.draw.circle(self.win, self.dark_green, (1440, 300), 15)

        # Traffic light 1.5 (bycicle) 
        rectangle = pygame.Rect(1250,280, 75, 40)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (1270, 300), 15)
        self.win.blit(self.vehicle_type_traffic, (1255,285))
        pygame.draw.circle(self.win, self.dark_green, (1305, 300), 15)
        self.win.blit(self.vehicle_type_traffic, (1290,285))

        # Traffic light 2
        rectangle = pygame.Rect(700,200, 40, 110)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (720, 290), 15)
        pygame.draw.circle(self.win, self.dark_yellow, (720, 255), 15)
        pygame.draw.circle(self.win, self.dark_green, (720, 220), 15)

        # Traffic light 3
        rectangle = pygame.Rect(500,710, 110, 40)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (590, 730), 15)
        pygame.draw.circle(self.win, self.dark_yellow, (555, 730), 15)
        pygame.draw.circle(self.win, self.dark_green, (520, 730), 15)

        # Traffic light 4 (pedestrians)
        rectangle = pygame.Rect(630,235, 40, 75)
        pygame.draw.rect(self.win, (0,0,0), rectangle)
        pygame.draw.circle(self.win, self.dark_red, (650, 255), 15)
        self.win.blit(self.ped_symbol_stop, (635,240))
        pygame.draw.circle(self.win, self.dark_green, (650, 290), 15)
        self.win.blit(self.ped_symbol_go, (635,275))

        # violation
        if self.veh_in_violation and self.red_crossing:
            if self.wanted_violation == 1:
                text = self.font.render("CAR VIOLATION DETECTED!",True,(255,0,0),(0,0,0))
            else:
                text = self.font.render("PEDESTRIAN VIOLATION DETECTED!",True,(255,0,0),(0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (400,100)
            self.win.blit(text, text_rect)



    def set_lights(self):
        # crash
        if self.crash_happening is True:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.active_light = -1
            self.is_yellow = -1
            return
        if self.timer > 400:
            self.wanted_violation = 1
        else:
            self.wanted_violation = 2
        # Light 0
        if self.timer > 0 and self.timer < self.yellow_time:
            pygame.draw.circle(self.win, self.yellow, (1130, 785), 15) # Light 0 = yellow
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.active_light = -1 # no active light
            self.is_yellow = 0
        elif self.timer >= self.yellow_time and self.timer < self.yellow_time + self.green_time:
            pygame.draw.circle(self.win, self.green, (1130, 820), 15) # Light 0 = green
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = 0
        elif self.timer >= self.yellow_time + self.green_time and self.timer < 2*self.yellow_time + self.green_time:
            pygame.draw.circle(self.win, self.yellow, (1130, 785), 15) # light 0 = yellow
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 0
            self.active_light = -1
        # light 1 active phase
        elif self.timer >= 2*self.yellow_time + self.green_time and self.timer < 3*self.yellow_time + self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.yellow, (1405, 300), 15) # Light 1 = yellow
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 1
            self.active_light = -1
        elif self.timer >= 3*self.yellow_time + self.green_time and self.timer < 3*self.yellow_time + 2*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.green, (1440, 300), 15) # Light 1 = green
            pygame.draw.circle(self.win, self.green, (1305, 300), 15) # Light 1.5 = green
            self.win.blit(self.vehicle_type_traffic, (1290,285)) 
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = 1
        elif self.timer >= 3*self.yellow_time + 2*self.green_time and self.timer < 4*self.yellow_time + 2*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.yellow, (1405, 300), 15) # Light 1 = yellow
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 1
            self.active_light = -1
        # light 2 active phase
        elif self.timer >= 4*self.yellow_time + 2*self.green_time and self.timer < 5*self.yellow_time + 2*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.yellow, (720, 255), 15) # Light 2 = yellow
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 2
            self.active_light = -1
        elif self.timer >= 5*self.yellow_time + 2*self.green_time and self.timer < 5*self.yellow_time + 3*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.green, (720, 220), 15) # Light 2 = green
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = 2
        elif self.timer >= 5*self.yellow_time + 3*self.green_time and self.timer < 6*self.yellow_time + 3*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.yellow, (720, 255), 15) # Light 2 = yellow
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 2
            self.active_light = -1
        # Light 3 active phase
        elif self.timer >= 6*self.yellow_time + 3*self.green_time and self.timer < 7*self.yellow_time + 3*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.yellow, (555, 730), 15) # Light 3 = yellow
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 3
            self.active_light = -1
        elif self.timer >= 7*self.yellow_time + 3*self.green_time and self.timer < 7*self.yellow_time + 4*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.green, (520, 730), 15) # Light 3 = green
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = 3
        elif self.timer >= 7*self.yellow_time + 4*self.green_time and self.timer < 8*self.yellow_time + 4*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.yellow, (555, 730), 15) # Light 3 = yellow
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = 3
            self.active_light = -1
        # Light 4 active phase
        elif self.timer >= 8*self.yellow_time + 4*self.green_time and self.timer < 9*self.yellow_time + 4*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = -1
        elif self.timer >= 9*self.yellow_time + 4*self.green_time and self.timer < 9*self.yellow_time + 5*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.green, (650, 290), 15) # light 4 = green
            self.win.blit(self.ped_symbol_go, (635,275))
            self.is_yellow = -1
            self.active_light = 4
        elif self.timer >= 9*self.yellow_time + 5*self.green_time and self.timer < 10*self.yellow_time + 5*self.green_time:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.is_yellow = -1
            self.active_light = -1
        

        if self.timer < 10*self.yellow_time + 5*self.green_time:
            self.timer += 1
        else:
            pygame.draw.circle(self.win, self.red, (1130, 750), 15) # Light 0 = red
            pygame.draw.circle(self.win, self.red, (1370, 300), 15) # Light 1 = red
            pygame.draw.circle(self.win, self.red, (1270, 300), 15) # Light 1.5 = red
            self.win.blit(self.vehicle_type_traffic, (1255,285))
            pygame.draw.circle(self.win, self.red, (720, 290), 15) # light 2 = red
            pygame.draw.circle(self.win, self.red, (590, 730), 15)  # light 3 = red
            pygame.draw.circle(self.win, self.red, (650, 255), 15) # light 4 = red
            self.win.blit(self.ped_symbol_stop, (635,240))
            self.timer = 1
        
    def force_violation(self):
        for i in range(len(self.car_group.sprites())):
            if self.car_group.sprites()[i].first_at_light is True:
                # pedestrians
                if self.car_group.sprites()[i].vehicle_type >= 4 and self.car_group.sprites()[i].vehicle_type <= 7 and self.wanted_violation == 2 and self.veh_in_violation < self.wanted_vehicles_in_violation:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.car_group.sprites()[i].in_violation = True
                    self.veh_in_violation += 1
                    return
                elif (self.car_group.sprites()[i].vehicle_type  < 4  or self.car_group.sprites()[i].vehicle_type  > 7) and self.veh_in_violation < self.wanted_vehicles_in_violation and self.wanted_violation == 1:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.car_group.sprites()[i].in_violation = True
                    self.veh_in_violation += 1
                    return
    
    def resolve_crash(self):
        if self.resolve_timer < 100:
            self.resolve_timer -= 1
            self.crash_happening = True
            self.start_at_crash()
        if self.resolve_timer == 0:
            self.resolve_timer = 100
            self.crash_timer = 0
        elif self.crash_happening is True and self.crash_timer > 100:
            if self.heli_group.sprites()[0].endposition is True:
                for i in range(len(self.car_group.sprites())):
                    if self.car_group.sprites()[i].in_violation is True:
                        self.car_group.sprites()[i].red_crossing = False
                        self.veh_in_violation -= 1
                        del self.car_group.sprites()[i]
                        self.car_group.remove(self.car_group.sprites()[i])
                        self.heli_group.sprites()[0].x = -600
                        self.resolve_timer -=1
                        break


    def violation_crash_check(self):
        for i in range(len(self.car_group.sprites())):
            if self.car_group.sprites()[i].in_violation is True and self.car_group.sprites()[i].velocity == (0,0):
                self.crash_timer += 1
                if self.crash_timer > 50:
                    self.crash_happening = True
                    if len(self.heli_group.sprites()) < 1:
                        heli = helicopter(self.car_group.sprites()[i].rect.x,self.car_group.sprites()[i].rect.y)
                        self.heli_group.add(heli)
                break
            else:
                self.crash_happening = False
                

    def stop_at_red(self):
        for i in range(len(self.car_group.sprites())):
            # if car is in violation skip
            if self.car_group.sprites()[i].in_violation is True:
                if self.car_group.sprites()[i].velocity == (0,-20) and self.is_yellow == 0:
                    self.red_crossing = False
                elif self.car_group.sprites()[i].velocity == (-20,0) and self.is_yellow == 1:
                    self.red_crossing = False
                elif self.car_group.sprites()[i].velocity == (0,20) and self.is_yellow == 2:
                    self.red_crossing = False
                elif self.car_group.sprites()[i].velocity == (20,0) and self.is_yellow == 3:
                    self.red_crossing = False
                else:
                    self.red_crossing = True
                continue

            # stop for traffic light 0
            if self.car_group.sprites()[i].velocity == (0,-20) and self.active_light != 0 and self.car_group.sprites()[i].rect.y > 820 and self.car_group.sprites()[i].rect.y < 850:
                self.car_group.sprites()[i].velocity = (0,0)
                self.car_group.sprites()[i].first_at_light = True

            
            # stop at light 1
            elif self.car_group.sprites()[i].vehicle_type < 4 and self.car_group.sprites()[i].velocity == (-20,0) and self.active_light != 1 and self.car_group.sprites()[i].rect.x > 1330 and self.car_group.sprites()[i].rect.x < 1370:
                self.car_group.sprites()[i].velocity = (0,0)
                #self.car_group.sprites()[i].first_at_light = True


            # stop at light 1.5 (bikes)
            elif self.car_group.sprites()[i].velocity == (-20,0) and self.active_light != 1 and self.car_group.sprites()[i].rect.x > 1230 and self.car_group.sprites()[i].rect.x < 1270:
                self.car_group.sprites()[i].velocity = (0,0) 
                self.car_group.sprites()[i].first_at_light = True

            
            # stop at light 2
            elif self.car_group.sprites()[i].velocity == (0,20) and self.active_light != 2 and self.car_group.sprites()[i].rect.y > 110 and self.car_group.sprites()[i].rect.y < 160:
                self.car_group.sprites()[i].velocity = (0,0)
                self.car_group.sprites()[i].first_at_light = True


            # stop at light 3
            elif self.car_group.sprites()[i].velocity == (20,0) and self.active_light != 3 and self.car_group.sprites()[i].rect.x > 400 and self.car_group.sprites()[i].rect.x < 440:
                self.car_group.sprites()[i].velocity = (0,0)

            # stop at light 4
            elif self.car_group.sprites()[i].start_angle == 270 and self.car_group.sprites()[i].vehicle_type >= 4 and self.car_group.sprites()[i].vehicle_type < 8 and self.active_light != 4 and self.car_group.sprites()[i].rect.x > 650 and self.car_group.sprites()[i].rect.x < 665:
                self.car_group.sprites()[i].velocity = (0,0)
                self.car_group.sprites()[i].first_at_light = True

    def start_at_crash(self):
        if self.skip_0 > 0:
            self.skip_0 -=1
        if self.skip_1 > 0:
            self.skip_1 -=1
        if self.skip_2 > 0:
            self.skip_2 -=1
        if self.skip_3 > 0:
            self.skip_3 -=1
        if self.skip_4 > 0:
            self.skip_4 -=1
        
            
        # start the cars again
        for i in range(len(self.car_group.sprites())):
            if self.car_group.sprites()[i].velocity == (0,0):
                # start light 0
                if self.skip_0 == 0 and self.car_group.sprites()[i].orig_velocity == (0,-20) and self.car_group.sprites()[i].rect.y < 820:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].prev_velocity
                    self.skip_0 = 22

                    
                # start light 1
                if self.skip_1 == 0 and self.car_group.sprites()[i].orig_velocity == (-20,0) and self.car_group.sprites()[i].rect.x < 1220:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].prev_velocity
                    self.skip_1 = 22
                    

                    
                # start light 2
                if self.skip_2 == 0 and self.car_group.sprites()[i].orig_velocity == (0,20) and self.car_group.sprites()[i].rect.y > 160:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].prev_velocity
                    self.skip_2 = 22

                    
                # start light 3
                if self.skip_3 == 0 and self.car_group.sprites()[i].orig_velocity == (20,0) and self.car_group.sprites()[i].rect.x > 440:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].prev_velocity
                    self.skip_3 = 22


                # start light 4
                if self.skip_4 == 0 and self.car_group.sprites()[i].start_angle == 270 and self.car_group.sprites()[i].vehicle_type >= 4 and self.car_group.sprites()[i].vehicle_type < 8 and self.car_group.sprites()[i].rect.x > 650:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].prev_velocity
                    self.skip_4 = 22


    def start_at_red(self):
        if self.resolve_timer != 100:
            return
        if self.skip_0 > 0:
            self.skip_0 -=1
        if self.skip_1 > 0:
            self.skip_1 -=1
        if self.skip_2 > 0:
            self.skip_2 -=1
        if self.skip_3 > 0:
            self.skip_3 -=1
        if self.skip_4 > 0:
            self.skip_4 -=1
        
            
        # start the cars again
        for i in range(len(self.car_group.sprites())):
            if self.car_group.sprites()[i].velocity == (0,0):
                # start light 0
                if self.skip_0 == 0 and self.car_group.sprites()[i].orig_velocity == (0,-20) and self.car_group.sprites()[i].rect.y > 820:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.skip_0 = 22
                    self.car_group.sprites()[i].first_at_light = False

                    
                # start light 1
                if self.skip_1 == 0 and self.car_group.sprites()[i].orig_velocity == (-20,0) and self.car_group.sprites()[i].rect.x > 1220:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.skip_1 = 22
                    self.car_group.sprites()[i].first_at_light = False

                    
                # start light 2
                if self.skip_2 == 0 and self.car_group.sprites()[i].orig_velocity == (0,20) and self.car_group.sprites()[i].rect.y < 160:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.skip_2 = 22
                    self.car_group.sprites()[i].first_at_light = False

                    
                # start light 3
                if self.skip_3 == 0 and self.car_group.sprites()[i].orig_velocity == (20,0) and self.car_group.sprites()[i].rect.x < 440:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.skip_3 = 22
                    self.car_group.sprites()[i].first_at_light = False


                # start light 4
                if self.skip_4 == 0 and self.car_group.sprites()[i].start_angle == 270 and self.car_group.sprites()[i].vehicle_type >= 4 and self.car_group.sprites()[i].vehicle_type < 8 and self.car_group.sprites()[i].rect.x < 675:
                    self.car_group.sprites()[i].velocity = self.car_group.sprites()[i].orig_velocity
                    self.skip_4 = 22
                    self.car_group.sprites()[i].first_at_light = False


    def main(self):
        exit = False
        timeout = 5
  
        while not exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True

            # update step 1
            self.background()
            self.set_lights()
            self.start_at_red()
            self.stop_at_red()
            self.resolve_crash()
            self.car_group.update()
            self.car_group.draw(self.win)
            self.heli_group.update()
            self.heli_group.draw(self.win)

            # add cars at random
            if timeout == 0 and len(self.car_group.sprites()) < self.wanted_cars:
                car = Car()
                margin_width = 100
                margin_height = 100
                car.rect = pygame.Rect((car.rect.x, car.rect.y), (car.rect.width + margin_width, car.rect.height + margin_height))                
                
                hit_on_spawn = False
                for i in range(len(self.car_group)):
                    if pygame.sprite.collide_rect_ratio(3)(car, self.car_group.sprites()[i]):
                        hit_on_spawn = True
                        break

                if not hit_on_spawn:
                    self.car_group.add(car)
                    timeout = 20
                else:
                    del car
            
            # violation
            self.violation_crash_check()
            if self.wanted_violation != 0:
                self.force_violation()    

            # check for collision
            coll_indices = self.collision()
            for i in coll_indices:
                if self.car_group.sprites()[i["index"]].velocity != (0,0):
                    if self.car_group.sprites()[i["index"]].turn_iteration == 3:
                        self.car_group.sprites()[i["index"]].prev_velocity = self.car_group.sprites()[i["index"]].velocity
                    else:
                        if self.car_group.sprites()[i["index"]].orig_velocity == (20,0):
                            if self.car_group.sprites()[i["index"]].left:
                                self.car_group.sprites()[i["index"]].prev_velocity = (0,-20)
                            else:
                                self.car_group.sprites()[i["index"]].prev_velocity = (0,20)
                        if self.car_group.sprites()[i["index"]].orig_velocity == (0,20):
                            if self.car_group.sprites()[i["index"]].left:
                                self.car_group.sprites()[i["index"]].prev_velocity = (20,0)
                            else:
                                self.car_group.sprites()[i["index"]].prev_velocity = (-20,0)
                        if self.car_group.sprites()[i["index"]].orig_velocity == (0,-20):
                            if self.car_group.sprites()[i["index"]].left:
                                self.car_group.sprites()[i["index"]].prev_velocity = (-20,0)
                            else:
                                self.car_group.sprites()[i["index"]].prev_velocity = (20,0)
                        if self.car_group.sprites()[i["index"]].orig_velocity == (-20,0):
                            if self.car_group.sprites()[i["index"]].left:
                                self.car_group.sprites()[i["index"]].prev_velocity = (0,20)
                            else:
                                self.car_group.sprites()[i["index"]].prev_velocity = (0,-20)

                self.car_group.sprites()[i["index"]].velocity = (0,0)            

            #update step 2
            pygame.display.update()
            self.in_frame()
            if timeout > 0:
                timeout -=1
            self.clock.tick(400)

    def collision(self):
        # collision
        coll_indices = []
        for i in range(0,len(self.car_group)):
            for j in range(0,len(self.car_group)):
                if j != i and pygame.sprite.collide_rect(self.car_group.sprites()[j], self.car_group.sprites()[i]):                    
                    coll_dict = {"index" : i, "angle" : self.car_group.sprites()[i].angle, "x":self.car_group.sprites()[i].rect.x, "y":self.car_group.sprites()[i].rect.y}
                    coll_indices.append(coll_dict)
                    break
        return coll_indices

    def in_frame(self):
        # remove a object if its outside the frame
        delete_index = []
        for i in range(len(self.car_group.sprites())):
            if self.car_group.sprites()[i].rect.x > self.w + 400 or self.car_group.sprites()[i].rect.y > self.h + 400 or self.car_group.sprites()[i].rect.x < -400 or self.car_group.sprites()[i].rect.y < - 400:
                delete_index.append(i)
        for i in delete_index:   
            if self.car_group.sprites()[i].in_violation is True:
                self.veh_in_violation -= 1
                self.red_crossing = False
            self.car_group.remove(self.car_group.sprites()[i])
            del self.car_group.sprites()[i]


class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # variables
        self.velocity = (0,0)
        self.margin = 10
        self.angle = 270
        self.turn_marker = random.getrandbits(1)
        self.left = random.getrandbits(1)
        self.turn_iteration = 3
        self.start_angle = 270
        self.vehicle_type = np.random.choice([0,1,2,3,4,5,6,7,8,9], p=[0.17,0.17,0.17,0.19,0.05,0.05,0.05,0.05,0.05,0.05])
        self.in_violation = False
        self.first_at_light = False
        
        # load image
        if self.vehicle_type >= 0 and self.vehicle_type < 4:
            if random.getrandbits(1):
                self.car_image = pygame.transform.scale(pygame.image.load("images/car_yellow.png"), (96,192))
            else:
                self.car_image = pygame.transform.scale(pygame.image.load("images/car.png"), (96,192))
        elif self.vehicle_type >= 4 and self.vehicle_type < 8:
            self.turn_marker = 1
            if self.vehicle_type == 4:
                self.car_image = pygame.transform.scale(pygame.image.load("images/person1.png"), (71*0.8,45*0.8))
            elif self.vehicle_type == 5:
                self.car_image = pygame.transform.scale(pygame.image.load("images/person2.png"), (83*0.8,43*0.8))
            elif self.vehicle_type == 6:
                self.car_image = pygame.transform.scale(pygame.image.load("images/person3.png"), (60*0.8,45*0.8))
            elif self.vehicle_type == 7:
                self.car_image = pygame.transform.scale(pygame.image.load("images/person4.png"), (74*0.8,55*0.8))

        else:
            rand = np.random.randint(0,3)
            self.turn_marker = 0
            if rand == 0:
                self.car_image = pygame.transform.scale(pygame.image.load("images/bike1.png"), (52,114))
            if rand == 1:
                self.car_image = pygame.transform.scale(pygame.image.load("images/bike2.png"), (52,107))
            if rand == 2:
                self.car_image = pygame.transform.scale(pygame.image.load("images/bike3.png"), (55,103))
        # sprite variables
        self.image = pygame.transform.rotate(self.car_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.height += self.margin
        self.rect.width += self.margin

        #spawn
        self.set_random_start()
        self.orig_velocity = self.velocity
        self.prev_velocity = self.orig_velocity

    def set_random_start(self):
        rand = np.random.randint(0,4)
        # pedestrians
        if self.vehicle_type >=4 and self.vehicle_type <= 7:
            if rand == 0:
                self.rect.x = -100
                self.rect.y = 660
                self.velocity = (5,0)
                self.angle = 270
                self.start_angle = 270
            elif rand == 1:
                self.rect.x = 2050
                self.rect.y = 300
                self.velocity = (-5,0)
                self.angle = 90
                self.start_angle = 90
            elif rand == 2:
                self.rect.x = 1100
                self.rect.y = 1200
                self.velocity = (0,-5)
                self.angle = 0
                self.start_angle = 0
            elif rand == 3:
                self.rect.x = 2050
                self.rect.y = 300
                self.velocity = (-5,0)
                self.angle = 90
                self.start_angle = 90
            return

        if self.vehicle_type > 7:
            self.rect.x = 2200
            self.rect.y = 380
            self.velocity = (-20,0)
            self.angle = 90
            self.start_angle = 90
            return

        if rand == 0:
            self.rect.x = -300
            self.rect.y = 530
            self.velocity = (20,0)
            self.angle = 270
            self.start_angle = 270
        elif rand == 1:
            self.rect.x = 810
            self.rect.y = -400
            self.velocity = (0,20)
            self.angle = 180
            self.start_angle = 180
        elif rand == 2:
            self.rect.x = 965
            self.rect.y = 1180
            self.velocity = (0,-20)
            self.angle = 0
            self.start_angle = 0
        elif rand == 3:
            self.rect.x = 2200
            self.rect.y = 420
            self.velocity = (-20,0)
            self.angle = 90
            self.start_angle = 90
        
    def movement(self):
        v_mag = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        vx = - v_mag * math.sin(math.radians(self.angle))
        vy = - v_mag * math.cos(math.radians(self.angle))
        return (vx, vy)

    def turn(self):
        # pedestrians
        if self.vehicle_type >= 4 and self.vehicle_type < 8 and self.turn_iteration > 0:
            # forced turns
            if self.start_angle == 0 and self.rect.y < 730:
                self.angle -= 30
                self.velocity = self.movement()
                self.turn_iteration -= 1
            elif self.start_angle == 90 and self.rect.x < 1130 :
                self.angle -= 30
                self.velocity = self.movement()            
                self.turn_iteration -= 1
            elif self.start_angle == 180 and self.rect.y > 500 :
                self.angle += 30
                self.velocity = self.movement()            
                self.turn_iteration -= 1
            elif self.start_angle == 270 and self.rect.x > 720 :
                self.angle += 30
                self.velocity = self.movement()            
                self.turn_iteration -= 1
            return

        # cars
        if self.turn_iteration > 0:
            if self.left:
                # left turn bottom lane
                if self.start_angle == 0 and self.rect.y < 460:
                    self.angle += 30
                    self.velocity = self.movement()
                    self.turn_iteration -= 1
                elif self.start_angle == 90 and self.rect.x < 860:
                    self.angle += 30
                    self.velocity = self.movement()            
                    self.turn_iteration -= 1
                elif self.start_angle == 180 and self.rect.y > 480:
                    self.angle += 30
                    self.velocity = self.movement()            
                    self.turn_iteration -= 1
                elif self.start_angle == 270 and self.rect.x > 900:
                    self.angle += 30
                    self.velocity = self.movement()            
                    self.turn_iteration -= 1
            else:
                # right turn bottom lane
                if self.start_angle == 0 and self.rect.y < 570:
                    self.angle -= 30
                    self.velocity = self.movement()
                    self.turn_iteration -= 1               
                elif self.start_angle == 90 and self.rect.x < 990 :
                    self.angle -= 30
                    self.velocity = self.movement() 
                    self.turn_iteration -= 1
                elif self.start_angle == 180 and self.rect.y > 360 :
                    self.angle -= 30
                    self.velocity = self.movement() 
                    self.turn_iteration -= 1
                elif self.start_angle == 270 and self.rect.x > 775 :
                    self.angle -= 30
                    self.velocity = self.movement() 
                    self.turn_iteration -= 1

    def update(self):
        # new position
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # calculate heading
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            angle = int(math.degrees(math.tan(self.velocity[1]/self.velocity[0])))
        self.image = pygame.transform.rotate(self.car_image, self.angle)


        # update rectangle
        x1, y1, x2, y2 = self.image.get_rect()
        self.rect.width = x2 - x1
        self.rect.height = y2 - y1
        self.rect.height += self.margin
        self.rect.width += self.margin

        # check for turn
        if self.turn_marker:
            self.turn()

class helicopter(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("images/helicopter.png"), (258*1.5,206*1.5))
        self.rect = self.image.get_rect()
        self.x = x
        self.rect.y = y
        self.rect.x = 2100
        self.velocity = 40
        self.endposition = False
    def update(self):
        if self.rect.x > self.x:
            self.rect.x -= 40
        elif self.rect.x == -600:
            del self
        else:
            self.endposition = True
        
        



if __name__ == "__main__":
    app = App()