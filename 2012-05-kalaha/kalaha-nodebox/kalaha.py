from nodebox.graphics import *
import math

canvas_size = (640, 480)

class Player(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.row = kwargs["row"]
        self.playing = kwargs["playing"]
        if kwargs.has_key("opponent"):
            self.opponent = kwargs["opponent"]
        else: 
            kwargs["opponent"] = self
            kwargs["row"] = self.row+1
            kwargs["playing"] = False
            self.opponent = Player(**kwargs)
        self.clr = Color(random(), random(), random())
        if self.row == 1:
            self.flip()
            self.x = int(kwargs["pit_size"]*1.5*(kwargs["num_houses"]-1))
            self.y = 2 * kwargs["pit_size"]
        self.width = int(canvas.width - kwargs["pit_size"]*(kwargs["num_houses"] * 1.5 - 0.5))
        self.height = int(canvas.height - kwargs["pit_size"]*3)
        self.x += int(self.width / 2)
        self.y +=  int(self.height / 2)
        self.kalaha = Kalaha(player = self, **kwargs)
        self.houses = [House(position = i, 
                             player = self, 
                             **kwargs) for i in range(kwargs["num_houses"])]
        self.append(self.kalaha)
        for house in self.houses:
            self.append(house)
    def change_turn(self, playing):
        self.playing = playing
        for house in self.houses:
            house.render_shape()
    def seeds(self):
        return reduce(lambda x, y: x + y.seeds, self.houses, [])
    def clicked_house(self):
        for house in self.houses:
            if house.pressed:
                return house
        return False

class Pit(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.seeds = []
        self.player = kwargs["player"]
        self.seeds_text = -1
        self.size = kwargs["pit_size"]
        self.width, self.height = self.size, self.size
        if self.player.row == 1:
            self.flip()
    def add(self, seeds):
        self.seeds += seeds
        grid = self.grid()
        for seed in self.seeds:
            seed.pit = self
            coords = grid.next()
            x = self.player.x + self.x 
            if self.player.row == 1:
                x = canvas.width - self.player.width - self.x + self.size*1.25
            seed.coordinates(x = coords[0] + x, 
                             y = coords[1] + self.y + self.player.y)
    def next(self):
        if self == self.player.kalaha:
            return self.player.opponent.houses[0]
        next = self.position + 1
        if next == len(self.player.houses):
            if self.player.playing:
                return self.player.kalaha
            return self.opposite()
        return self.player.houses[next]

class Kalaha(Pit):
    def __init__(self, *args, **kwargs):
        Pit.__init__(self, *args, **kwargs)
        self.x = int(kwargs["num_houses"] * self.size * 1.5)
        self.height = self.size*3
        self.name = "Kalaha P%s" % self.player.row
        if self.player.row == 1:
            self.y -= self.size * 2
        self.shape = buffered_ellipse(self.size, self.size*3, self.player.clr)
    def capture(self, house):
        self.add(house.opposite().empty() + house.empty())
    def grid(self):
        return grid(3, len(self.player.houses)*2, self.size/4, self.size/4, True)
    def draw(self):
        image(self.shape)

class House(Pit):
    def __init__(self, *args, **kwargs):
        Pit.__init__(self, *args, **kwargs)
        self.position = kwargs["position"]
        self.x = int(self.position * self.size * 1.5)
        self.name = "House P%s-%s" % (self.player.row, self.position)
        for i in range (kwargs["init_seeds"]):
            seed = Seed(pit = self, **kwargs)
            self.add([seed])
        self.render_shape()
    def empty(self):
        s = self.seeds
        self.seeds = []
        return s
    def opposite(self):
        return self.player.opponent.houses[len(self.parent.houses) - 1 - self.position]
    def neighbours(self, n = 0):
        neighbours = [self.next()]
        for seed in range(n-1):
            neighbours.append(neighbours[-1].next())
        return neighbours
    def grid(self):
        cols = int(math.ceil(math.sqrt(len(self.seeds))))
        return grid(cols, cols, self.size/4, self.size/4, True)
    def render_shape(self):
        line = 3 if self.player.playing else 1
        self.shape = buffered_ellipse(self.size, self.size, self.player.clr, line)
    def draw(self):
        image(self.shape)

class Seed(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.pit = kwargs["pit"]
        self.clr = Color(random(0.6, 0.8, 0.8))
        self.size = kwargs["seed_size"]
        self.width = self.size
        self.height = self.size
        self.name = "Seed P%s-%s-%s" % (self.pit.player.row, self.pit.position, len(self.pit.seeds))
        self.shape = buffered_ellipse(self.size, self.size, self.clr, 1, self.clr)
        board = kwargs["board"]
        board.append(self)
    def coordinates(self, x, y):
        self.origin(-self.pit.size/4, -self.pit.size/4)
        self.x, self.y = x , y
    def draw(self):
        image(self.shape)

class Board(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.num_houses = 6
        self.init_seeds = 3
        self.pit_size = int(canvas.width/(self.num_houses*1.5 + 4))
        self.seed_size = int(self.pit_size/5)
        self.turn = Player(row = 0, 
                           playing = True,
                           pit_size = self.pit_size,
                           num_houses = self.num_houses,
                           init_seeds = self.init_seeds,
                           seed_size = self.seed_size,
                           board = self)
        self.players = [self.turn, self.turn.opponent]
        for player in self.players:
            self.append(player)
    def sow(self, house):
        seeds = house.empty()
        for pit in house.neighbours(len(seeds)):
            seed = seeds.pop()
            pit.add([seed])
        if (len(pit.seeds) == 1 and pit != self.turn.kalaha and
                pit.player == self.turn and len(pit.opposite().seeds) > 0):
            self.turn.kalaha.capture(pit)
        if pit != self.turn.kalaha:
            self.change_player()
    def change_player(self):
        self.turn = self.turn.opponent
        self.turn.change_turn(True)
        self.turn.opponent.change_turn(False)
    def game_over(self, player):
        player.opponent.kalaha.add(reduce(
            lambda s, h: s + h.empty(), player.opponent.houses, []))
    def update(self):
        canvas.clear()
        if canvas.mouse.pressed:
            house = self.turn.clicked_house()
            if house != False and len(house.seeds) > 0:
                self.sow(house)
            for player in self.players:
                if len(player.seeds()) == 0:
                    self.game_over(player)

def buffered_ellipse(width, height, line = Color(1), strength = 1, clr = False):
    buffer = OffscreenBuffer(width+strength*2, height+strength*2)
    buffer.push()
    if clr != False:
        fill(clr)
    else: 
        nofill()
    stroke(line)
    strokewidth(strength)
    ellipse(width/2+strength, height/2+strength, width, height)
    buffer.pop()
    return buffer.texture

if __name__ == "__main__":
    canvas.fps = 16
    canvas.size = canvas_size
    canvas.append(Board()) 
    canvas.run()
