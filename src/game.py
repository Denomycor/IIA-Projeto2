import copy
from jogos import GameState
from jogos import Game


#Helpers
ref = [0,0,0,0]

def alignLeft(str, chars):
    return (" "*(chars-len(str)))+str

def reverse( line ):
    return line[::-1]

def transpose( matrix ):
    return list(map(lambda x: list(x), zip(*matrix)))

def removeZeros( line ):
    return list(filter( lambda x: x != 0, line))

def sumStep( line ):
    if len(line) < 2:
        return False

    done = False
    for i in range(len(line)-2, -1, -1):
        if line[i] == line[i+1]:
            line[i+1] *= 2
            line[i] = 0
            i -= 1
            done = True
            continue
    return done

def pad( line ):
    return ref[:len(ref)-len(line):] + line

def sumLine( line ):
    li = removeZeros(line)

    while sumStep( li ):
        li = removeZeros( li )
    return pad(li)

move = {
    "direita": lambda m: list( map( lambda l: sumLine(l), m )), 
    "esquerda": lambda m: list( map( lambda l: reverse(sumLine(reverse(l))) , m )),
    "cima": lambda m: transpose( map( lambda l: reverse(sumLine(reverse(l))) , transpose(m) ) ),
    "baixo": lambda m: transpose( map( lambda l: sumLine(l) , transpose(m) ) ),
}

#TODO Remove player enum, change to "atacante" e "defendor" strings
#Start to work on players AI functions

"""--------------------------------------------------------------------------------------
    State Class
--------------------------------------------------------------------------------------"""
class Jogo2048State(GameState):
    
    """Returns a new state representing the board after the attacker player chooses a direction"""
    def __collapse(self, direction):
        try:
            newstate = Jogo2048State(to_move="defensor", utility=0, board = move[direction](self.board), moves=self.moves+1)
        except KeyError:
            raise RuntimeError("Error - invalid direction of movement" )

        return newstate
    
    """Returns a new state representing the board after a player action, doesn't check whether the action is valid or not"""
    def next_move(self, move):
        if self.to_move == "atacante":
            return self.__collapse(move)
        elif self.to_move == "defensor":
            newstate = Jogo2048State(to_move="atacante", utility=0, board = copy.deepcopy(self.board), moves=self.moves+1)
            newstate.board[3-int(move[0])][int(move[2])] = 2
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
        for i in self.board:
            for j in i:
                print(alignLeft(str(j), 5), end=" ")
            print()
        print("-"*28)

    """Returns all valid moves for the state"""
    def get_moves(self):
        if self.to_move == "atacante":
            return [ a for a in ["cima", "direita", "baixo", "esquerda"] if self.__collapse(a).board != self.board ]
        if self.to_move == "defensor":
            res = []
            for i in range(3, -1, -1):
                for j in range(4):
                    if self.board[i][j] == 0:
                        res.append(str(3-i)+","+str(j))
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
        self.initial.board[3-pos1[0]][pos1[1]]=2
        self.initial.board[3-pos2[0]][pos2[1]]=2
        self.points = 0

    def actions(self, state):
        return state.get_moves()

    def result(self, state, move):
        return state.next_move(move)

    def utility(self, state, player):
        # A state is as usefull, for the attacker, as the number of empty pieces on the board.
        c = 0
        for i in state.board:
            for j in i:
                if j==0:
                    c+=1
        if player == "atacante":
            return c/16.0
        if player == "defensor":
            return (16-c)/16.0
        else:
            raise RuntimeError("Error - invalid player descriptor")

    def terminal_test(self, state):
        return not (state.to_move == "defensor" or bool(len(state.get_moves())))

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        state.display()

    def jogar(self, jogador1, jogador2, verbose=True):
        #TODO
        return super().jogar(jogador1, jogador2, verbose=verbose)
