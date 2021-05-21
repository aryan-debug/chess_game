import pygame
import sys

pygame.init()

RANKS = 8
FILES = 8
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
RECT_WIDTH = 100
RECT_HEIGHT = 100
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
green_color = (118,150,86)
white_color = (238,238,210)
move_color_dict = {'white':'black','black':'white'}

class Board:
    def __init__(self,ranks, files, rect_width, rect_height):
        self.ranks = ranks
        self.files = files
        self.rect_width = rect_width
        self.rect_height = rect_height
        self.rect_pos_x = 0
        self.rect_pos_y = 0
        self.color_counter = 0
        self.actual_board = self.make_board(self.ranks, self.files)
        self.move_color = 'white'
        self.white_king_pos = (7,4)
        self.black_king_pos = (0,4)
        self.king_pos_dict = {"white": self.black_king_pos, "black":self.white_king_pos}
        self.pinned_pieces = []

    def draw_board(self):
        for rank in range(self.ranks):
            for file in range(self.files):
                if self.rect_pos_x >= SCREEN_WIDTH:
                    self.rect_pos_x = 0
                    self.rect_pos_y += self.rect_height
                if self.color_counter % 2 == 0:
                    current_color = white_color
                pygame.draw.rect(screen,current_color, pygame.Rect(self.rect_pos_x,self.rect_pos_y,self.rect_width,self.rect_width))
                self.rect_pos_x += self.rect_width
                current_color = green_color
                self.color_counter += 1
            self.color_counter += 1
        self.rect_pos_x = 0
        self.rect_pos_y = 0
        self.color_counter = 0
        pygame.display.flip()

    def make_board(self,ranks,files):
        _2d_board = [[Rook("black"),Knight("black"),Bishop("black"),Queen("black"),King("black"),Bishop("black"),Knight("black"),Rook("black")],
        [Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black")]]

        for rank in range(2,self.ranks-2):
            _2d_board.append([])
            for file in range(self.files):
                _2d_board[rank].append(None)

        _2d_board.append([Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white")])
        _2d_board.append([Rook("white"),Knight("white"),Bishop("white"),Queen("white"),King("white"),Bishop("white"),Knight("white"),Rook("white")])
        return _2d_board
    
    def draw_pieces(self, board):
        for x, row in enumerate(board):
            for y, position in enumerate(row):
                if position:
                    position.draw(y*100,x*100)
                
    def is_checked(self):
        king_pos_x,king_pos_y = board.black_king_pos
        king_diagonal_moves = [(-1,-1),(-1,1),(1,-1),(1,1)]
        king_hor_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        king_knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        offset_1 = {"black":1,"white":-1}
        pieces_on_hor = []
        pieces_on_diagonal = []
        #check for diagonal check
        for x,y in king_diagonal_moves:
            offset = 1
            try:
                while -1 < king_pos_x+x*offset < 8 and -1 < king_pos_y+y*offset < 8 and (actual_board[king_pos_x+x*offset][king_pos_y+y*offset] == None or actual_board[king_pos_x][king_pos_y].color != actual_board[king_pos_x+x*offset][king_pos_y+y*offset].color):
                    pieces_on_diagonal.append((king_pos_x+x*offset,king_pos_y+y*offset))
                    offset+=1
            except AttributeError:
                pass
        #check for horizontal and vertical checks
        for x,y in king_hor_moves:
            current_x,current_y = x,y
            try:
                while -1 < current_x+king_pos_x < 8 and -1 < current_y+king_pos_y < 8 and (actual_board[current_x + king_pos_x][current_y + king_pos_y] == None or actual_board[king_pos_x][king_pos_y].color != actual_board[current_x+king_pos_x][current_y+king_pos_y].color):
                    pieces_on_hor.append((king_pos_x+current_x,king_pos_y+current_y))
                    current_x += x
                    current_y += y
            except AttributeError:
                pass
        #checks by bishop or queen
        for x,y in pieces_on_diagonal:
            if actual_board[x][y] != None and (isinstance(actual_board[x][y],Bishop) or isinstance(actual_board[x][y],Queen)):
                return True
        #checks by rook or queen
        for x,y in pieces_on_hor:
            if actual_board[x][y] != None and isinstance(actual_board[x][y],Rook) or isinstance(actual_board[x][y],Queen):
                return True
        #checks by pawn
        try:
            if (actual_board[x][y].color != actual_board[x+offset_1[actual_board[x][y].color]][y-1].color or actual_board[x][y].color != actual_board[x+offset_1[actual_board[x][y].color]][y+1].color) and (isinstance(actual_board[x-1][y-1],Pawn) or isinstance(actual_board[x-1][y+1],Pawn)):
                return True
        except AttributeError:
            pass
        #checks for knight
        for x,y in king_knight_moves:
            try:
                if isinstance(actual_board[king_pos_x + x][king_pos_y + y], Knight) and actual_board[king_pos_x][king_pos_y].color != actual_board[king_pos_x + x][king_pos_y + y].color and -1 < x < 8 and -1 < y < 8:
                    return True
            except:
                pass
        king_pos_x,king_pos_y = board.king_pos_dict[board.move_color]
        



                    
class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type
        self.image = pygame.image.load(f'piece_images\\{self.color}_{self.piece_type}.png')
    #draw the piece
    def draw(self, x, y):
        screen.blit(self.image, (x, y))

class Pawn(Piece):
    def __init__(self,color):
        self.piece_type = "pawn"
        self.first_move = True
        super().__init__(color,self.piece_type)

    def generated_valid_move(self, previous_y, previous_x):
        offset = {"black":1,"white":-1}
        valid_moves_list = []
        front = previous_y + offset[self.color]
        #check for first move
        if self.first_move:
            valid_moves_list.append((previous_y + offset[self.color]* 2, previous_x))
        #check for piece on front
        if actual_board[front][previous_x] == None:
            valid_moves_list.append((front,previous_x))
            self.has_moved = True
        #check for piece on right side
        try:
            right = previous_x+1
            if actual_board[front][right]:
                if actual_board[front][right].color != self.color:
                        valid_moves_list.append((front,right))
                        self.has_moved = True
        except IndexError:
            pass
        #check for piece on left side
        left = previous_x-1
        if actual_board[front][left]:
            if actual_board[front][left].color != self.color:
                    valid_moves_list.append((front,left))
                    self.has_moved = True
        return valid_moves_list
    
class Knight(Piece):
    def __init__(self, color):
        self.piece_type = 'knight'
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x):
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        valid_moves_list = []
        for row, col in knight_moves:
            knight_move_y = previous_y + row
            knight_move_x = previous_x + col
            try:
                if actual_board[knight_move_y][knight_move_x] == None or actual_board[knight_move_y][knight_move_x].color != self.color:
                    valid_moves_list.append((knight_move_y,knight_move_x))
            except IndexError:
                pass
        return valid_moves_list

class Bishop(Piece):
    def __init__(self, color):
        self.piece_type = 'bishop'
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x):
        valid_moves_list = []
        bishop_moves = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in bishop_moves:
            offset = 1
            y_offset = previous_y + row * offset 
            x_offset = previous_x + col * offset
            while -1 < y_offset <8 and -1 < x_offset <8 and (actual_board[y_offset][x_offset] == None or actual_board[y_offset][x_offset].color != self.color):
                y_offset = previous_y + row * offset
                x_offset = previous_x + col * offset
                valid_moves_list.append((y_offset,x_offset))
                if -1 < previous_y + row + row * offset <8 and -1 < previous_x + col + col * offset <8 and actual_board[previous_y + row + row * offset][previous_x + col + col * offset] != None and actual_board[previous_y + row + row * offset][previous_x + col + col * offset].color != self.color:
                    valid_moves_list.append((previous_y + row + row * offset, previous_x + col + col * offset))
                    break
                offset += 1
        return valid_moves_list
        

class Rook(Piece):
    def __init__(self,color):
        self.piece_type = 'rook'
        super().__init__(color, self.piece_type)
    
    def generated_valid_move(self,previous_y,previous_x):
        valid_moves_list = []
        rook_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        for row, col in rook_moves:
            current_x, current_y = col, row
            while -1 < previous_y + current_y < 8 and -1 < previous_x + current_x < 8 and actual_board[previous_y + current_y][previous_x + current_x] == None:
                valid_moves_list.append((previous_y + current_y,previous_x + current_x))
                if -1 < previous_y + current_y + row< 8 and -1 < previous_x + current_x + col< 8 and actual_board[previous_y + current_y + row][previous_x + current_x + col] != None and actual_board[previous_y + current_y + row][previous_x + current_x + col].color != self.color:
                    valid_moves_list.append((previous_y + current_y + row,previous_x + current_x + col))
                    break
                current_x += col
                current_y += row
        return valid_moves_list


class Queen(Piece):
    def  __init__(self, color):
        self.piece_type = "queen"
        super().__init__(color,self.piece_type)
    def generated_valid_move(self,previous_y,previous_x):
        valid_moves_list = []
        rook_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        bishop_moves = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in rook_moves:
            current_x, current_y = col, row
            while -1 < previous_y + current_y < 8 and -1 < previous_x + current_x < 8 and actual_board[previous_y + current_y][previous_x + current_x] == None:
                valid_moves_list.append((previous_y + current_y, previous_x + current_x))
                if -1 < previous_y + current_y  + row< 8 and -1 < previous_x + current_x + col < 8 and actual_board[previous_y + current_y + row][previous_x + current_x + col] != None and actual_board[previous_y + current_y + row][previous_x + current_x + col].color != self.color:
                    valid_moves_list.append((previous_y + current_y + row,previous_x + current_x + col))
                    break
                current_x += col
                current_y += row
        for row, col in bishop_moves:
            offset = 1
            while -1 < previous_y + row * offset <8 and -1 < previous_x + col * offset <8 and actual_board[previous_y + row*offset][previous_x + col * offset] == None:
                valid_moves_list.append((previous_y + row*offset,previous_x + col * offset))
                if -1 < previous_y + row + row * offset <8 and -1 < previous_x + col + col * offset <8 and actual_board[previous_y + row + row * offset][previous_x + col + col * offset] != None and actual_board[previous_y + row + row * offset][previous_x + col + col * offset].color != self.color:
                    valid_moves_list.append((previous_y + row + row * offset, previous_x + col + col * offset))
                    break
                offset += 1
        return valid_moves_list
        

class King(Piece):
    def __init__(self, color):
        self.piece_type = 'king'
        super().__init__(color, self.piece_type)
    
    def generated_valid_move(self, previous_y, previous_x):
        valid_moves_list = []
        king_moves = [(0,1),(0,-1),(1,0),(-1,0),(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in king_moves:
            if -1 < previous_y + col < 8 and -1 < previous_x + row < 8 and actual_board[previous_y + col][previous_x + row] != self.color:
                valid_moves_list.append((previous_y + col, previous_x + row))
        return valid_moves_list

board = Board(RANKS,FILES, RECT_WIDTH, RECT_HEIGHT)
fake_board = Board(RANKS,FILES, RECT_WIDTH, RECT_HEIGHT)
board.draw_board()
actual_board = board.make_board(RANKS,FILES)
fake_board_copy = actual_board[:]
board.draw_pieces(actual_board)
pygame.display.update()
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x,y = event.pos
            previous_x, previous_y = x//100,y//100
            current_piece = actual_board[previous_y][previous_x]
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if current_piece != None and board.move_color == current_piece.color:
                x,y = event.pos
                new_x, new_y = x//100,y//100
                fake_board_copy = actual_board[:]
                fake_board_copy[previous_y][previous_x] = actual_board[new_y][new_x]
                if fake_board.is_checked():
                    pass
                if current_piece not in board.pinned_pieces:
                    if (new_y,new_x) in current_piece.generated_valid_move(previous_y, previous_x):
                        actual_board[new_y][new_x] = current_piece
                        actual_board[previous_y][previous_x] = None
                        board.draw_board()
                        board.draw_pieces(actual_board)
                        board.move_color = move_color_dict[current_piece.color]
                        if isinstance(current_piece, Pawn):
                            current_piece.first_move = False
                        if isinstance(current_piece, King) and current_piece.color == "white":
                            board.white_king_pos = (new_y,new_x)
                        elif isinstance(current_piece, King) and current_piece.color == "black":
                            board.black_king_pos = (new_y,new_x)
                pygame.display.update()

            
  
