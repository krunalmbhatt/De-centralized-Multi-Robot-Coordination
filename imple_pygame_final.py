#!/usr/bin/env python

import rvo2
import matplotlib.pyplot as plt
import math
import threading
import random
import pygame
import time 
class Py_RVO():

    def __init__(self,radius, num_agents) -> None:
        self.sim = rvo2.PyRVOSimulator(1/60., 1.5, 5, 1.5, 1, 0.4, 2)
        self.goals = []
        self.flag = 0
        self.radius = radius
        self.num_agents = num_agents
        self.new_agents_x = []
        self.new_agents_y = []
        self.colors = []
        self.update = False
        self.agents = []
        self.createAgents(r=self.radius,num=num_agents)
        self.obstacle_vertices = [[(4.0,3.0),(4.0,4.0),(3.0,4.0),(3.0,3.0)],[(-3.0,3.0),(-3.0,4.0),(-4.0,4.0),(-4.0,3.0)],[(-3.0,-4.0),(-3.0,-3.0),(-4.0,-3.0),(-4.0,-4.0)],[(4.0,-4.0),(4.0,-3.0),(3.0,-3.0),(3.0,-4.0)] ]
        for i in self.obstacle_vertices:
            # self.obstacle_vertices = [(0.0,0.0),(0.0,2.0),(-2.0,2.0),(-2.0,0.0)] 
            self.createObstacle(i)
    


# Pass either just the position (the other parameters then use
# the default values passed to the PyRVOSimulator constructor),
# or pass all available parameters.
    def createAgent(self,pos,goal):
        a0 = self.sim.addAgent(pos)
        self.agents.extend([a0])
        self.goals.extend([goal])
        self.colors.extend(['black'])
        self.update = True

    def addGoals(self,r,num):
        pi = math.pi
        for p in range(0,num):
            x = math.cos((2*pi/num*p) - pi)*r
            y = math.sin((2*pi/num*p) - pi)*r
            self.goals.extend([(x,y)])

    def createAgents(self,r,num):
        pi = math.pi
        rand = random.randint(0,num)
        for p in range(0,num):
            x = math.cos(2*pi/num*p)*r
            y = math.sin(2*pi/num*p)*r            # x = random.uniform(-r,r)
            # y = random.uniform(-r,r)
            if p == rand:
                x += 0.1
                y += 0.2
            self.new_agents_x.extend([x])
            self.new_agents_y.extend([y])
            self.agents.extend([self.sim.addAgent((x,y))])
            self.colors.extend(['black'])
        
        self.addGoals(r=r,num=num)
        self.new_agents_x = []
        self.new_agents_y = []
        


    def createObstacle(self,pos):
        # Obstacles are also supported.
        o1 = self.sim.addObstacle(pos)
        self.sim.processObstacles()

    def setPrefVelocity(self):
        for agent,goal in zip(self.agents,self.goals):
            pos = self.sim.getAgentPosition(agent)
            vel = ((goal[0]-pos[0])*2 ,(goal[1]-pos[1])*2)
            if abs(vel[0]) <= 0.2 and abs(vel[1]) <= 0.2 :
                vel = (0,0)
            elif abs(vel[0]) < 1 and abs(vel[1]) < 1 :
                vel = (vel[0]*2,vel[1]*2)
            self.sim.setAgentPrefVelocity(agent,vel)
        

    def reachedGoal(self):
        count = 1
        reached = self.num_agents
        for agent,goal in zip(self.agents,self.goals):
            pos = self.sim.getAgentPosition(agent)
            if abs(pos[0]-goal[0]) > 0.1 or abs(pos[1]-goal[1]) > 0.1:
                count = 0
                reached -= 1
        return (count,reached)
    
    def draw_text(self,text,screen):
            text_font = pygame.font.SysFont(None,30)
            img = text_font.render(text,True,(255,255,255))
            screen.blit(img,(1100,100))
    
    def run(self):
        print('Simulation has %i agents and %i obstacle vertices in it.' %
            (self.sim.getNumAgents(), self.sim.getNumObstacleVertices()))
        pygame.init()
        SCREEN_WIDTH = 1400
        SCREEN_HEIGHT = 1000
        ZOOM_FACTOR = 1.1
        # zoom_level = 1.0
        if self.num_agents<= 50:
            zoom_level = 20.0
            radius = 5.0
        elif self.num_agents <= 100:
            zoom_level = 4.0
            radius = 2.0
        elif self.num_agents <= 200:
            zoom_level = 2.0
            radius = 1.5

        else:
            zoom_level = 1.0
            radius = 1.0

        path_print_flag = 0
        screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        run = True

        cmap = plt.get_cmap('hsv')
        followed_path = []
        while self.flag < 1:
            screen.fill((0,0,0))

            self.sim.doStep()
            self.setPrefVelocity()
            positions = [self.sim.getAgentPosition(agent_no)
                        for agent_no in self.agents]
#               print('step=%2i  t=%.3f  %s' % (step, sim.getGlobalTime(), '  '.join(positions)))

            x_vals = []
            y_vals = []
            n = len(positions)
            scaling_factor =  1  * zoom_level #int(1000/n)
            # radius = 1.0 #min(2.0,1.0*scaling_factor)
            for pose,x in zip(positions,range(n)):
                i = cmap(x)
                color = (math.floor(i[0]*255),math.floor(i[1]*255),math.floor(i[2]*255))
                pos_x = (pose[0]* scaling_factor) + SCREEN_WIDTH/2
                pos_y = (pose[1] * scaling_factor) + SCREEN_HEIGHT/2
                pygame.draw.circle(screen,color,center=(pos_x,pos_y),radius=radius)
                x_vals.extend([pose[0]])
                y_vals.extend([pose[1]])
               
                if self.num_agents <=50 and path_print_flag % 10 == 0:
                    path_print_flag = 0
                    element = [pos_x,pos_y,color]
                    followed_path.extend([element])
                


            path_print_flag +=1
            for point in followed_path:
                pygame.draw.circle(screen,point[2],center=(point[0],point[1]),radius=1.0)

            for points in self.obstacle_vertices:
                left_top = points[2]
                right_bottom = points[0]
                left_bottom = points[3]
                player = pygame.Rect((SCREEN_WIDTH/2 + (left_bottom[0] * zoom_level)),(SCREEN_HEIGHT/2 + (left_bottom[1] * zoom_level)),(abs(left_top[0]-right_bottom[0])* zoom_level),(abs(left_top[1]-right_bottom[1])*zoom_level))
                pygame.draw.rect(screen,(255,255,255),player)

            # for x,y in self.obstacle_vertices:
                # pygame.draw.line(screen,(255,255,255),(SCREEN_WIDTH/2 - 40,SCREEN_HEIGHT/2),(SCREEN_WIDTH/2 + 40,SCREEN_HEIGHT/2),4)
            # player = pygame.Rect((SCREEN_WIDTH/2 + (left_top[0] * zoom_level)),(SCREEN_HEIGHT/2),(abs(left_top[0]-right_bottom[0])* zoom_level),(abs(left_top[1]-right_bottom[1])*zoom_level))
            # pygame.draw.rect(screen,(255,255,255),player)

                

            time.sleep(0.01)
            # print(x_vals)
            # print("----------------------")
            # print(y_vals)
            # print("----------------------")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.flag = 1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:  # Zoom in
                        zoom_level *= ZOOM_FACTOR
                        # screen = pygame.display.set_mode((int(WIDTH * zoom_level), int(HEIGHT * zoom_level)))
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:  # Zoom out
                        zoom_level /= ZOOM_FACTOR
                        # screen = pygame.display.set_mode((int(WIDTH * zoom_level), int(HEIGHT * zoom_level)))
            # # sc.set_offsets(x_vals,y_vals)
            # plt.pause(0.1)
            # plt.clf()  # Clear plot for the next frame
            # # plt.figure(figsize=(self.radius+2,self.radius+2))
            # plt.xlim((-(self.radius+2),self.radius+2))
            # plt.ylim((-(self.radius+2),self.radius+2))
            if self.update:
                self.update = False
                continue
            # plt.scatter(x_vals, y_vals,c=self.colors)

            # plt.show(block=False)

            val = self.reachedGoal()
            self.flag = val[0]
            text = f"Reached Goal: {val[1]} / {self.num_agents}"
            self.draw_text(text=text,screen=screen)
            pygame.display.update()
        pygame.quit()
        print("All Agents reached their goal successfully")

# def main():
    # agents = int(input("Number Of Agents: "))
    # radius = float(input("Enter radius of circle such that it can easily accomodate the agents: "))
    # obj = Py_RVO(radius=radius,num_agents=agents)
    # obj.run()

class Addition():
    def __init__(self,py_rvo):
        self.sim = py_rvo
        pass
    
    def run(self):
        # ask_obstacle = int(input("Want to add obstacles ?"))
        # if ask_obstacle:
        #     loc = tuple(map(float, input("Enter X and Y position of Obstacle: ").strip().split()))
        #     self.sim.createObstacle(loc)
        ask_agent = int(input("Do you want to add agents? "))
        if ask_agent:
            number = int(input("How many agents: "))
            for i in range(number):
                pos =tuple(map(float, input("Position of Agent: ").strip().split()))
                goal = tuple(map(float, input("Goal of Agent: ").strip().split()))
                self.sim.createAgent(pos,goal)

def main():
    agents = int(input("Number Of Agents: "))
    radius = float(input("Enter radius of circle such that it can easily accomodate the agents: "))
    # obstacles = int(input("Number Of Obstacles: "))
    py_rvo = Py_RVO(radius=radius,num_agents=agents)
    # obstacle = Addition(py_rvo)

    # thread_1 = threading.Thread(target=py_rvo.run)
    # thread_2 = threading.Thread(target=obstacle.run)

    # thread_1.start()
    # thread_2.start()

    # thread_1.join()
    py_rvo.run()

if __name__ == "__main__":
    main()


