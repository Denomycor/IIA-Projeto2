import copy
from jogos import *

#Helpers
ref = [0,0,0,0]

def alignLeft(str, chars):
    return (" "*(chars-len(str)))+str

def reverse(line):
    return line[::-1]

def transpose(matrix):
    return list(map(lambda x: list(x), zip(*matrix)))

def removeZeros(line):
    return list(filter( lambda x: x != 0, line))

def sumStep(line):
    if len(line) < 2:
        return False

    done = False
    for i in range(len(line)-2, -1, -1):
        if line[i] == line[i+1]:
            line[i+1] *= 2
            line[i] = 0
            i -= 1
            done = True
    return done

def pad(line):
    return ref[:len(ref)-len(line):] + line

def sumLine(line):
    li = removeZeros(line)

    while sumStep(li):
        li = removeZeros(li)
    return pad(li)

actions = {
    "direita": lambda m: list( map( lambda l: sumLine(l), m )), 
    "esquerda": lambda m: list( map( lambda l: reverse(sumLine(reverse(l))) , m )),
    "cima": lambda m: transpose( map( lambda l: reverse(sumLine(reverse(l))) , transpose(m) ) ),
    "baixo": lambda m: transpose( map( lambda l: sumLine(l) , transpose(m) ) ),
}

#Get the max value of the board
def max_val(board):
    max = 0
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
    

"""--------------------------------------------------------------------------------------
    State Class
--------------------------------------------------------------------------------------"""
# GameState = namedtuple('GameState', 'to_move, utility, board, moves')
class Jogo2048State(GameState):
    
    """Returns a new state representing the board after the attacker player chooses a direction"""
    def __collapse(self, direction):
        try:
            newstate = Jogo2048State(to_move="defensor", utility=0, board = actions[direction](self.board), moves=self.moves+1)
        except KeyError:
            raise RuntimeError("Error - invalid direction of movement" )

        return newstate
    
    """Returns a new state representing the board after a player action, doesn't check whether the action is valid or not"""
    def next_move(self, move):
        if self.to_move == "atacante":
            return self.__collapse(move)
        elif self.to_move == "defensor":
            newstate = Jogo2048State(to_move="atacante", utility=0, board = copy.deepcopy(self.board), moves=self.moves+1)
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
        self.initial = Jogo2048State(to_move = "atacante", utility = (16-2)/16.0, board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
        self.initial.board[pos1[0]][pos1[1]]=2
        self.initial.board[pos2[0]][pos2[1]]=2
        self.points = 0

    def actions(self, state):
        return state.get_moves()

    def result(self, state, move):
        ref = state.next_move(move)
        ref._replace(utility = self.utility(ref, ref.to_move))
        return ref

    def utility(self, state, player):
        return boardEmpty(state.board)

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
class Player:
    def __init__(self, name, alg):
        self.name = name
        self.alg = alg

    def display(self):
        print(self.name)

def eval_attacker(state, player):
    return

atacante = Player("atacante",
                  lambda game, state: alphabeta_cutoff_search_new(state, game, 10, eval_fn = num_livres))





""" TODO: REMOVE BEFORE DELIVERY THIS IS TEST CODE """
tmp = Jogo2048_48([0,1], [3,3])
tmp.display(tmp.initial)