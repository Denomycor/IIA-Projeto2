from jogos import Game

class Jogo2048_48(Game):

    #Board is a list of lists 4*4 which stores the board pieces
    board = [ [ 0 for j in range(4)] for i in range(4)]

    def __init__(self, pos1, pos2):
        self.board[pos1[0]][pos1[1]]=2
        self.board[pos2[0]][pos2[1]]=2

    