from nodebox.graphics import *

players = ["Anna", "Bob"]
pit_size = 50
pits = 6
seeds = 3

class Player(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.name = kwargs["name"]
        self.row = kwargs["row"]
        self.kalaha = Kalaha(player = self)
        self.houses = [House(position = i, player = self) for i in range(pits)]
        self.y = 100*self.row
        self.playing = False
        self.clr = Color(random(), random(), random())
        if self.row == 1:
            self.flip()
            self.x = pit_size*1.5*(pits-1)
        self.append(self.kalaha)
        for house in self.houses:
            self.append(house)
    def seeds(self):
        seeds = 0
        for house in self.houses:
            seeds += house.seeds
        return seeds
    def clicked_house(self):
        for house in self.houses:
            if house.clicked():
                return house
        return False
    def draw(self):
        pass

class Pit(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.seeds = 0
        self.player = kwargs["player"]
        if self.player.row == 1:
            self.flip()
    def add(self):
        self.seeds += 1
    def next(self):
        if self == self.player.kalaha:
            return self.player.opponent.houses[0]
        next = self.position + 1
        if next == pits:
            if self.player.playing:
                return self.player.kalaha
            return self.opposite()
        return self.player.houses[next]

class Kalaha(Pit):
    def __init__(self, *args, **kwargs):
        Pit.__init__(self, *args, **kwargs)
        self.x = 1.5 * pits * pit_size
        self.kalaha_text = -1
    def capture(self, seeds):
        self.seeds += seeds
    def draw(self):
        if self.seeds != self.kalaha_text:
            self.kalaha_text = self.seeds
            self.text = Text(str(self.seeds), x = 0 , y = 0)
            self.text.fill = Color(0,0,0)
        return self.text.draw()

class House(Pit):
    def __init__(self, *args, **kwargs):
        Pit.__init__(self, *args, **kwargs)
        self.seeds = seeds
        self.size = pit_size
        self.position = kwargs["position"]
        self.x = int(self.position * self.size * 1.5)
        self.width, self.height = self.size,self.size
        self.enabled = True
        self.seeds_text = 0
    def empty(self):
        s = self.seeds
        self.seeds = 0
        return s
    def opposite(self):
        return self.player.opponent.houses[pits - self.position - 1]
    def neighbours(self):
        if self.seeds == 0:
            return []
        neighbours = [self.next()]
        for seed in range(self.seeds-1):
            neighbours.append(neighbours[-1].next())
        return neighbours
    def clicked(self):
        return self.pressed
    def draw_seeds(self):
        if self.seeds != self.seeds_text:
            self.seeds_text = self.seeds
            self.text = Text(str(self.seeds), x = self.size/2 - 6 , y = self.size/2 - 6)
            self.text.fill = Color(0,0,0)
        return self.text.draw()
    def draw(self):
        nofill()
        stroke(self.player.clr)
        if self.player.playing:
            strokewidth(3)
        else:
            strokewidth(1)
        ellipse(self.size/2, self.size/2, self.size, self.size)
        self.draw_seeds()

class Board(Layer):
    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.players = [Player(name = kwargs["players"][i], row = i) for i in [0,1]]
        self.players[0].opponent = self.players[1]
        self.players[1].opponent = self.players[0]
        self.turn = self.players[0]
        self.turn.playing = True
        self.translate(150, 200)
        for player in self.players:
            self.append(player)
    def sow(self, house):
        pits = house.neighbours()
        seeds = house.empty()
        for pit in pits:
            pit.add()
        last = pits[-1]
        if (last.seeds == 1 and last != self.turn.kalaha and
                last.player == self.turn and last.opposite().seeds > 0):
            self.turn.kalaha.capture(last.opposite().empty() + last.empty())
        if last != self.turn.kalaha:
            self.change_player()
    def change_player(self):
        self.turn = self.turn.opponent
        self.turn.playing = True
        self.turn.opponent.playing = False
    def game_over(self, player):
        player.opponent.kalaha.capture(sum([h.empty() for h in player.opponent.houses]))
    def draw(self):
        canvas.clear()
        mouse = canvas.mouse
        if mouse.pressed:
            house = self.turn.clicked_house()
            if house != False and house.seeds > 0:
                self.sow(house)
            for player in self.players:
                if player.seeds() == 0:
                    self.game_over(player)

canvas.append(Board(0, 0, 640, 480, players = players)) 
canvas.run()
