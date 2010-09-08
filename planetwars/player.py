from planetwars.util import TypedSetBase

class Player(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Player %d: '%s'>" % (self.id, self.name)

    def __or__(self, other):
        if isinstance(other, Player):
            return Players((self, other))
        elif isinstance(other, Players):
            return other | self
        else:
            raise TypeError("Invalid operation for <Player> and %s" % type(other))

class Players(TypedSetBase):
    accepts = (Player, )

NOBODY = Player(0, "Nobody")
ME = PLAYER1 = Player(1, "Me")
PLAYER2 = Player(2, "Player 2")
PLAYER3 = Player(3, "Player 3")
PLAYER4 = Player(4, "Player 4")

ENEMIES = Players([PLAYER2, PLAYER3, PLAYER4])
NOT_ME = ENEMIES | NOBODY
EVERYBODY = NOT_ME | ME

PLAYER_MAP = {
    0: NOBODY,
    1: ME,
    2: PLAYER2,
    3: PLAYER3,
    4: PLAYER4,
}
