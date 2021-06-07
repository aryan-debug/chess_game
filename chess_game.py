import pygame
import sys
from copy import deepcopy
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
white_king_pos = (7,4)
black_king_pos = (0,4)
king_pos_dict = {"white": white_king_pos, "black": black_king_pos}

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
                
    def is_checked(self,board):
        for king_pos_y,king_pos_x in king_pos_dict.values():
            for row in range(RANKS):
                for col in range(FILES):
                    current_piece = board[row][col]
                    try:
                        if current_piece != None and current_piece.color != board[king_pos_y][king_pos_x].color:
                            if isinstance(current_piece, King):
                                if len({*current_piece.generated_moves(row,col,board)}.intersection({(king_pos_y, king_pos_x)})):
                                    return True, board[king_pos_y][king_pos_x].color, {*current_piece.generated_moves(row, col, board)}, {(row, col)}
                            else:
                                if len({*current_piece.generated_valid_move(row,col, board)}.intersection({(king_pos_y, king_pos_x)})):
                                    return True, board[king_pos_y][king_pos_x].color, {*current_piece.generated_valid_move(row, col, board)}, {(row, col)}
                    except AttributeError:
                        pass
        return False, None, None, None

    def is_checkmated(self, king_color, piece_moves, king_moves, piece_y_x):
        if not len(king_moves) and not self.can_be_blocked(king_color,  fake_board_copy, piece_moves) and not self.can_be_captured(king_color, fake_board_copy, piece_y_x):
            return True
        return False
    def can_be_blocked(self, king_color, board, piece_moves):
        board_copy = [row[:] for row in board]
        for row in range(RANKS):
            for col in range(RANKS):
                current_piece = board_copy[row][col]
                if current_piece != None and current_piece.color == king_color and not isinstance(current_piece, King):
                    current_piece_moves = current_piece.generated_valid_move(row, col, board_copy)
                    for move_y, move_x in {*current_piece_moves}.intersection(piece_moves):
                        board_copy[move_y][move_x] = current_piece
                        board_copy[row][col] = None
                        is_check = self.is_checked(board_copy)[0]
                        if not is_check:
                            board_copy = [row[:] for row in board]
                            return True
                        board_copy = [row[:] for row in board]
        return False
    def can_be_captured(self, king_color, board, piece_y_x):
        for row in range(RANKS):
            for col in range(RANKS):
                current_piece = board[row][col]
                if current_piece != None and current_piece.color == king_color :
                    current_piece_moves = current_piece.generated_valid_move(row, col, board)
                    for move_y, move_x in {*current_piece_moves}.intersection(piece_y_x):
                        board[move_y][move_x] = current_piece
                        board[row][col] = None
                        is_check = self.is_checked(board)[0]
                        if not is_check:
                            board = [row[:] for row in fake_board_copy]
                            return True
                        board = [row[:] for row in fake_board_copy]
        return False  
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

    def generated_valid_move(self, previous_y, previous_x, board):
        offset = {"black":1,"white":-1}
        valid_moves_list = []
        front = previous_y + offset[self.color]
        #check for first move
        if self.first_move and board[previous_y + offset[self.color]* 2][previous_x] == None:
            valid_moves_list.append((previous_y + offset[self.color]* 2, previous_x))
        #check for piece on front
        if board[front][previous_x] == None:
            valid_moves_list.append((front,previous_x))
            self.has_moved = True
        #check for piece on right side
        try:
            right = previous_x+1
            if board[front][right]:
                if board[front][right].color != self.color:
                    valid_moves_list.append((front,right))
                    self.has_moved = True
        except IndexError:
            pass
        #check for piece on left side
        left = previous_x-1
        if board[front][left]:
            if board[front][left].color != self.color:
                valid_moves_list.append((front,left))
                self.has_moved = True
        return valid_moves_list
    
class Knight(Piece):
    def __init__(self, color):
        self.piece_type = 'knight'
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        valid_moves_list = []
        for row, col in knight_moves:
            knight_move_y = previous_y + row
            knight_move_x = previous_x + col
            if -1 < knight_move_y < RANKS and -1 < knight_move_x < RANKS and (board[knight_move_y][knight_move_x] == None or (board[knight_move_y][knight_move_x] != None and board[knight_move_y][knight_move_x].color != self.color)):
                valid_moves_list.append((knight_move_y,knight_move_x))
        return valid_moves_list

class Bishop(Piece):
    def __init__(self, color):
        self.piece_type = 'bishop'
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves_list = []
        bishop_moves = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in bishop_moves:
            current_y = previous_y + row
            current_x =  previous_x + col
            for x in range(0,RANKS):
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    if board[current_y][current_x] != None and board[current_y][current_x].color != self.color:
                        valid_moves_list.append((current_y, current_x))
                        break
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else:
                        break
                current_x += col
                current_y +=  row
        return valid_moves_list
                
class Rook(Piece):
    def __init__(self,color):
        self.piece_type = 'rook'
        super().__init__(color, self.piece_type)
    
    def generated_valid_move(self,previous_y,previous_x, board):
        valid_moves_list = []
        rook_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        for row, col in rook_moves:
            current_y = previous_y + row
            current_x = previous_x + col
            for x in range(0, RANKS):
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    if board[current_y][current_x] != None and board[current_y][current_x].color != self.color:
                        valid_moves_list.append((current_y, current_x))
                        break
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else: break
                current_x += col
                current_y +=  row
        return valid_moves_list
                



class Queen(Piece):
    def  __init__(self, color):
        self.piece_type = "queen"
        super().__init__(color,self.piece_type)
    def generated_valid_move(self,previous_y,previous_x, board):
        valid_moves_list = []
        queen_moves = [(0,1),(0,-1),(1,0),(-1,0),(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in queen_moves:
            current_y = previous_y + row
            current_x =  previous_x + col
            for x in range(0,RANKS):
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    if board[current_y][current_x] != None and board[current_y][current_x].color != self.color:
                        valid_moves_list.append((current_y, current_x))
                        break
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else:
                        break
                current_x += col
                current_y +=  row
        return valid_moves_list
        

class King(Piece):
    def __init__(self, color):
        self.piece_type = 'king'
        super().__init__(color, self.piece_type)
    
    def generated_moves(self, previous_y, previous_x, board):
        moves_list = []
        king_moves = [(0,1),(0,-1),(1,0),(-1,0),(-1,-1),(-1,1),(1,-1),(1,1)]
        for row, col in king_moves:
            current_y = previous_y + row
            current_x = previous_x + col
            if -1 < current_y < RANKS and -1 < current_x < RANKS:
                if board[current_y][current_x] == None:
                    moves_list.append((current_y, current_x))
                if board[current_y][current_x] != None and board[current_y][current_x].color != self.color:
                    moves_list.append((current_y, current_x))
        return moves_list

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves = self.filtered_moves(board)
        return valid_moves

    def filtered_moves(self, a_board):
        a_board_copy = [row[:] for row in a_board]
        #get opposite colored king's position
        king_pos_y, king_pos_x = king_pos_dict[board.move_color]
        king = a_board[king_pos_y][king_pos_x]
        king_moves = self.generated_moves(king_pos_y, king_pos_x, a_board)
        valid_moves = []
        for move_y, move_x in king_moves:
            #move the king to that position
            a_board_copy[move_y][move_x] = king
            a_board_copy[king_pos_y][king_pos_x] = None
            if self.color == "white":
                king_pos_dict["white"] = (move_y,move_x)
            if self.color == "black":
                king_pos_dict["black"] = (move_y,move_x)
            #check if it is a check
            is_check = board.is_checked(a_board_copy)[0]
            if not is_check:
                valid_moves.append((move_y, move_x))
            #reset the fake board
            if self.color == "white":
                king_pos_dict["white"] = (king_pos_y,king_pos_x)
            if self.color == "black":
                king_pos_dict["black"] = (king_pos_y,king_pos_x)
            a_board_copy = [row[:] for row in a_board]
        return valid_moves
            


board = Board(RANKS,FILES, RECT_WIDTH, RECT_HEIGHT)
board.draw_board()
actual_board = board.make_board(RANKS,FILES)
fake_board_copy = [row[:] for row in actual_board]
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
                if (new_y,new_x) in current_piece.generated_valid_move(previous_y, previous_x,fake_board_copy):
                    fake_board_copy[new_y][new_x] = current_piece
                    fake_board_copy[previous_y][previous_x] = None
                    if isinstance(current_piece, Pawn):
                            current_piece.first_move = False
                    if isinstance(current_piece, King) and current_piece.color == "white":
                        king_pos_dict["white"] = (new_y,new_x)
                    elif isinstance(current_piece, King) and current_piece.color == "black":
                        king_pos_dict["black"] = (new_y,new_x)
                    is_check, king_color, piece_moves, piece_y_x = board.is_checked(fake_board_copy)
                    if is_check:
                        king_y, king_x = king_pos_dict[board.move_color]
                        king_moves = fake_board_copy[king_y][king_x].generated_valid_move(king_y, king_x, fake_board_copy)
                        if board.is_checkmated(king_color, piece_moves, king_moves, piece_y_x):
                            actual_board[new_y][new_x] = current_piece
                            actual_board[previous_y][previous_x] = None
                            board.draw_board()
                            board.draw_pieces(actual_board)
                            board.move_color = move_color_dict[current_piece.color]
                            pygame.display.update()
                            print(f"{board.move_color} is checkmated")
                            break
                        if king_color == board.move_color:
                            fake_board_copy = [row[:] for row in actual_board]
                            continue
                    actual_board[new_y][new_x] = current_piece
                    actual_board[previous_y][previous_x] = None
                    fake_board_copy = [row[:] for row in actual_board]
                    if current_piece not in board.pinned_pieces:
                        board.draw_board()
                        board.draw_pieces(actual_board)
                        board.move_color = move_color_dict[current_piece.color]
                        pygame.display.update()
                    board.pinned_pieces = []