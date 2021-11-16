import copy
from jogos import *
from random import randint

"""--------------------------------------------------------------------------------------
    Helpers
--------------------------------------------------------------------------------------"""
ref = [0,0,0,0]

def rotate90(board):
    return reverse(transpose(board))

def alignLeft(str, chars):
    return (" "*(chars-len(str)))+str

def reverse(line):
    return line[::-1]

def transpose(matrix):
    return list(map(lambda x: list(x), zip(*matrix)))

def removeZeros(line):
    return list(filter( lambda x: x != 0, line))

def pad(line):
    return ref[:len(ref)-len(line):] + line

def sumLine(line):
    li = removeZeros(line)

    points = 0
    for i in range(len(li)-2, -1, -1):
        if li[i] == li[i+1]:
            li[i+1] *= 2
            li[i] = 0
            points += li[i+1]
            i -= 1
    
    return (pad(removeZeros(li)), points)

def sumPoints( m, toReverse, toTranspose):
    linesAndPoints = list(m)
    board = list( map( lambda x: reverse(x[0]), linesAndPoints) if toReverse else map( lambda x: x[0], linesAndPoints))
    if toTranspose:
        board = transpose(board)
    points = list( map( lambda x: x[1], linesAndPoints))
    points = sum(points)

    return (board, points)

actions = {
    "direita": lambda m: sumPoints( map( lambda l: sumLine(l), m ), False, False), 
    "esquerda": lambda m: sumPoints( map( lambda l: sumLine(reverse(l)) , m ), True, False),
    "cima": lambda m: sumPoints( map( lambda l: sumLine(reverse(l)) , transpose(m)), True, True),
    "baixo": lambda m: sumPoints( map( lambda l: sumLine(l) , transpose(m)), False, True)
}


"""--------------------------------------------------------------------------------------
    State Class
--------------------------------------------------------------------------------------"""
# GameState = namedtuple('GameState', 'to_move, utility, board, moves')
class Jogo2048State(GameState):
    
    """Returns a new state representing the board after the attacker player chooses a direction"""
    def __collapse(self, direction):
        try:
            output = actions[direction](self.board)
            newstate = Jogo2048State(to_move="defensor", utility = self.utility + output[1], board = output[0], moves=self.moves+1)
        except KeyError:
            raise RuntimeError("Error - invalid direction of movement" )

        return newstate
    
    """Returns a new state representing the board after a player action, doesn't check whether the action is valid or not"""
    def next_move(self, move):
        #TODO os novos estados criados precisam de ter o campo utility atualizado (nova pontuação)

        if self.to_move == "atacante":
            return self.__collapse(move)
        elif self.to_move == "defensor":
            newstate = Jogo2048State(to_move="atacante", utility = self.utility, board = copy.deepcopy(self.board), moves=self.moves+1)
            newstate.board[int(move[0])][int(move[2])] = 2
            return newstate
        else:
            raise RuntimeError("Error - invalid player descriptor")

    """Returns the other player, the one not playing this turn"""
    def other(self):
        if self.to_move == "atacante":
            return "defensor"
        if self.to_move == "defensor":
            return "atacante"
        else:
            raise RuntimeError("Error - invalid player descriptor")

    """Prints the board"""
    def display(self):
        print("="*28)
        for i in self.board:
            for j in i:
                print(alignLeft(str(j), 5), end=" ")
            print()
        print("="*28)

    """Returns all valid moves for the state"""
    def get_moves(self):
        if self.to_move == "atacante":
            return [ a for a in ["cima", "esquerda", "direita", "baixo"] if self.__collapse(a).board != self.board ]
        if self.to_move == "defensor":
            res = []
            for i in range(4):
                for j in range(4):
                    if self.board[i][j] == 0:
                        res.append(str(i)+","+str(j))
            return res
        else:
            raise RuntimeError("Error - invalid player descriptor")


"""--------------------------------------------------------------------------------------
    Game Class
--------------------------------------------------------------------------------------"""
class Jogo2048_48(Game):

    def __init__(self, pos1, pos2):
        self.initial = Jogo2048State(to_move = "atacante", utility = 0, board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
        self.initial.board[pos1[0]][pos1[1]]=2
        self.initial.board[pos2[0]][pos2[1]]=2
        self.points = 0

    """Return a list of the allowable moves at this point."""
    def actions(self, state):
        return state.get_moves()

    """Return the state that results from making a move from a state."""
    def result(self, state, move):
        return state.next_move(move)

    def resultActions(self, state, moves):
        finalState = None
        for i in moves:
            finalState = state.next_move(i)
        return finalState

    """utility is the score of the current board, equal to both players"""
    def utility(self, state, player):
        return state.utility 

    """Return True if this is a final state for the game."""
    def terminal_test(self, state):
        return not (state.to_move == "defensor" or bool(len(state.get_moves())))

    """Return the player whose move it is in this state."""
    def to_move(self, state):
        return state.to_move

    """Print or otherwise display the state."""
    def display(self, state):
        state.display()

    def jogar(self, jogador1, jogador2, verbose=True):
        #TODO
        return super().jogar(jogador1, jogador2, verbose)


"""--------------------------------------------------------------------------------------
    Eval Parameters
--------------------------------------------------------------------------------------"""
#The higher the avg the more combined pieces are.
def boardAvg(board):
    c = 0
    acc = 0
    max = 2
    for i in board:
        for j in i:
            if(j!=0):
                c+=1
                acc+=j
                if j>max:
                    max = j
    return acc/float(c)/max

#The emptier the board the furthest the game is to ending.
def boardEmpty(board):
    c = 0
    for i in board:
        for j in i:
            if j==0:
                c+=1
    return c/15.0

#The more pieces with equal value lined up with no other pieces between them the better the board.
def boardComb(board):
    pot=0
    for i in range(4):
        lastH = board[i][0]
        lastV = board[0][i]
        for j in range(1, 4, 1):
            if board[i][j] == lastH:
                pot+=1
            elif board[i][j]!=lastH and  board[i][j]!=0:
                lastH = board[i][j]
            if board[j][i] == lastV:
                pot+=1
            elif board[j][i]!=lastV and  board[j][i]!=0:
                lastV = board[j][i]
    return pot/24.0

#The better the disposition of the pieces on the board the better.
def boardPos(board):

    def calcWeight(board1, board2):
        acc = 0
        for i in range(4):
            for j in range(4):
                acc += board1[i][j] * board2[i][j]
        return acc

    def idealPos(board):
        flat = [item for row in board for item in row]
        flat.sort(reverse=True)

        result = []
        for i in range(4):
            result.append(flat[i*4:i*4+4])

        result[1] = reverse(result[1])
        result[3] = reverse(result[3])
        return result

    posWeight = [
        [16, 15, 14, 13],
        [ 9, 10, 11, 12],
        [ 8,  7,  6,  5],
        [ 1,  2,  3,  4]]
    base = calcWeight(idealPos(board), posWeight)

    curr = calcWeight(posWeight, board)

    return curr/base


def score(s, weight):
    return boardAvg(s.board) * weight[0] + boardComb(s.board) * weight[1] + boardEmpty(s.board) * weight[2] + boardPos(s.board) * weight[3]

def decorator_func_ataque_48(deco):

    def func_ataque_48(state, player):
        return score(state, deco)

    return func_ataque_48


def decorator_func_defesa_48(deco):
    
    def func_defesa_48(state, player):
        return score(state, deco)
    
    return func_defesa_48


"""--------------------------------------------------------------------------------------
    Players
--------------------------------------------------------------------------------------"""
class Player:
    def __init__(self, name, alg):
        self.name = name
        self.alg = alg 

    def display(self):
        print(self.name)



def score(s, weight):
    return boardAvg(s.board) * weight[0] + boardComb(s.board) * weight[1] + boardEmpty(s.board) * weight[2] + boardPos(s.board) * weight[3]

def decorator_func_ataque_48(deco):

    def func_ataque_48(state, player):
        return score(state, deco)

    return func_ataque_48

def decorator_func_defesa_48(deco):
    
    def func_defesa_48(state, player):
        return score(state, deco)
    
    return func_defesa_48


#func_ataque_48 = decorator_func_ataque_48(weight)
#func_defesa_48 = decorator_func_defesa_48(weight)


"""Alphabeta Players"""
atacante = Player("atacante",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = func_ataque_48))


defensor = Player("defensor",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = func_defesa_48))


"""Input Player"""
def readConsole(game, state):
    print("points: "+str(state.utility))
    print("Jogadas possíveis: ", state.get_moves())
    return input(state.to_move+", para onde quer jogar? ")

player = Player("input", readConsole)


"""Obsessive Players"""
def obsessivo_48(game, state):
    return state.get_moves()[0]

atacante_obsessivo = Player("obsessivoA", obsessivo_48)
defensor_obsessivo = Player("obsessivoD", obsessivo_48)


""""Hipolito Player"""
def hipolito_48(game, state):
    moves = state.get_moves()
    states = list(map(lambda m: state.next_move(m), moves))
    max = 0
    for i in range(0,len(states), 1):
        if state.to_move == "atacante":
            if states[i].utility > states[max].utility:
                max = i
        elif state.to_move == "defensor":
            if 0-states[i].utility > 0-states[max].utility:
                max = i
        else:
            raise RuntimeError("Invalid player")
    return moves[i]

atacante_hipolito = Player("hipolitoA", hipolito_48)
defensor_hipolito = Player("hipolitoD", hipolito_48)


"""--------------------------------------------------------------------------------------
    Genetic
--------------------------------------------------------------------------------------"""

def randomGame():
    return Jogo2048_48([randint(0,3), randint(0,3)], [randint(0,3), randint(0,3)])


def generate():
    a = randint(0, 100)
    b = randint(0, 100)
    c = randint(0, 100)
    d = randint(0, 100)
    return (a,b,c,d)

def reproduce(t1, t2):
    t3 = [0,0,0,0]
    j = (t1, t2)
    for i in range(4):
        t3[i] = j[randint(0,1)][i]
    return tuple(t3)

def fitness( tuple, survivors ):
    tuple[0].sort(key=lambda x: x["score"], reverse=True)
    tuple[1].sort(key=lambda x: x["score"])
    return (tuple[0][0:survivors], tuple[1][0:survivors])

def mutate(ent, g):

    conv = 20-g/2 if 20-g/2>0 else 1

    new = list(ent)
    for i in range(len(new)):
        if randint(0,10)>5:
            continue
        new[i] += [randint(0,30)+conv, 0-(randint(0,30)+conv)][randint(0,1)]
        new[i] %= 100
    return tuple(new)


def writetxt(players, id):
    path = 'attack.txt' if id == 0 else 'defense.txt'
    with open(path, 'w') as file:
        for info in players:
            file.write('-----------------------------------------------\n')
            file.write('Player: '+info["player"].name+' |Score: '+ str(info["score"])+' |ADN: '+str(info["adn"])+'\n')


"""--------------------------------------------------------------------------------------
    Games and Tournaments
--------------------------------------------------------------------------------------"""

def faz_campeonato(listAtk, listDef):
    for a in listAtk:
        for d in listDef:
            game = randomGame()
            score = game.jogar(a["player"].alg, d["player"].alg, False)
            print(a["player"].name + " vs " + d["player"].name + " score: " + str(score))
            a["score"] += score
            d["score"] += score

    return (listAtk, listDef)



def createPlayer(prefix, gen, player):
    
    func = decorator_func_ataque_48(gen) if player == "atacante" else decorator_func_defesa_48(gen) 
    res = {
        "player": Player( prefix + str(gen), lambda game, state: alphabeta_cutoff_search_new(state, game, 2, eval_fn = func)),
        "score": 0,
        "adn": gen
    }
    return res

def createOptPlayer(name, gen, player):
    func = decorator_func_ataque_48(gen) if player == "atacante" else decorator_func_defesa_48(gen) 
    res = {
        "player": Player( name, lambda game, state: alphabeta_cutoff_search_new(state, game, 2, eval_fn = func)),
        "score": 0,
        "adn": gen
    }
    return res

"""--------------------------------------------------------------------------------------
    TODO: REMOVE BEFORE DELIVERY THIS IS TEST CODE
--------------------------------------------------------------------------------------"""


listAtk = []#[atacante_hipolito, atacante_obsessivo]
listDef = []#[defensor_obsessivo, defensor_hipolito]



init_pop = 0
num_gen = 1000
num_reproduce = 1
num_survivors = 3

#createOptPlayer("Opt1AHipolito", (13, 47, 54, 57), "atacante")
#createOptPlayer("Opt2AHipolito", (18, 47, 54, 57), "atacante")

for i in range(init_pop):
    ga = generate()
    listAtk.append( createPlayer( "Atk-", ga, "atacante") )
    gd = generate()
    listDef.append( createPlayer( "Def-", gd, "defesa") )

listAtk.append(createOptPlayer("Opt1A", (27.1, 72.5, 70.5, 75.0), "atacante"))
listAtk.append(createOptPlayer("Opt2A", (99, 28, 78, 23), "atacante"))
listAtk.append(createOptPlayer("Opt3A", (87.0, 67.5, 45.5, 75.0), "atacante"))
listAtk.append(createOptPlayer("Opt4A", (18.299999999999997, 23.0, 58.0, 72.4), "atacante"))
listAtk.append(createOptPlayer("OptOptA", (10.299999999999997, 27.0, 85.0, 74.5), "atacante"))

listDef.append(createOptPlayer("Opt1D", (83.1, 23.6, 35.5, 24.9), "defesa"))
listDef.append(createOptPlayer("Opt2D", (24.799999999999997, 36.199999999999996, 87.5, 55.8), "defesa"))
listDef.append(createOptPlayer("Opt3D", (68.6, 68.5, 8, 80.3), "defesa"))
listDef.append(createOptPlayer("Opt4D", (54.3, 74.6, 52.9, 48.0), "defesa"))
listDef.append(createOptPlayer("OptOptD", (99.1, 74.6, 37.0, 57.900000000000006), "defesa"))


for g in range(num_gen):
    print("Generation: "+str(g))
    for j in range(len(listAtk)):
        listAtk[j]["score"] = 0
        listDef[j]["score"] = 0
    lists = faz_campeonato(listAtk, listDef)
    lists = fitness(lists, num_survivors)
    writetxt(listAtk, 0)
    writetxt(listDef, 1)
    listAtk = lists[0]
    listDef = lists[1]
    newAtk = []
    newDef = []
    for i in range(num_reproduce):
        ga = mutate( reproduce(listAtk[randint(0, len(listAtk)-1)]["adn"], listAtk[randint(0, len(listAtk)-1)]["adn"] ), g)
        newAtk.append( createPlayer( "Atk("+str(g)+")-", ga, "atacante") )
        gd = mutate( reproduce(listDef[randint(0, len(listDef)-1)]["adn"], listDef[randint(0, len(listDef)-1)]["adn"] ), g )
        newDef.append( createPlayer( "Def("+str(g)+")-", gd, "defesa") )
    listAtk.extend(newAtk)
    listDef.extend(newDef)
