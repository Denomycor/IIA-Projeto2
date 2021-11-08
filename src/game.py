import copy
from jogos import GameState
from jogos import Game
from enum import Enum




class playersEnum(Enum):
    attacker = 1
    defender = 2

class attackerActionsEnum(Enum):
    cima = 0
    baixo = 1
    direita = 2
    esquerda = 3



# GameState = namedtuple('GameState', 'to_move, utility, board, moves')
class Jogo2048State(GameState):
    
    """Returns a new state representing the board after the attacker player chooses a direction"""
    def __collapse(self, direction):
        newstate = copy.deepcopy(self)
        newstate.to_move = playersEnum.defender
        newstate.moves += 1

        if direction == attackerActionsEnum.cima:
            for i in range(4):
                moved = True
                while(moved):
                    moved = False
                    for p in range(3):

                        if newstate.board[p][i]==0 and newstate.board[p+1][i]!=0:
                            newstate.board[p][i]=newstate.board[p+1][i]
                            newstate.board[p+1][i] = 0
                            moved = True
                            continue

                        if newstate.board[p][i] == newstate.board[p+1][i]:
                            newstate.board[p][i] <<=1
                            newstate.board[p+1][i] = 0
                            moved = True
                            continue

        elif direction == attackerActionsEnum.direita:
            for i in range(4):
                moved = True
                while(moved):
                    moved = False
                    for p in range(3):

                        if newstate.board[i][p]==0 and newstate.board[i][p+1]!=0:
                            newstate.board[i][p]=newstate.board[i][p+1]
                            newstate.board[i][p+1] = 0
                            moved = True
                            continue

                        if newstate.board[i][p] == newstate.board[i][p+1]:
                            newstate.board[i][p] <<=1
                            newstate.board[i][p+1] = 0
                            moved = True
                            continue

        elif direction == attackerActionsEnum.baixo:
            for i in range(4):
                moved = True
                while(moved):
                    moved = False
                    for p in range(3, 0, -1):

                        if newstate.board[p][i]==0 and newstate.board[p-1][i]!=0:
                            newstate.board[p][i]=newstate.board[p-1][i]
                            newstate.board[p-1][i] = 0
                            moved = True
                            continue

                        if newstate.board[p][i] == newstate.board[p-1][i]:
                            newstate.board[p][i] <<=1
                            newstate.board[p-1][i] = 0
                            moved = True
                            continue

        elif direction == attackerActionsEnum.esquerda:
            for i in range(4):
                moved = True
                while(moved):
                    moved = False
                    for p in range(3, 0, -1):

                        if newstate.board[i][p]==0 and newstate.board[i][p-1]!=0:
                            newstate.board[i][p]=newstate.board[i][p-1]
                            newstate.board[i][p-1] = 0
                            moved = True
                            continue

                        if newstate.board[i][p] == newstate.board[i][p-1]:
                            newstate.board[i][p] <<=1
                            newstate.board[i][p-1] = 0
                            moved = True
                            continue
        else:
            print("Error - invalid direction of movement" )

        return newstate
    
    """Returns a new state representing the board after a player action, doesn't check whether the action is valid or not"""
    def next_move(self, move):
        if self.to_move == playersEnum.attacker:
            return self.__collapse(move)
        elif self.to_move == playersEnum.defender:
            newstate = copy.deepcopy(self)
            newstate.to_move = playersEnum.attacker
            newstate.moves += 1
            self.board[3-move[0]][move[1]] = 2
            return newstate
        else:
            print("Error - invalid player descriptor")

    """Returns the other player, the one not playing this turn"""
    def other(self):
        if self.to_move == playersEnum.attacker:
            return playersEnum.defender
        if self.to_move == playersEnum.defender:
            return playersEnum.attacker
        else:
            print("Error - invalid player descriptor")

    """Prints the board"""
    def display(self):
        #TODO
        return

    """Returns all valid moves for the state"""
    def get_moves(self):
        if self.to_move == playersEnum.attacker:
            return [ a for a in attackerActionsEnum if self.__collapse(a).board != self.board ]
        if self.to_move == playersEnum.defender:
            res = []
            for i in range(4):
                for j in range(4):
                    if self.board[3-i][j] == 0:
                        res.append((3-i, j))
            return res
        else:
            print("Error - invalid player descriptor")

    
    


class Jogo2048_48(Game):

    def __init__(self, pos1, pos2):
         #Board is a list of lists 4*4 which stores the board pieces
        self.initial = Jogo2048State(to_move = playersEnum.attacker, utility = [], board = [ [ 0 for j in range(4)] for i in range(4)], moves = 0)
        self.initial.board[3-pos1[0]][pos1[1]]=2
        self.initial.board[3-pos2[0]][pos2[1]]=2
        self.points = 0

    def actions(self, state):
        return state.get_moves()

    def result(self, state, move):
        return state.next_move(move)

    def utility(self, state, player):
        #TODO
        return

    def terminal_test(self, state):
        return state.to_move == playersEnum.defender or bool(len(state.get_moves()))

    def to_move(self, state):
        return state.to__move

    def display(self, state):
        state.display()

    
