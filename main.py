import copy
import numpy as np
import random
import tqdm as tqdm
from random import randint


def calc_distance(loc1, loc2):
    __x1, __y1 = loc1
    __x2, __y2 = loc2
    return abs(__x1 - __x2) + abs(__y1 - __y2)


class Time:
    def __init__(self):
        self.time = [0]
        self.locations = [(0, 0)]
        self.location = self.locations[-1]
        self.ride = 0

    def increase_time(self, start, stop, ride):
        distance = calc_distance(start, stop)
        if distance > 1:
            self.time.extend(range(self.time[-1]+1, self.time[-1] + distance+1))
            for i in range(distance-1):
                self.locations.append((-1, -1))
            self.locations.append(stop)
            self.location = self.locations[-1]
            self.ride = self.ride + ride
        elif distance is 1:
            self.time.append(self.time[-1]+1)
            self.locations.append(stop)
            self.location = self.locations[-1]
            self.ride = self.ride + ride

    def pop_ride(self, ride):
        self.ride = self.ride - 1
        self.del_last_location()
        for x in reversed(self.locations):
            if x == (-1, -1):
                self.del_last_location()
            else: break
        if self.location is ride.start and self.time[-1] is not 0:
            self.del_last_location()
            for y in reversed(self.locations):
                if y == (-1, -1):
                    self.del_last_location()

    def decrease_ride(self, ride):
        if ride.stop == self.location:
            self.pop_ride(ride)
        else:
            return

    def del_last_location(self):
        self.locations = self.locations[:-1]
        self.location = self.locations[-1]
        self.time = self.time[:-1]

    def elapse(self, __t):
        for _ in range(__t):
            self.locations.append(self.location)
            self.time.append(self.time[-1]+1)

    def is_bonus(self, start, earliest):
        try:
            if self.locations[earliest] == start:
                return True
            else:
                return False
        except IndexError:
            return False

    def get_time(self):
        return self.time[-1]

    def __str__(self):
        return str(self.time[-1])


class Car:
    def __init__(self, __id):
        self.rides = []
        self.T = Time()
        self.location = (0, 0)
        self.fitness = -1
        self.id = __id

    def add_ride(self, ride):
        if self.can_make_it(ride):
            self.rides.append(ride)
            self.T.increase_time(self.location, ride.start, 0)
            self.T.increase_time(ride.start, ride.stop, 1)
            self.location = self.T.location
            ride.set_car(self)

    def add_bonus_ride(self, ride):
        if ride.car is None:
            if self.can_start_early(ride):
                self.rides.append(ride)
                self.T.increase_time(self.location, ride.start, 0)
                self.T.increase_time(ride.start, ride.stop, 1)
                self.location = self.T.location
                ride.set_car(self)

    def add_random_ride(self, ride):
        if ride.car is None:
            if self.can_make_it(ride):
                self.rides.append(ride)
                self.T.increase_time(self.location, ride.start, 0)
                self.T.elapse(ride.earliest - self.T.get_time())
                self.T.increase_time(ride.start, ride.stop, 1)
                self.location = self.T.location
                ride.set_car(self)
    def is_bonus_ride(self, ride):
        return self.T.is_bonus(ride.start, ride.earliest)

    def remove_ride(self, ride):
        for _id, _ride in enumerate(self.rides):
            if _ride.id == ride.id:
                del self.rides[_id]
                self.T.decrease_ride(ride)
                self.location = self.T.location
                break

    def can_make_it(self, ride):
        return self.T.get_time() + calc_distance(self.location, ride.start) + ride.distance() - ride.latest <= 0

    def can_start_early(self, ride):
        return self.T.get_time() + calc_distance(self.location, ride.start) - ride.earliest is 0

    def is_bonus(self, ride):
        return self.T.get_time() + calc_distance(self.location, ride.start) - ride.earliest <= 0

    def set_bonus_rides(self, __rides):
        __rides = sorted(__rides, key=lambda __ride: calc_distance(__ride.start, self.T.location))
        for ride in __rides:
            self.add_bonus_ride(ride)

    def set_random_rides(self, __rides):
        __rides = sorted(__rides, key=lambda __ride: calc_distance(__ride.start, self.T.location) - __ride.earliest)
        for _ in __rides[:int((len(__rides)/2))]:
            _ride = np.random.choice(__rides[:int(len(__rides)/2)])
            self.add_random_ride(_ride)
            break

    def __str__(self):
        _str = str(self.id) + ' rides:'
        for ride in self.rides:
            _str = _str +str(ride)
        return _str


class Cars:
    def __init__(self, cars_rides):
        self.cars_rides = cars_rides
        self.fitness = -1
        self.cars = [Car(i) for i in range(F)]

    def set_random(self):
        for __car in self.cars:
            __car.set_random_rides(self.cars_rides)

    def add_rides(self, rides):
        for ride in rides:
            self.unassign_ride(ride)
        for ride in rides:
            self.add_ride(ride)

    def add_ride(self, new_ride):
        if new_ride.car is not None:
            self.assign_ride(new_ride)

    def add_ride_to_random(self, new_ride):
        if new_ride.car is None:
            new_ride.car = random.choice(self.cars)
            self.unassign_ride(new_ride)
            self.add_ride(new_ride)
        else:
            self.add_ride(new_ride)

    def assign_ride(self, new_ride):
        _car = self.cars[new_ride.car.id]
        if _car.can_make_it(new_ride):
            _car.add_ride(self.cars_rides[new_ride.id])
            self.cars_rides[new_ride.id].car = _car

    def unassign_ride(self, new_ride):
        if new_ride.car is not None:
            for _id, _ride in enumerate(self.cars_rides):
                if _ride.id == new_ride.id:
                    if _ride.car is not None:
                        _car_rides = _ride.car.rides
                        for _idcr, _car_ride in enumerate(_car_rides):
                            if _ride.id == _car_ride.id:
                                _ride.car.remove_ride(_ride)
                                _ride.car = None
                                return
                    else:
                        return

    def __str__(self):
        __str = ''
        for car in self.cars:
            if car.rides is not None:
                rides_str = ''
                for ride in car.rides:
                        rides_str = rides_str + ' ' + str(ride.id)
                __str = __str + (str(len(rides_str.split())) + rides_str)
                __str = __str + '\n'
        __str = __str + ('Fitness: '+str(self.fitness))
        return __str


class Ride:
    def __init__(self, start, stop, earliest, latest, __id):
        self.start = start
        self.stop = stop
        self.earliest = earliest
        self.latest = latest
        self.car = None
        self.id = __id
        self.bonus = 0

    def set_car(self, __car):
        self.car = __car

    def distance(self):
        return calc_distance(self.start, self.stop)

    def increase_bonus(self):
        self.bonus = self.bonus + B

    def __str__(self):
        return str(self.id)


population = 8
generations = 10


def ga():
    __cars_pop = init_car_rides()
    for generation in tqdm.tqdm(range(generations)):
        __cars_pop = fitness(__cars_pop)
        __cars_pop = selection(__cars_pop)
        __cars_pop = crossover(__cars_pop)
        __cars_pop = mutation(__cars_pop)
        print('Generation: ' + str(generation))
        print('Nr cars:' + str(len(__cars_pop)))
        print(str(__cars_pop[0]))

    write_output(__cars_pop[0])


def fitness(__cars_pop):
    for __cars in __cars_pop:
        __cars.fitness = 0
        for __car in __cars.cars:
            for ride in __car.rides:
                __cars.fitness = __cars.fitness + ride.distance()
                if ride.car.is_bonus_ride(ride):
                    __cars.fitness = __cars.fitness + B
    return __cars_pop


def selection(__cars_pop):
    __cars_pop = sorted(__cars_pop, key=lambda __cars: __cars.fitness, reverse=True)

    _max = 0
    for __cars in __cars_pop:
        _max = max(_max, __cars.fitness)
    print('\nFittest:'+str(_max))

    __cars_pop = __cars_pop[:int(0.4*len(__cars_pop))]

    return __cars_pop

def crossover(__cars_pop):
    aux = []
    print('Crossover')
    for _ in tqdm.tqdm(range(int((population - len(__cars_pop)) / 4))):
        parent1 = random.choice(__cars_pop)
        parent2 = random.choice(__cars_pop)
        child1 = Cars(copy.deepcopy(initial_rides))
        child2 = Cars(copy.deepcopy(initial_rides))

        child1.add_rides(parent1.cars_rides)
        child1.add_rides(parent2.cars_rides)

#        child2.add_rides(parent2.cars_rides)
#        child2.add_rides(parent1.cars_rides)
        aux.append(child1)
#        aux.append(child2)
    __cars_pop.extend(aux)
    return __cars_pop


def mutation(__cars_pop):
    print('\nMutation')
    for __cars in __cars_pop:
        for __id, __ride in enumerate(__cars.cars_rides):
            if random.uniform(0.0, 1.0) <= 0.8 and __ride.car is None:
                __cars.add_ride_to_random(__ride)
    return __cars_pop


def init_car_rides():
    print('Initialize car rides')
    __cars_pop = [Cars(copy.deepcopy(initial_rides)) for _ in range(population)]
    for _id, x in tqdm.tqdm(enumerate(__cars_pop)):
        print(str(_id) + ' cars')
        x.set_random()
        print(str(x))
    return __cars_pop


def read_input(_file_name):
    _f = open(_file_name, 'r')
    _lines = _f.readlines()
    __rides = []
    __R, __C, __F, __N, __B, __T = [int(val) for val in _lines[0].split()]
    for _id in range(1, __N+1):
        a, b, x, y, s, f = _lines[_id].split()
        __ride = Ride((int(a), int(b)), (int(x), int(y)), int(s), int(f), _id-1)
        __rides.append(__ride)
    __rides = np.array(__rides)
    return __R, __C, __F, __N, __B, __T, __rides


def write_output(__cars):
    with open(file_name.split('.')[0].split('/')[1]+'.out', 'w') as f:
        f.write(str(__cars))
    _str = ''
    for ride in __cars.cars_rides:
        if ride.car is None:
            _str = _str + str(ride.id) + ' '
    print('Unassigned rides:' + _str)


if __name__ == '__main__':
    file_name = "Files/e_high_bonus.in"
    R, C, F, N, B, T, initial_rides = read_input(file_name)
    ga()

