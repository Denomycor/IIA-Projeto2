import copy
from jogos import *
from random import randint
from func_timeout import func_timeout, FunctionTimedOut

"""--------------------------------------------------------------------------------------
    Helpers
--------------------------------------------------------------------------------------"""

"""rotates a given matrix 90 degrees"""
def rotate90(board):
    return reverse(transpose(board))

""""Inverts a given list"""
def reverse(line):
    return line[::-1]

"""Transposes a given matrix"""
def transpose(matrix):
    return [ list(x) for x in zip(*matrix) ]

"""Removes zeros from a given array"""
def remove_zeros(line):
    return list(filter( lambda x: x != 0, line))

"""Pads a given array until a given length or 4 by default"""
def pad(array, leng=4, filler=" ", isStr=True):
    return (filler if isStr else [filler])*(leng-len(array)) + array

"""Sums a line with 2048 rules """
def sum_line(line):
    li = remove_zeros(line)

    points = 0
    for i in range(len(li)-2, -1, -1):
        if li[i] == li[i+1]:
            li[i+1] *= 2
            li[i] = 0
            points += li[i+1]
            i -= 1
    
    return (pad(remove_zeros(li), filler=0, isStr=False), points)

"""Sums the points of all the lines"""
def sum_points( m, toReverse, toTranspose):
    linesAndPoints = list(m)
    board = list( map( lambda x: reverse(x[0]), linesAndPoints) if toReverse else map( lambda x: x[0], linesAndPoints))
    if toTranspose:
        board = transpose(board)
    points = list( map( lambda x: x[1], linesAndPoints))
    points = sum(points)

    return (board, points)

"""Dictonaries that maps a 2048 action to a function that executes said action in a given board"""
actions = {
    "direita": lambda m: sum_points( map( lambda l: sum_line(l), m ), False, False),
    "esquerda": lambda m: sum_points( map( lambda l: sum_line(reverse(l)) , m ), True, False),
    "cima": lambda m: sum_points( map( lambda l: sum_line(reverse(l)) , transpose(m)), True, True),
    "baixo": lambda m: sum_points( map( lambda l: sum_line(l) , transpose(m)), False, True)
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
                print(pad(str(j), leng=5), end=" ")
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

    def __init__(self, positions):
        self.initial = Jogo2048State(to_move = "atacante", utility = 0, board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
        for pos in positions:
            self.initial.board[pos[0]][pos[1]]=2
        self.points = 0

    """Return a list of the allowable moves at this point."""
    def actions(self, state):
        return state.get_moves()

    """Return the state that results from making a move on a state."""
    def result(self, state, move):
        return state.next_move(move)

    """Returns the state that results from making several moves on a state"""
    def resultActions(self, state, moves):
        finalState = state
        for i in moves:
            finalState = self.result(finalState, i)
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

    """Makes a match between two players"""
    def jogar(self, jogador1, jogador2, verbose=True):
        return super().jogar(jogador1, jogador2, verbose)

    """Makes a match between two players, with a timeout"""
    def jogarTimeout(self, jogador1, jogador2, nsec=-1, verbose=True):
        estado = self.initial
        if verbose :
            self.display
        jogadores = (jogador1,jogador2)
        ind_proximo = 0
        
        while not self.terminal_test(estado):
            try:
                if nsec == -1:
                    ReturnedValue = jogadores[ind_proximo](self, estado)
                else:
                    ReturnedValue = func_timeout(nsec, jogadores[ind_proximo], args=(self, estado))
            except FunctionTimedOut:
                print("Timed Out!")
                ReturnedValue = None
            jogada = ReturnedValue
            if jogada == None:
                return 0 if estado.to_move == "atacante" else 100000
            else:
                estado = self.result(estado,jogada)
                if verbose:
                    self.display(estado)
                ind_proximo = 1 - ind_proximo

        return self.utility(estado, self.to_move(self.initial))


"""--------------------------------------------------------------------------------------
    Eval Parameters
--------------------------------------------------------------------------------------"""

"""The higher the average the more combined pieces are."""
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

"""The emptier the board the furthest the game is to ending."""
def boardEmpty(board):
    c = 0
    for i in board:
        for j in i:
            if j==0:
                c+=1
    return c/15.0

"""#The more pieces with equal value lined up with no other pieces between them the better the board."""
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

"""The better the disposition of the pieces on the board the better."""
def boardPos(board):

    """Calculates the score of this criteria for a board"""
    def calcWeight(board1, board2):
        acc = 0
        for i in range(4):
            for j in range(4):
                acc += board1[i][j] * board2[i][j]
        return acc

    """Places the pieces in optimal places on the board in order to maximize score"""
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

"""Returns the value to be used as evaluation in alphabeta algorithms"""
def score(s, weight):
    return boardAvg(s.board) * weight[0] + boardComb(s.board) * weight[1] + boardEmpty(s.board) * weight[2] + boardPos(s.board) * weight[3]

"""Decorates the evaluation function with a given set of weights"""
def decorator_func_48(deco):

    """Eval function"""
    def func_ataque_48(state, player):
        return score(state, deco)

    return func_ataque_48

"""Creates an eval function from a function that only takes the board as a parameter. For attackers"""
def decorator_eval_func_atk(deco):

    """Eval function"""
    def evalFunc(state, player):
        return deco(state.board)

    return evalFunc

"""Creates an eval function from a function that only takes the board as a parameter. For attackers"""

def decorator_eval_func_def(deco):

    """Eval function"""
    def evalFunc(state, player):
        return 0 - deco(state.board)

    return evalFunc

"""--------------------------------------------------------------------------------------
    Players
--------------------------------------------------------------------------------------"""

"""Represents a player"""
class Player:
    def __init__(self, name, alg):
        self.name = name
        self.alg = alg 

    def display(self):
        print(self.name)

idealAttackerWeight = (10.299999999999997, 27.0, 85.0, 74.5)
idealDefenderWeight = (99.1, 74.6, 37.0, 57.900000000000006)

func_ataque_48 = decorator_func_48(idealAttackerWeight)
func_defesa_48 = decorator_func_48(idealDefenderWeight)

def pick_random(game, state):
    act = game.actions(state)
    return act[random.randint(0, len(act)-1)]

atacante_ali = Player("AliD", pick_random)
defensor_ali = Player("DefD", pick_random)

"""Alphabeta Players"""
atacante = Player("atacante",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 5, eval_fn = func_ataque_48))

defensor = Player("defensor",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 5, eval_fn = func_defesa_48))

"""Input Player (manual player, for test purposes)"""
def readConsole(game, state):
    print("points: "+str(state.utility))
    print("Jogadas poss??veis: ", state.get_moves())
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

"""Generates a game with a random initial board"""
def randomGame():
    return Jogo2048_48({(randint(0,3), randint(0,3)), (randint(0,3), randint(0,3))})

"""Generates a random set of weights for the genetic algorithm"""
def generate():
    a = randint(0, 100)
    b = randint(0, 100)
    c = randint(0, 100)
    d = randint(0, 100)
    return (a,b,c,d)

"""Takes 2 sets of weights and merges them into one, taking randomly the weight from one parent or the other"""
def reproduce(t1, t2):
    t3 = [0,0,0,0]
    j = (t1, t2)
    for i in range(4):
        t3[i] = j[randint(0,1)][i]
    return tuple(t3)

"""Kills/Discards all entities of the genetic algorithm keeping only the #survivors better ones"""
def fitness( tuple, survivors ):
    tuple[0].sort(key=lambda x: x["score"], reverse=True)
    tuple[1].sort(key=lambda x: x["score"])
    return (tuple[0][0:survivors], tuple[1][0:survivors])

"""Takes an entity (set of weights) and the current generation, and has 50% chance to change each weight. The mutations are less radical has generations progress"""
def mutate(ent, g):

    conv = 35-g/2 if 35-g/2>0 else 0

    new = list(ent)
    for i in range(len(new)):
        if randint(0,10)>5:
            continue
        new[i] += [randint(0,15)+conv, 0-(randint(0,15)+conv)][randint(0,1)]
        new[i] %= 100
    return tuple(new)

"""Writes results to a txt file (one for attack players, one for defense players)"""
def writetxt(players, id):
    path = 'attack.txt' if id == 0 else 'defense.txt'
    with open(path, 'w') as file:
        for info in players:
            file.write('-----------------------------------------------\n')
            file.write('Player: '+info["player"].name+' |Score: '+ str(info["score"])+' |ADN: '+str(info["adn"])+'\n')


"""--------------------------------------------------------------------------------------
    Tournament
--------------------------------------------------------------------------------------"""

"""Runs a tournament between players """
def faz_campeonato(listAtk, listDef):
    for a in listAtk:
        for d in listDef:
            game = randomGame()
            score = game.jogar(a["player"].alg, d["player"].alg, False)
            print(a["player"].name + " vs " + d["player"].name + " score: " + str(score))
            a["score"] += score
            d["score"] += score

    return (listAtk, listDef)

"""Creates a new player with a given ADN and a prefix"""
def createPlayer(prefix, gen):
    return {
        "player": Player( prefix + str(gen), lambda game, state: alphabeta_cutoff_search_new(state, game, 2, eval_fn = decorator_func_48(gen))),
        "score": 0,
        "adn": gen
    }

"""Manually creates a player with the given name and ADN"""
def createOptPlayer(name, gen):
    return {
        "player": Player( name, lambda game, state: alphabeta_cutoff_search_new(state, game, 2, eval_fn = decorator_func_48(gen))),
        "score": 0,
        "adn": gen
    }

"""--------------------------------------------------------------------------------------
    TEST CODE
--------------------------------------------------------------------------------------"""
randomGame().jogarTimeout(atacante_ali.alg, defensor_ali.alg, 10, False)
randomGame().jogarTimeout(atacante_ali.alg, defensor_ali.alg, verbose=False)