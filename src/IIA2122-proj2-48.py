import copy
from jogos import *

"""--------------------------------------------------------------------------------------
    Helpers
--------------------------------------------------------------------------------------"""
ref = [0,0,0,0]

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
    "baixo": lambda m: sumPoints( map( lambda l: sumLine(l) , transpose(m)), False, True),
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
            newstate = Jogo2048State(to_move="atacante", utility= self.utility, board = copy.deepcopy(self.board), moves=self.moves+1)
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
            return [ a for a in ["cima", "direita", "baixo", "esquerda"] if self.__collapse(a).board != self.board ]
        if self.to_move == "defensor":
            res = []
            for i in range(3, -1, -1):
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
         #Board is a list of lists 4*4 which stores the board pieces
        self.initial = Jogo2048State(to_move = "atacante", utility = 0, board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
        self.initial.board[pos1[0]][pos1[1]]=2
        self.initial.board[pos2[0]][pos2[1]]=2
        self.points = 0

    def actions(self, state):
        return state.get_moves()

    def result(self, state, move):
        return state.next_move(move)

    def utility(self, state, player):
        #utility is the score on a current state, equal to both players
        return state.utility 

    def terminal_test(self, state):
        return not (state.to_move == "defensor" or bool(len(state.get_moves())))

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        state.display()

    def jogar(self, jogador1, jogador2, verbose=True):
        #TODO
        return super().jogar(jogador1, jogador2, verbose)



"""--------------------------------------------------------------------------------------
    Players
--------------------------------------------------------------------------------------"""
#Get the max value of the board
def max_val(board):
    max = 2
    for i in board:
        for j in i:
            if j>max:
                max = j
    return max

#The highter the avg the more combined pieces are. Ranges from 2 to max_piece_value
def boardAvg(board):
    c = 0
    acc = 0
    for i in board:
        for j in i:
            if(j!=0):
                c+=1
                acc+=j
    return acc/float(c)/max_val(board)

#The emptier the board the furthest the game is to ending. Ranges from 0 to 15
def boardEmpty(board):
    c = 0
    for i in board:
        for j in i:
            if j==0:
                c+=1
    return c/15.0

#The more pieces with equal value lined up with no other pieces between them the better the board. Ranges from 0 to 24
def boardComb(board):
    pot=0
    for i in range(4):
        last = board[i][0]
        for j in range(1, 4, 1):
            if board[i][j] == last:
                pot+=1
            elif board[i][j]!=last and  board[i][j]!=0:
                last = board[i][j]

    for i in range(4):
        last = board[0][i]
        for j in range(1, 4, 1):
            if board[j][i] == last:
                pot+=1
            elif board[j][i]!=last and  board[j][i]!=0:
                last = board[j][i]
    return pot/24.0
    

class Player:
    def __init__(self, name, alg):
        self.name = name
        self.alg = alg

    def display(self):
        print(self.name)

def eval_attacker(state, player):
    return

atacante = Player("atacante",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = eval_attacker))

def eval_defender(state, player):
    return

defensor = Player("defensor",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = eval_defender))




# Does hipolito algorithm uses alphabeta or not?

def eval_hipolito(state, player):
    moves = state.get_moves()
    states = list(map(lambda m: state.next_move(m), moves))
    max = 0
    for i in range(1,len(states), 1):
        if player == "atacante":
            if states[i].utility > states[max].utility:
                max = i
        elif player == "defensor":
            if 0-states[i].utility > 0-states[max].utility:
                max = i
        else:
            raise RuntimeError("Invalid player")
    return moves[i]

def hipolitoF(game, state):
    moves = state.get_moves()
    states = list(map(lambda m: state.next_move(m), moves))
    max = 0
    for i in range(1,len(states), 1):
        if game.to_move == "atacante":
            if states[i].utility > states[max].utility:
                max = i
        elif game.to_move == "defensor":
            if 0-states[i].utility > 0-states[max].utility:
                max = i
        else:
            raise RuntimeError("Invalid player")
    return moves[i]

hipolito = Player("hipolito",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = eval_hipolito))

hipolito2 = Player("hipolito2", hipolitoF)




""" TODO: REMOVE BEFORE DELIVERY THIS IS TEST CODE """
tmp = Jogo2048_48([3,2], [3,3])
tmp.display(tmp.initial)

state = tmp.result(tmp.initial, "direita")

tmp.display(state)
print("uti --> " + str(state.utility))

state = tmp.result(state, "0,0")

print(tmp.actions(state))

state2 = tmp.result(state, "direita")
tmp.display(state2)
print("uti --> " + str(state2.utility))