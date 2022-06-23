import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter

import os

# 상자 안에 입자 2개가 자유롭게 떠다니는 프로젝트를 구현
particle_container = []
particles_x = []
particles_y = []
Temperature = 0

class simulation:
    def __init__(self,box_length = 10, collision_determiner=0.1, radius = 0.1, time_interval = 0.001):
        # 시뮬레이션 정보
        self.time = 0
        self.time_interval = 0.001
        self.end_iteration = 0
        self.num_of_particles = 0

        # 시뮬레이션 저장소
        self.simulation_saver = []

        # 충돌 계수
        self.sharp_b = 100

        # 시뮬레이션 입자 기본정보
        self.radius = 0.5
        self.box_length = box_length
        self.collision_determniner = collision_determiner
        self.mass = 1

        
        self.hi = [1,2,3]
    
    def generate_particles(self, _num_of_particles):
        self.num_of_particles = _num_of_particles
        total_energy = 0
        for i in range(0,self.num_of_particles):
            initial_parameter = [random.random(),random.random(),random.random()+2,random.random()+2]
            temp = particle(initial_parameter[0],initial_parameter[1],initial_parameter[2],initial_parameter[3],self.num_of_particles) # todo random처리할것
            total_energy += 0.5*math.sqrt(initial_parameter[2]**2 + initial_parameter[3]**2)
            """
            if i==0:
                temp = particle(0,1,0,-2,self.num_of_particles)
            if i==1:
                temp = particle(0,-1,0,2,self.num_of_particles)
            """
            particles_x.append(temp)
            particles_y.append(temp)
            particle_container.append(temp)
        # 총에너지 ,(m,k = 1)
        self.Temperature = total_energy/self.num_of_particles
        # 정렬
        self.sort_particle_location()
        # 시뮬레이션 부분 저장
        self.simulation_partial_save()

    def transmit_data(self, iter):
        return self.simulation_saver[iter][0], self.simulation_saver[iter][1], self.simulation_saver[iter][2], self.simulation_saver[iter][3]

    def simulation_partial_save(self):
        list_x = []
        list_y = []
        list_vx = []
        list_vy = []
        for i in range(0,self.num_of_particles):
            temp = particle_container[i]
            list_x.append(temp.x)
            list_y.append(temp.y)
            list_vx.append(temp.vx)
            list_vy.append(temp.vy)
        self.simulation_saver.append([list_x,list_y,list_vx,list_vy])

    def detect_wall_collision(self):
        # 벽에 충돌하는 입자 체크
        # x 좌표(왼쪽)
        num = self.num_of_particles
        for i in range(0,num):
            particle_temp = particles_x[i]
            # x좌표가 0미만
            if (particle_temp.x < 0) and ((particle_temp.x - self.radius) + self.box_length/2 < self.collision_determniner):
                if particle_temp.wall_x_collision == False:
                    particle_temp.generate_wall_collision_x()
            else:
                break

        # x 좌표(오른쪽)
        for i in range(-1,-num-1,-1):
            particle_temp = particles_x[i]
            # x좌표가 0초과
            if (particle_temp.x > 0) and (-(particle_temp.x + self.radius) + self.box_length/2 < self.collision_determniner):
                if particle_temp.wall_x_collision == False:
                    particle_temp.generate_wall_collision_x()
            else:
                break

        # y 좌표(아래)
        for i in range(0,num):
            particle_temp = particles_y[i]
            # y좌표가 0미만
            if (particle_temp.y < 0) and ((particle_temp.y - self.radius) + self.box_length/2 < self.collision_determniner):
                if particle_temp.wall_y_collision == False:
                    particle_temp.generate_wall_collision_y()
            else:
                break

        # y 좌표(위)
        for i in range(-1,-num-1,-1):
            particle_temp = particles_y[i]
            # y좌표가 0초과
            if (particle_temp.y > 0) and (-(particle_temp.y + self.radius) + self.box_length/2 < self.collision_determniner):
                if particle_temp.wall_y_collision == False:
                    particle_temp.generate_wall_collision_y()
            else:
                break
    
    def sort_particle_location(self):
        particles_x.sort(key=lambda s: s.x)
        particles_y.sort(key=lambda s: s.y)

        for index, temp_particle in enumerate (particles_x):
            temp_particle.order_x = index
        for index, temp_particle in enumerate (particles_y):
            temp_particle.order_y = index

    
    def start_simulation(self,end_time):
        """
        시뮬레이션이 이뤄지는 과정
        1. 먼저 새롭게 발생한 충돌을 수집하고 적용시킨다.(위치 맵을 통해서)
        2. 입자 위치를 업데이트한다.
        3. 맵에 입자의 새로운 위치를 업데이트 하고 정렬한다.
        4. 시뮬레이션 저장
        """
        self.end_iteration = int(end_time/self.time_interval)
        for i in range(1,self.end_iteration):
            if i%2000 == 0:
                os.system('cls')
                print("시뮬레이션 진행도 :",i*100/self.end_iteration)
            # 1. 새롭게 발생한 충돌 수집 및 적용
            # 벽에 충돌한거 detect
            self.detect_wall_collision()
            # 개별 입자 따라가면서 충돌상황 수집
            for temp_particle in particle_container:
                temp_particle.verify_collision()

            # 2-1. 개별 입자 가속도 계산
            for temp_particle in particle_container:
                temp_particle.acc()


            # 2. 개별 입자 클래스에서 업데이트
            for temp_particle in particle_container:
                temp_particle.update_location()
            
            # 3. 정렬
            self.sort_particle_location()

            # 4. 저장
            self.simulation_partial_save()

class particle(simulation):
    def __init__(self, init_x, init_y, init_vx, init_vy, num_of_particles):
        super().__init__()
        self.x = init_x
        self.y = init_y
        self.vx = init_vx
        self.vy = init_vy
        self.collision_list = []

        self.accx = 0
        self.accy = 0

        self.order_x = -1
        self.order_y = -1

        self.wall_x_collision = False
        self.wall_y_collision = False

        self.num_of_particles = num_of_particles
    
    def verify_collision(self):

        self.collision_list = []
        # 충돌 후보군 : 입자로부터 collision determiner 거리
        # 왼쪽으로 가까운거 찾음
        collision_candidate_x = []
        for i in range(self.order_x-1, -1, -1):
            temp_particle = particles_x[i]
            if self.x - temp_particle.x <= self.collision_determniner:
                collision_candidate_x.append(temp_particle)
            else:
                break
        # 오른쪽으로 가까운거
        for i in range(self.order_x+1, self.num_of_particles, 1):
            temp_particle = particles_x[i]
            if temp_particle.x - self.x <= self.collision_determniner:
                collision_candidate_x.append(temp_particle)
            else:
                break

        # 아래로 가까운거 찾음
        collision_candidate_y = []
        for i in range(self.order_y-1, -1, -1):
            temp_particle = particles_y[i]
            if self.y - temp_particle.y <= self.collision_determniner:
                collision_candidate_y.append(temp_particle)
            else:
                break
        # 위로 가까운거
        for i in range(self.order_y+1, self.num_of_particles, 1):
            temp_particle = particles_y[i]
            if temp_particle.y - self.y <= self.collision_determniner:
                collision_candidate_y.append(temp_particle)
            else:
                break

        collision_candidate = list(set(collision_candidate_x) & set(collision_candidate_y))
        # 이제부터 얘랑 충돌
        #print("얘랑 충돌 y값", self.y, "충돌후보 수 : ",len(collision_candidate), "x후보",len(collision_candidate_x), "order x", self.order_x)
        for temp_particle in collision_candidate:
            d = math.sqrt((self.x - temp_particle.x)**2 + (self.y - temp_particle.y)**2)
            try:
                sin = (self.y - temp_particle.y)/d
                cos = (self.x - temp_particle.x)/d
            except:
                sin=0
                cos = 0
            temp_list = [temp_particle, d, sin, cos]
            self.collision_list.append(temp_list)
    
    def generate_wall_collision_x(self):
        self.wall_x_collision = True

    def generate_wall_collision_y(self):    
        self.wall_y_collision = True
    
    def acc(self):
        self.accx = 0
        self.accy = 0
        for inner_list in self.collision_list:
            self.accx += inner_list[3]*50*math.exp(-3*inner_list[1])
            self.accy += inner_list[2]*50*math.exp(-3*inner_list[1])
    
        if self.wall_x_collision:
            self.accx += (-1 if self.x>0 else 1)*50*math.exp(-3*((self.box_length/2)-abs(self.x)))
        
        if self.wall_y_collision:
            self.accy += (-1 if self.y>0 else 1)*50*math.exp(-3*((self.box_length/2)-abs(self.y)))
    
    def update_location(self):
        self.x= self.x + self.vx*self.time_interval + 0.5*self.accx*self.time_interval*self.time_interval
        self.y= self.y + self.vy*self.time_interval + 0.5*self.accy*self.time_interval*self.time_interval
        self.vx = self.vx + self.accx*self.time_interval
        self.vy = self.vy + self.accy*self.time_interval
        
        # 벽 충돌판정 다시
        # x축
        if self.wall_x_collision == True and (self.box_length/2)-abs(self.x) > self.collision_determniner:
            self.wall_x_collision = False
        
        # y축
        if self.wall_y_collision == True and (self.box_length/2)-abs(self.y) > self.collision_determniner:
            self.wall_y_collision = False

        # 오류로 벽 나갈경우 -> 격리
        if self.x > self.box_length/2 + 5 or self.x < -self.box_length -5 or self.y > self.box_length/2 +5 or self.y < -self.box_length/2 -5:
            self.x = -100
            self.y = -100
            self.vx = 0
            self.vy = 0


aa= simulation(box_length=10)
aa.generate_particles(100)
aa.start_simulation(50)

fig, (ax1, ax2) = plt.subplots(1,2)
ax1.grid(True)
particles1, = ax1.plot([],[], 'bo')
ax1.set_xlim(-15, 15)
ax1.set_ylim(-15, 15)

# x 범위 0~10까지 0.2단위로 나눔
print("temperature : ", aa.Temperature)
bar_x = [i/5 for i in range(0,81,1)]
bar_y = [0 for i in range(0,81,1)]
barcollection = ax2.bar(bar_x,bar_y,width = 0.1)
ax2.set_xlim(-1, 4)
ax2.set_ylim(0, 0.5)

# 볼츠만 분포 그리기
k = 1
m = 1
def boltz(v):
    return (m*v/(k*aa.Temperature))*math.exp(-m*v*v/(2*k*aa.Temperature))*0.2
    
listx = [i/5 for i in range(0,41,1)]
listy = []
for i in range(0,41,1):
    listy.append(boltz(i/5))
ax2.plot(listx,listy)

rms = 0
def update(data):
    x_list, y_list, vx_list, vy_list = aa.transmit_data(data)
    particles1.set_data(x_list, y_list)

    # vx_list, vy_list 한번에 계산해서 묶음
    v_list = [math.sqrt(vx_list[itera]*vx_list[itera] + vy_list[itera]*vy_list[itera]) for itera in range(len(vx_list))]
    number = [0 for i in range(0,81,1)]
    rms=0
    for speed in v_list:
        rms += speed**2
        pivot = int(speed/0.5)
        number[pivot] += 1
    rms = math.sqrt(rms/aa.num_of_particles)
    print(rms)

    for p, b in enumerate(barcollection):
        b.set_height(number[p]/aa.num_of_particles)

    return particles1

f = []
for i in range(0,aa.end_iteration,100):
    f.append(i)
ani = animation.FuncAnimation(fig, update, frames=f, interval = 20)
ani.save("sim2.gif", dpi=300, writer=PillowWriter(fps=25))

plt.show()