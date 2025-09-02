from random import randint

from greedy import Greedy

# Truck Loading Test
truck_capacity = 10000
packages = [randint(15,50) for _ in range(5000)]
trucks_necessary = Greedy(packages, truck_capacity)
print(trucks_necessary.value)

# Max Distance Between Points Test
product_range = 250
houses_on_road = [randint(0,10000) for _ in range(500)]
product_necessary = Greedy(houses_on_road, product_range, 1)
print(product_necessary.value, product_necessary.placements)
