"""
инициализировал муравья, чтобы пересечь карту
init_location - > отмечает, где на карте начинается муравей
possible_locations - > список возможных узлов, к которым может перейти муравей
при внутреннем использовании дает список возможных местоположений, которые муравей может пересечь для _minus тех узлов, которые уже посещены_
pheromone_map - > карта значений феромонов для каждого обхода между каждым узлом
distance_callback - > - это функция для вычисления расстояния между двумя узлами
Альфа - > параметр из алгоритма ACO для управления влиянием количества феромона при выборе в _pick_path()
beta - > a параметры из ACO, которые управляют влиянием расстояния до следующего узла в _pick_path()
first_pass -> если это первый проход на карте, то сделайте несколько шагов по-другому, как указано в приведенных ниже методах

маршрут - > список, который обновляется метками узлов, пройденных муравьем
pheromone_trail - > список количеств феромонов, отложенных вдоль тропы муравьев, сопоставленных с каждым пересечением маршрута
distance_traveled -> общее расстояние, пройденное по этапам маршрута
местоположение - > отмечает, где в данный момент находится муравей
tour_complete - > флаг, указывающий на то, что муравей завершил свой обход
используется get_route() и get_distance_traveled()
"""
from threading import Thread

class ant_colony:
	class ant(Thread):
		def __init__(self, init_location, possible_locations, pheromone_map, distance_callback, alpha, beta, first_pass=False):

			Thread.__init__(self)
			
			self.init_location = init_location
			self.possible_locations = possible_locations			
			self.route = []
			self.distance_traveled = 0.0
			self.location = init_location
			self.pheromone_map = pheromone_map
			self.distance_callback = distance_callback
			self.alpha = alpha
			self.beta = beta
			self.first_pass = first_pass
			
			#добавьте начальное местоположение к маршруту, прежде чем делать случайное блуждание
			self._update_route(init_location)
			
			self.tour_complete = False
			
		def run(self):
			"""
до самого себя.possible_locations пуст (муравей посетил все узлы)
_pick_path (), чтобы найти следующий узел для перехода к
_traverse() в:
_update_route() (чтобы показать последний обход)
_update_distance_traveled () (после обхода)
верните маршрут муравьев и его расстояние, для использования в ant_colony:
делайте обновления феромонов
проверьте наличие новых возможных оптимальных решений с помощью этого последнего тура муравьев
"""
			while self.possible_locations:
				next = self._pick_path()
				self._traverse(self.location, next)
				
			self.tour_complete = True
		
		def _pick_path(self):
			
			#на первом проходе (без феромонов), то мы можем просто выбрать (), чтобы найти следующий
			if self.first_pass:
				import random
				return random.choice(self.possible_locations)
			
			attractiveness = dict()
			sum_total = 0.0
			#для каждого возможного местоположения найдите его привлекательность (это (количество феромонов)*1 / расстояние [тау*эта, от алгоритма])
#суммируйте все суммы аттративности для расчета вероятности каждого маршрута на следующем шаге
			for possible_next_location in self.possible_locations:
		
				pheromone_amount = float(self.pheromone_map[self.location][possible_next_location])
				distance = float(self.distance_callback(self.location, possible_next_location))
				
				#tau^alpha * eta^beta
				attractiveness[possible_next_location] = pow(pheromone_amount, self.alpha)*pow(1/distance, self.beta)
				sum_total += attractiveness[possible_next_location]
			
			
			if sum_total == 0.0:
				#увеличьте все нули таким образом, чтобы они были наименьшими ненулевыми значениями, поддерживаемыми системой
				#взял здесь: http://stackoverflow.com/a/10426033/5343977
				def next_up(x):
					import math
					import struct
				
					if math.isnan(x) or (math.isinf(x) and x > 0):
						return x

					if x == 0.0:
						x = 0.0

					n = struct.unpack('<q', struct.pack('<d', x))[0]
					
					if n >= 0:
						n += 1
					else:
						n -= 1
					return struct.unpack('<d', struct.pack('<q', n))[0]
					
				for key in attractiveness:
					attractiveness[key] = next_up(attractiveness[key])
				sum_total = next_up(sum_total)
			
			#кумулятивное вероятностное поведение: http://stackoverflow.com/a/3679747/5343977
			#случайным образом выберите следующий путь
			import random
			toss = random.random()
					
			cummulative = 0
			for possible_next_location in attractiveness:
				weight = (attractiveness[possible_next_location] / sum_total)
				if toss <= weight + cummulative:
					return possible_next_location
				cummulative += weight
		
		def _traverse(self, start, end):
			"""
_update_route() для отображения нового обхода
_update_distance_traveled () для записи нового пройденного расстояния
сам.обновление местоположения в новое местоположение
называется от()
"""
			self._update_route(end)
			self._update_distance_traveled(start, end)
			self.location = end
		
		def _update_route(self, new):
		
			self.route.append(new)
			self.possible_locations.remove(new)
			
		def _update_distance_traveled(self, start, end):
			
			self.distance_traveled += float(self.distance_callback(start, end))
	
		def get_route(self):
			if self.tour_complete:
				return self.route
			return None
			
		def get_distance_traveled(self):
			if self.tour_complete:
				return self.distance_traveled
			return None
		
	def __init__(self, nodes, distance_callback, start=None, ant_count=50, alpha=.5, beta=1.2,  pheromone_evaporation_coefficient=.40, pheromone_constant=1000.0, iterations=80):
		
		
		if type(nodes) is not dict:
			raise TypeError("nodes must be dict")
		
		if len(nodes) < 1:
			raise ValueError("there must be at least one node in dict nodes")

		self.id_to_key, self.nodes = self._init_nodes(nodes)
		
		self.distance_matrix = self._init_matrix(len(nodes))
		
		self.pheromone_map = self._init_matrix(len(nodes))

		self.ant_updated_pheromone_map = self._init_matrix(len(nodes))
		
		#
		if not callable(distance_callback):
			raise TypeError("distance_callback is not callable, should be method")
			
		self.distance_callback = distance_callback
		
		#start
		if start is None:
			self.start = 0
		else:
			self.start = None
			
			for key, value in self.id_to_key.items():
				if value == start:
					self.start = key
			
			
			if self.start is None:
				raise KeyError("Key: " + str(start) + " not found in the nodes dict passed.")
		
		#ant_count
		if type(ant_count) is not int:
			raise TypeError("ant_count must be int")
			
		if ant_count < 1:
			raise ValueError("ant_count must be >= 1")
		
		self.ant_count = ant_count
		
		#alpha	
		if (type(alpha) is not int) and type(alpha) is not float:
			raise TypeError("alpha must be int or float")
		
		if alpha < 0:
			raise ValueError("alpha must be >= 0")
		
		self.alpha = float(alpha)
		
		#beta
		if (type(beta) is not int) and type(beta) is not float:
			raise TypeError("beta must be int or float")
			
		if beta < 1:
			raise ValueError("beta must be >= 1")
			
		self.beta = float(beta)
		
		#pheromone_evaporation_coefficient
		if (type(pheromone_evaporation_coefficient) is not int) and type(pheromone_evaporation_coefficient) is not float:
			raise TypeError("pheromone_evaporation_coefficient must be int or float")
		
		self.pheromone_evaporation_coefficient = float(pheromone_evaporation_coefficient)
		
		#pheromone_constant
		if (type(pheromone_constant) is not int) and type(pheromone_constant) is not float:
			raise TypeError("pheromone_constant must be int or float")
		
		self.pheromone_constant = float(pheromone_constant)
		
		#итерации
		if (type(iterations) is not int):
			raise TypeError("iterations must be int")
		
		if iterations < 0:
			raise ValueError("iterations must be >= 0")
			
		self.iterations = iterations
		
		#other internal variable init
		self.first_pass = True
		self.ants = self._init_ants(self.start)
		self.shortest_distance = None
		self.shortest_path_seen = None
		
	def _get_distance(self, start, end):
		
		if not self.distance_matrix[start][end]:
			distance = self.distance_callback(self.nodes[start], self.nodes[end])
			
			if (type(distance) is not int) and (type(distance) is not float):
				raise TypeError("distance_callback should return either int or float, saw: "+ str(type(distance)))
			
			self.distance_matrix[start][end] = float(distance)
			return distance
		return self.distance_matrix[start][end]
		
	def _init_nodes(self, nodes):
		
		id_to_key = dict()
		id_to_values = dict()
		
		id = 0
		for key in sorted(nodes.keys()):
			id_to_key[id] = key
			id_to_values[id] = nodes[key]
			id += 1
			
		return id_to_key, id_to_values
		
	def _init_matrix(self, size, value=0.0):
		"""
настройка матрицы NxN (где n = размер)
используется в обоих случаях.distance_matrix и self.pheromone_map
поскольку они требуют идентичных матриц, кроме того, какое значение инициализировать, чтобы
"""
		ret = []
		for row in range(size):
			ret.append([float(value) for x in range(size)])
		return ret
	
	def _init_ants(self, start):
		
		#выделите новых муравьев на первом проходе
		if self.first_pass:
			return [self.ant(start, self.nodes.keys(), self.pheromone_map, self._get_distance,
				self.alpha, self.beta, first_pass=True) for x in range(self.ant_count)]
		#в противном случае, просто сбросьте их, чтобы использовать на другом проходе
		for ant in self.ants:
			ant.__init__(start, self.nodes.keys(), self.pheromone_map, self._get_distance, self.alpha, self.beta)
	
	def _update_pheromone_map(self):
		
		#всегда квадратная матрица
		for start in range(len(self.pheromone_map)):
			for end in range(len(self.pheromone_map)):
				#decay the pheromone value at this location
				#tau_xy <- (1-rho)*tau_xy	(ACO)
				self.pheromone_map[start][end] = (1-self.pheromone_evaporation_coefficient)*self.pheromone_map[start][end]
				
				#tau_xy <- tau_xy + delta tau_xy_k
				#	delta tau_xy_k = Q / L_k
				self.pheromone_map[start][end] += self.ant_updated_pheromone_map[start][end]
	
	def _populate_ant_updated_pheromone_map(self, ant):
		#maim loop
		route = ant.get_route()
		for i in range(len(route)-1):
			
			current_pheromone_value = float(self.ant_updated_pheromone_map[route[i]][route[i+1]])
		
			#	delta tau_xy_k = Q / L_k
			new_pheromone_value = self.pheromone_constant/ant.get_distance_traveled()
			
			self.ant_updated_pheromone_map[route[i]][route[i+1]] = current_pheromone_value + new_pheromone_value
			self.ant_updated_pheromone_map[route[i+1]][route[i]] = current_pheromone_value + new_pheromone_value
		
	def mainloop(self):
		"""
Запускает рабочих муравьев, собирает их результаты и обновляет карту феромонов с помощью значений феромонов от рабочих
звонки:
_update_pheromones()
муравей.бежать()
запускает симуляцию самостоятельно.время итераций
"""
		
		for _ in range(self.iterations):
		
			for ant in self.ants:
				ant.start()
			
			
			for ant in self.ants:
				ant.join()
			
			for ant in self.ants:	
				
				self._populate_ant_updated_pheromone_map(ant)
				
				#если мы еще не видели никаких путей, то заселите их для сравнения позже
				if not self.shortest_distance:
					self.shortest_distance = ant.get_distance_traveled()
				
				if not self.shortest_path_seen:
					self.shortest_path_seen = ant.get_route()
					
				#если мы увидим более короткий путь, то сохраните его для возвращения
				if ant.get_distance_traveled() < self.shortest_distance:
					self.shortest_distance = ant.get_distance_traveled()
					self.shortest_path_seen = ant.get_route()
			
			
			self._update_pheromone_map()
			
		
			if self.first_pass:
				self.first_pass = False
			
		
			self._init_ants(self.start)
			
		
			self.ant_updated_pheromone_map = self._init_matrix(len(self.nodes), value=0)
		
		
		ret = []
		for id in self.shortest_path_seen:
			ret.append(self.id_to_key[id])
		
		return ret