from enum import Enum
import random, math

symbols = {
	"": "¤",
	"N": "╥",
	"W": "╞",
	"S": "╨",
	"E": "╡",
	"NE": "╚",
	"NW": "╝",
	"NS": "║",
	"WE": "═",
	"WS": "╗",
	"SE": "╔",
	"NWS": "╣",
	"NSE": "╠",
	"NWE": "╩",
	"WSE": "╦",
	"NWSE": "╬" 	
}

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

class Room():
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		self.start = False
		self.end = False
		self.available = True
		self.connections = []
		self.name = "{}-{}-{}".format(x, y, z)
		self.symbol = ""

	def is_available(self):
		return self.available

	def is_used(self):
		return not self.available

	def use(self):
		self.available = False

	def __str__(self):
		return "[{}, {}, {}]".format(self.x, self.y, self.z)

class Labyrinth():
	def __init__(self, width, height, depth, start, end):
		self.width = width
		self.height = height
		self.depth = depth
		self.rooms = [[[Room(x, y, z) for z in range(self.depth)] for y in range(self.height)] for x in range(self.width)]
		self.rooms[start[0]][start[1]][start[2]].start = True
		self.rooms[end[0]][end[1]][end[2]].end = True
		self.generate()
		self.nameify()
		self.yamlfy()
		self.htmlfy()

	def yaml(self, room):
		s = ""
		s += "synopsis: Another Room\n"
		s += "description: "
		s += "You've discovered dAnkan!\n" if room.end else \
				"You see the door you entered through.\n" if room.start else \
					"You have no idea where you are...\n"
		s += "exits:\n"
		for d in room.connections:
			s += "  {}: {}\n".format(d.lower(), self.get_room_in_direction(room, d).name)
		return s

	def coords_in_bounds(self, x, y, z):
		return x >= 0 and x < self.width and \
			y >= 0 and y < self.height and \
			z >= 0 and z < self.depth

	def room_at(self, x, y, z):
		return self.rooms[x][y][z]

	def connect(self, room1, room2):
		if room1.x != room2.x:
			if room1.x - room2.x < 0:
				room1.connections.append("EAST")
				room2.connections.append("WEST")
			else:
				room1.connections.append("WEST")
				room2.connections.append("EAST")
		elif room1.y != room2.y:
			if room1.y - room2.y < 0:
				room1.connections.append("SOUTH")
				room2.connections.append("NORTH")
			else:
				room1.connections.append("NORTH")
				room2.connections.append("SOUTH")
		elif room1.z != room2.z:
			if room1.z - room2.z < 0:
				room1.connections.append("DOWN")
				room2.connections.append("UP")
			else:
				room1.connections.append("UP")
				room2.connections.append("DOWN")

	def get_room_in_direction(self, room, direction):
		if direction == "EAST": return self.room_at(room.x+1, room.y, room.z)
		if direction == "WEST": return self.room_at(room.x-1, room.y, room.z)
		if direction == "NORTH": return self.room_at(room.x, room.y-1, room.z)
		if direction == "SOUTH": return self.room_at(room.x, room.y+1, room.z)
		if direction == "UP": return self.room_at(room.x, room.y, room.z-1)
		if direction == "DOWN": return self.room_at(room.x, room.y, room.z+1)

	def get_connection_rooms(self, room, connections):
		return [self.get_room_in_direction(room, d) for d in connections]


	def get_possible_neighbours_of(self, room):
		candidates = []
		if self.coords_in_bounds(room.x-1, room.y, room.z): candidates.append(self.room_at(room.x-1, room.y, room.z))
		if self.coords_in_bounds(room.x+1, room.y, room.z): candidates.append(self.room_at(room.x+1, room.y, room.z))
		if self.coords_in_bounds(room.x, room.y-1, room.z): candidates.append(self.room_at(room.x, room.y-1, room.z))
		if self.coords_in_bounds(room.x, room.y+1, room.z): candidates.append(self.room_at(room.x, room.y+1, room.z))
		if self.coords_in_bounds(room.x, room.y, room.z-1): candidates.append(self.room_at(room.x, room.y, room.z-1))
		if self.coords_in_bounds(room.x, room.y, room.z+1): candidates.append(self.room_at(room.x, room.y, room.z+1))
		return candidates

	def get_available_neighbours_of(self, room):
		return [r for r in self.get_possible_neighbours_of(room) if r.is_available()]

	def get_used_neighbours_of(self, room):
		return [r for r in self.get_possible_neighbours_of(room) if r.is_used()]

	def generate(self):
		frontier = set()
		current_room = self.rooms[0][0][0]
		current_room.use()
		frontier |= set(self.get_available_neighbours_of(current_room))

		while frontier != set():
			current_room = random.sample(frontier, 1)[0]
			current_room.use()
			frontier.remove(current_room)

			frontier |= set(self.get_available_neighbours_of(current_room))
			
			used_neighbours = self.get_used_neighbours_of(current_room)
			self.connect(current_room, random.choice(used_neighbours))

	def make_symbol_from_connections(self, connections):
		symbol = ""
		if "NORTH" in connections: symbol += "N"
		if "WEST" in connections: symbol += "W"
		if "SOUTH" in connections: symbol += "S"
		if "EAST" in connections: symbol += "E"
		return symbols[symbol]

	def nameify(self):
		for x in range(self.width):
			for y in range(self.height):
				for z in range(self.depth):
					current_room = self.rooms[x][y][z]
					if current_room.start:
						current_room.symbol = "S"
					elif current_room.end:
						current_room.symbol = "E"	
					else:
						current_room.symbol = self.make_symbol_from_connections(current_room.connections)

	def yamlfy(self):
		for x in range(self.width):
			for y in range(self.height):
				for z in range(self.depth):
					room = self.rooms[x][y][z]
					with open("yaml/" + room.name + ".yaml", "w+") as f:
						f.write(self.yaml(room))

	def htmlfy(self):
		s = "<html>\n"
		s += "\t<head>\n"
		s += "\t\t<meta charset=\"UTF-8\">\n"
		s += "\t\t<style>html{background-color: black; color: white;} font{font-family: \"Courier\";}</style>\n\t</head>\n"
		s += "\t<body>\n"

		for z in range(self.depth):
			for y in range(self.height):
				for x in range(self.width):
					r = self.rooms[x][y][z]
					if "UP" in r.connections and "DOWN" in r.connections:
						s += "<font color=\"green\">{}</font>".format(r.symbol)
					elif "UP" in r.connections:
						s += "<font color=\"yellow\">{}</font>".format(r.symbol)
					elif "DOWN" in r.connections:
						s += "<font color=\"blue\">{}</font>".format(r.symbol)
					else:
						s += "<font>{}</font>".format(r.symbol)
				s += "<br>\n\t\t"
			s += "--------<br>\n"

		s += "\t</body>"
		s += "</html>"

		with open("map.html", "w+") as f:
			f.write(s)

	def __str__(self):
		s = ""
		for z in range(self.depth):
			for y in range(self.height):
				for x in range(self.width):
					r = self.rooms[x][y][z]
					if "UP" in r.connections and "DOWN" in r.connections:
						s += "{}{}{}".format(bcolors.GREEN, r.symbol, bcolors.ENDC)
					elif "UP" in r.connections:
						s += "{}{}{}".format(bcolors.YELLOW, r.symbol, bcolors.ENDC)
					elif "DOWN" in r.connections:
						s += "{}{}{}".format(bcolors.BLUE, r.symbol, bcolors.ENDC)
					else:
						s += "{}".format(r.symbol)

					# s += "{}".format(self.rooms[x][y][z].symbol)
				s += "\n"
			s += "--------\n"
		return s

if __name__ == "__main__":
	width = 2
	height = 2
	depth = 2
	start = (0, 0, 0)
	end = (1, 1, 1)
	l = Labyrinth(width, height, depth, start, end)

	with open("yaml/settings.yaml", "w+") as f:
		s = "start: {}-{}-{}\nalso_load: []".format(start[0], start[1], start[2])
		f.write(s)
	print(l)
