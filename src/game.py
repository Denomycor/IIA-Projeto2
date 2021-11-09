import copy
from jogos import GameState
from jogos import Game
from enum import Enum



class playersEnum(Enum):
    attacker = 1
    defender = 2

def alignLeft(str, chars):
    return (" "*(chars-len(str)))+str

# GameState = namedtuple('GameState', 'to_move, utility, board, moves')
class Jogo2048State(GameState):
    
    """Returns a new state representing the board after the attacker player chooses a direction"""
    def __collapse(self, direction):
        newstate = Jogo2048State(to_move=playersEnum.defender, utility=0, board = copy.deepcopy(self.board), moves=self.moves+1)

        if direction == "cima":          
            for i in range(4):
                if newstate.board[0][i] == newstate.board[1][i] and newstate.board[1][i] == newstate.board[2][i] and newstate.board[2][i] == newstate.board[3][i]:
                    newstate.board[0][i] <<=1
                    newstate.board[1][i] <<=1
                    newstate.board[2][i] = 0
                    newstate.board[3][i] = 0
                else:
                    moved = True
                    while(moved):
                        moved = False
                        for p in range(3):

                            if newstate.board[p][i]==0 and newstate.board[p+1][i]!=0:
                                newstate.board[p][i]=newstate.board[p+1][i]
                                newstate.board[p+1][i] = 0
                                moved = True
                                continue

                            if newstate.board[p][i] == newstate.board[p+1][i] and newstate.board[p][i] !=0 :
                                newstate.board[p][i] <<=1
                                newstate.board[p+1][i] = 0
                                moved = True
                                continue

        elif direction == "esquerda":
            for i in range(4):
                if newstate.board[i][0] == newstate.board[i][1] and newstate.board[i][1] == newstate.board[i][2] and newstate.board[i][2] == newstate.board[i][3]:
                    newstate.board[i][0] <<=1
                    newstate.board[i][1] <<=1
                    newstate.board[i][2] = 0
                    newstate.board[i][3] = 0
                else:
                    moved = True
                    while(moved):
                        moved = False
                        for p in range(3):

                            if newstate.board[i][p]==0 and newstate.board[i][p+1]!=0:
                                newstate.board[i][p]=newstate.board[i][p+1]
                                newstate.board[i][p+1] = 0
                                moved = True
                                continue

                            if newstate.board[i][p] == newstate.board[i][p+1] and newstate.board[i][p] !=0 :
                                newstate.board[i][p] <<=1
                                newstate.board[i][p+1] = 0
                                moved = True
                                continue

        elif direction == "baixo":
            for i in range(4):
                if newstate.board[0][i] == newstate.board[1][i] and newstate.board[1][i] == newstate.board[2][i] and newstate.board[2][i] == newstate.board[3][i]:
                    newstate.board[3][i] <<=1
                    newstate.board[2][i] <<=1
                    newstate.board[1][i] = 0
                    newstate.board[0][i] = 0
                else:
                    moved = True
                    while(moved):
                        moved = False
                        for p in range(3, 0, -1):

                            if newstate.board[p][i]==0 and newstate.board[p-1][i]!=0:
                                newstate.board[p][i]=newstate.board[p-1][i]
                                newstate.board[p-1][i] = 0
                                moved = True
                                continue

                            if newstate.board[p][i] == newstate.board[p-1][i] and newstate.board[p][i] !=0 :
                                newstate.board[p][i] <<=1
                                newstate.board[p-1][i] = 0
                                moved = True
                                continue

        elif direction == "direita":
            for i in range(4):
                if newstate.board[i][0] == newstate.board[i][1] and newstate.board[i][1] == newstate.board[i][2] and newstate.board[i][2] == newstate.board[i][3]:
                    newstate.board[i][3] <<=1
                    newstate.board[i][2] <<=1
                    newstate.board[i][1] = 0
                    newstate.board[i][0] = 0
                else:
                    moved = True
                    while(moved):
                        moved = False
                        for p in range(3, 0, -1):

                            if newstate.board[i][p]==0 and newstate.board[i][p-1]!=0:
                                newstate.board[i][p]=newstate.board[i][p-1]
                                newstate.board[i][p-1] = 0
                                moved = True
                                continue

                            if newstate.board[i][p] == newstate.board[i][p-1] and newstate.board[i][p] !=0 :
                                newstate.board[i][p] <<=1
                                newstate.board[i][p-1] = 0
                                moved = True
                                continue
        else:
            raise RuntimeError("Error - invalid direction of movement" )

        return newstate
    
    """Returns a new state representing the board after a player action, doesn't check whether the action is valid or not"""
    def next_move(self, move):
        if self.to_move == playersEnum.attacker:
            return self.__collapse(move)
        elif self.to_move == playersEnum.defender:
            newstate = Jogo2048State(to_move=playersEnum.attacker, utility=0, board = copy.deepcopy(self.board), moves=self.moves+1)
            newstate.board[3-int(move[0])][int(move[2])] = 2
            return newstate
        else:
            raise RuntimeError("Error - invalid player descriptor")

    """Returns the other player, the one not playing this turn"""
    def other(self):
        if self.to_move == playersEnum.attacker:
            return playersEnum.defender
        if self.to_move == playersEnum.defender:
            return playersEnum.attacker
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
        if self.to_move == playersEnum.attacker:
            return [ a for a in ["cima", "direita", "baixo", "esquerda"] if self.__collapse(a).board != self.board ]
        if self.to_move == playersEnum.defender:
            res = []
            for i in range(3, -1, -1):
                for j in range(4):
                    if self.board[i][j] == 0:
                        res.append(str(3-i)+","+str(j))
            return res
        else:
            raise RuntimeError("Error - invalid player descriptor")

    
    


class Jogo2048_48(Game):

    def __init__(self, pos1, pos2):
         #Board is a list of lists 4*4 which stores the board pieces
        self.initial = Jogo2048State(to_move = playersEnum.attacker, utility = (16-2)/16.0, board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
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
        if player == playersEnum.attacker:
            return c/16.0
        if player == playersEnum.defender:
            return (16-c)/16.0
        else:
            raise RuntimeError("Error - invalid player descriptor")

    def terminal_test(self, state):
        return not (state.to_move == playersEnum.defender or bool(len(state.get_moves())))

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        state.display()

    def jogar(self, jogador1, jogador2, verbose=True):
        #TODO
        return super().jogar(jogador1, jogador2, verbose=verbose)

