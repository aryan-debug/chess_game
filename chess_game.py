import pygame
import sys
from copy import deepcopy

from pygame.constants import CONTROLLERBUTTONUP

pygame.init()
import math

RANKS = 8
FILES = 8
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
RECT_WIDTH = 100
RECT_HEIGHT = 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
green_color = (118, 150, 86)
white_color = (238, 238, 210)
move_color_dict = {"white": "black", "black": "white"}
white_king_pos = (7, 4)
black_king_pos = (0, 4)
king_pos_dict = {"white": white_king_pos, "black": black_king_pos}


class Board:
    def __init__(self, ranks, files, rect_width, rect_height):
        self.ranks = ranks
        self.files = files
        self.rect_width = rect_width
        self.rect_height = rect_height
        self.rect_pos_x = 0
        self.rect_pos_y = 0
        self.color_counter = 0
        self.actual_board = self.make_board(self.ranks, self.files)
        self.move_color = "white"
        self.pinned_pieces = []
        self.board = None

    def draw_board(self):
        if self.board is None:
            self.board = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for rank in range(self.ranks):
                for file in range(self.files):
                    if self.rect_pos_x >= SCREEN_WIDTH:
                        self.rect_pos_x = 0
                        self.rect_pos_y += self.rect_height
                    # switch colors
                    if self.color_counter % 2 == 0:
                        current_color = white_color
                    pygame.draw.rect(
                        self.board,
                        current_color,
                        pygame.Rect(
                            self.rect_pos_x,
                            self.rect_pos_y,
                            self.rect_width,
                            self.rect_width,
                        ),
                    )
                    self.rect_pos_x += self.rect_width
                    current_color = green_color
                    self.color_counter += 1
                self.color_counter += 1
            self.rect_pos_x = 0
            self.rect_pos_y = 0
            self.color_counter = 0
        screen.blit(self.board, (0, 0))

    def make_board(self, ranks, files):
        # black pieces
        _2d_board = [
            [
                Rook("black"),
                Knight("black"),
                Bishop("black"),
                Queen("black"),
                King("black"),
                Bishop("black"),
                Knight("black"),
                Rook("black"),
            ],
            [
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
                Pawn("black"),
            ],
        ]

        for rank in range(2, self.ranks - 2):
            _2d_board.append([])
            for file in range(self.files):
                _2d_board[rank].append(None)
        # white pieces
        _2d_board.append(
            [
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
                Pawn("white"),
            ]
        )
        _2d_board.append(
            [
                Rook("white"),
                Knight("white"),
                Bishop("white"),
                Queen("white"),
                King("white"),
                Bishop("white"),
                Knight("white"),
                Rook("white"),
            ]
        )
        return _2d_board

    def draw_pieces(self, board):
        for x, row in enumerate(board):
            for y, position in enumerate(row):
                if position and not position.active and position.is_valid:
                    position.draw(y * 100, x * 100)

    def redraw_board(self):
        self.draw_board()
        self.draw_pieces(actual_board)

    def is_checked(self, board):
        # go through king position and the whole board
        for king_pos_y, king_pos_x in king_pos_dict.values():
            for row in range(RANKS):
                for col in range(FILES):
                    current_piece = board[row][col]
                    try:
                        # pick pieces that are of opposite color
                        if (
                            current_piece != None
                            and current_piece.color
                            != board[king_pos_y][king_pos_x].color
                        ):
                            if isinstance(current_piece, King):
                                if len(
                                    {
                                        *current_piece.generated_moves(row, col, board)
                                    }.intersection({(king_pos_y, king_pos_x)})
                                ):
                                    return (
                                        True,
                                        board[king_pos_y][king_pos_x].color,
                                        {
                                            *current_piece.generated_moves(
                                                row, col, board
                                            )
                                        },
                                        {(row, col)},
                                    )
                            else:
                                # check if opposite colored piece's moves intersect with king's position
                                if len(
                                    {
                                        *current_piece.generated_valid_move(
                                            row, col, board
                                        )
                                    }.intersection({(king_pos_y, king_pos_x)})
                                ):
                                    return (
                                        True,
                                        board[king_pos_y][king_pos_x].color,
                                        {
                                            *current_piece.generated_valid_move(
                                                row, col, board
                                            )
                                        },
                                        {(row, col)},
                                    )
                    except AttributeError:
                        pass
        return False, None, None, None

    def is_checkmated(self, king_color, piece_moves, king_moves, piece_y_x):
        if (
            not len(king_moves)
            and not self.can_be_blocked(king_color, fake_board, piece_moves)
            and not self.can_be_captured(king_color, fake_board, piece_y_x)
        ):
            return True
        return False

    def can_be_blocked(self, king_color, board, piece_moves):
        board_copy = [row[:] for row in board]
        for row in range(RANKS):
            for col in range(RANKS):
                current_piece = board_copy[row][col]
                # pick same colored pieces
                if (
                    current_piece != None
                    and current_piece.color == king_color
                    and not isinstance(current_piece, King)
                ):
                    current_piece_moves = current_piece.generated_valid_move(
                        row, col, board_copy
                    )
                    # moves that intersect with the piece that gives a check
                    for move_y, move_x in {*current_piece_moves}.intersection(
                        piece_moves
                    ):
                        # play the move on fake board
                        board_copy[move_y][move_x] = current_piece
                        board_copy[row][col] = None
                        # check if it is a check
                        is_check = self.is_checked(board_copy)[0]
                        if not is_check:
                            # reset the board
                            board_copy = [row[:] for row in board]
                            return True
                        # reset the board
                        board_copy = [row[:] for row in board]
        return False

    def can_be_captured(self, king_color, board, piece_y_x):
        for row in range(RANKS):
            for col in range(RANKS):
                current_piece = board[row][col]
                # same colored pieces
                if current_piece != None and current_piece.color == king_color:
                    current_piece_moves = current_piece.generated_valid_move(
                        row, col, board
                    )
                    # same colored pieces that intersect with the piece that gives the check
                    for move_y, move_x in {*current_piece_moves}.intersection(
                        piece_y_x
                    ):
                        # play the move
                        board[move_y][move_x] = current_piece
                        board[row][col] = None
                        # check if it is still check
                        is_check = self.is_checked(board)[0]
                        if not is_check:
                            # reset the board
                            board = [row[:] for row in fake_board]
                            return True
                        board = [row[:] for row in fake_board]
        return False


class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type
        self.image = pygame.image.load(
            f"piece_images/{self.color}_{self.piece_type}.png"
        )
        self.active = False
        self.is_valid = True

    # draw the piece
    def draw(self, x, y):
        screen.blit(self.image, (x, y))


class Pawn(Piece):
    def __init__(self, color):
        self.piece_type = "pawn"
        self.first_move = True
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        offset = {"black": 1, "white": -1}
        valid_moves_list = []
        front = previous_y + offset[self.color]
        # check for first move
        if (
            self.first_move
            and board[previous_y + offset[self.color] * 2][previous_x] == None
        ):
            valid_moves_list.append((previous_y + offset[self.color] * 2, previous_x))
        # check for piece on front
        if board[front][previous_x] == None:
            valid_moves_list.append((front, previous_x))
            self.has_moved = True
        # check for piece on right side
        try:
            right = previous_x + 1
            if board[front][right]:
                if board[front][right].color != self.color:
                    valid_moves_list.append((front, right))
                    self.has_moved = True
        except IndexError:
            pass
        # check for piece on left side
        left = previous_x - 1
        if board[front][left]:
            if board[front][left].color != self.color:
                valid_moves_list.append((front, left))
                self.has_moved = True
        return valid_moves_list


class Knight(Piece):
    def __init__(self, color):
        self.piece_type = "knight"
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        knight_moves = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]
        valid_moves_list = []
        for row, col in knight_moves:
            knight_move_y = previous_y + row
            knight_move_x = previous_x + col
            # check if the move is going out of the board or a square is free or it can capture a piece
            if (
                -1 < knight_move_y < RANKS
                and -1 < knight_move_x < RANKS
                and (
                    board[knight_move_y][knight_move_x] == None
                    or (
                        board[knight_move_y][knight_move_x] != None
                        and board[knight_move_y][knight_move_x].color != self.color
                    )
                )
            ):
                valid_moves_list.append((knight_move_y, knight_move_x))
        return valid_moves_list


class Bishop(Piece):
    def __init__(self, color):
        self.piece_type = "bishop"
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves_list = []
        bishop_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for row, col in bishop_moves:
            current_y = previous_y + row
            current_x = previous_x + col
            for x in range(0, RANKS):
                # check if the move is outside the board
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    # check for captures
                    if (
                        board[current_y][current_x] != None
                        and board[current_y][current_x].color != self.color
                    ):
                        valid_moves_list.append((current_y, current_x))
                        break
                    # check for empty squares
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else:
                        break
                current_x += col
                current_y += row
        return valid_moves_list


class Rook(Piece):
    def __init__(self, color):
        self.piece_type = "rook"
        self.has_moved = False
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves_list = []
        rook_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for row, col in rook_moves:
            current_y = previous_y + row
            current_x = previous_x + col
            for x in range(0, RANKS):
                # check if the move is outside the board
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    # check for captures
                    if (
                        board[current_y][current_x] != None
                        and board[current_y][current_x].color != self.color
                    ):
                        valid_moves_list.append((current_y, current_x))
                        break
                    # check for empty square
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else:
                        break
                current_x += col
                current_y += row
        return valid_moves_list


class Queen(Piece):
    def __init__(self, color):
        self.piece_type = "queen"
        super().__init__(color, self.piece_type)

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves_list = []
        queen_moves = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        for row, col in queen_moves:
            current_y = previous_y + row
            current_x = previous_x + col
            for x in range(0, RANKS):
                # same stuff here
                if -1 < current_y < RANKS and -1 < current_x < RANKS:
                    if (
                        board[current_y][current_x] != None
                        and board[current_y][current_x].color != self.color
                    ):
                        valid_moves_list.append((current_y, current_x))
                        break
                    if board[current_y][current_x] == None:
                        valid_moves_list.append((current_y, current_x))
                    else:
                        break
                current_x += col
                current_y += row
        return valid_moves_list


class King(Piece):
    def __init__(self, color):
        self.piece_type = "king"
        self.has_moved = False
        super().__init__(color, self.piece_type)

    def generated_moves(self, previous_y, previous_x, board):
        king_pos_y, king_pos_x = king_pos_dict[self.color]
        moves_list = []
        king_moves = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        for row, col in king_moves:
            current_y = king_pos_y + row
            current_x = king_pos_x + col
            # same stuff here
            if -1 < current_y < RANKS and -1 < current_x < RANKS:
                if board[current_y][current_x] == None:
                    moves_list.append((current_y, current_x))
                if (
                    board[current_y][current_x] != None
                    and board[current_y][current_x].color != self.color
                ):
                    moves_list.append((current_y, current_x))
        # returns all the moves except the pieces it cannot capture (i.e. same colored pieces)
        return moves_list

    def generated_valid_move(self, previous_y, previous_x, board):
        valid_moves = self.filtered_moves(board)
        return valid_moves

    def filtered_moves(self, a_board):
        a_board_copy = [row[:] for row in a_board]
        # get opposite colored king's position
        king_pos_y, king_pos_x = king_pos_dict[board.move_color]
        king = a_board[king_pos_y][king_pos_x]
        king_moves = self.generated_moves(king_pos_y, king_pos_x, a_board)
        valid_moves = []
        for move_y, move_x in king_moves:
            # move the king to that position
            if a_board_copy[move_y][move_x] == None:
                a_board_copy[move_y][move_x] = king
                a_board_copy[king_pos_y][king_pos_x] = None

                # check if it is a check
                king_pos_dict[king.color] = (move_y, move_x)

                is_check = board.is_checked(a_board_copy)[0]

                king_pos_dict[king.color] = (king_pos_y, king_pos_x)

                if not is_check:
                    valid_moves.append((move_y, move_x))
                # reset the fake board
                a_board_copy = [row[:] for row in a_board]
        return valid_moves

    def short_castle(self, board, color, rook_x):
        # get king's position
        king_pos_y, king_pos_x = king_pos_dict[color]
        # get rook's position
        rook = board[king_pos_y][rook_x]
        # check for pieces between rook and bishop
        pieces_in_between = not all(
            piece is None for piece in board[king_pos_y][king_pos_x + 1 : -1]
        )
        # check if these square are occupied by other piece's valid moves
        check_squares = {(king_pos_y, king_pos_x + 1), (king_pos_y, king_pos_x + 2)}
        can_castle = True
        # checking for it here
        for row in range(RANKS):
            for col in range(FILES):
                current_piece = board[row][col]
                if (
                    current_piece != None
                    and current_piece.color != board[king_pos_y][king_pos_x].color
                ):
                    if isinstance(current_piece, King):
                        if len(
                            {
                                *current_piece.generated_moves(row, col, board)
                            }.intersection(check_squares)
                        ):
                            can_castle = False
                    else:
                        if len(
                            {
                                *current_piece.generated_valid_move(row, col, board)
                            }.intersection(check_squares)
                        ):
                            can_castle = False
        # check if pieces are not there and king or rook have not moved and "check_squares" are not occupied
        if (
            not pieces_in_between
            and not self.has_moved
            and not rook.has_moved
            and can_castle
        ):
            # move the king and rook
            board[king_pos_y][king_pos_x + 2] = self
            board[king_pos_y][king_pos_x] = None
            # change king's position in the dictionary
            king_pos_dict[self.color] = (king_pos_y, king_pos_x + 2)
            board[king_pos_y][rook_x - 2] = rook
            board[king_pos_y][rook_x] = None
        return board

    def long_castle(self, board, color, rook_x):
        # basically, the same stuff here
        board_copy = [row[:] for row in board]
        king_pos_y, king_pos_x = king_pos_dict[color]
        rook = board[king_pos_y][rook_x]
        pieces_in_between = not all(
            piece is None for piece in board[king_pos_y][-1 : king_pos_x - 1]
        )
        can_castle = True
        check_squares = {(king_pos_y, king_pos_x - 1), (king_pos_y, king_pos_x - 2)}
        for row in range(RANKS):
            for col in range(FILES):
                current_piece = board[row][col]
                if (
                    current_piece != None
                    and current_piece.color != board_copy[king_pos_y][king_pos_x].color
                ):
                    if isinstance(current_piece, King):
                        if len(
                            {
                                *current_piece.generated_moves(row, col, board_copy)
                            }.intersection(check_squares)
                        ):
                            can_castle = False
                    else:
                        if len(
                            {
                                *current_piece.generated_valid_move(
                                    row, col, board_copy
                                )
                            }.intersection(check_squares)
                        ):
                            can_castle = False
        if (
            not pieces_in_between
            and not self.has_moved
            and not rook.has_moved
            and can_castle
        ):
            board[king_pos_y][king_pos_x - 2] = self
            board[king_pos_y][king_pos_x] = None
            king_pos_dict[self.color] = (king_pos_y, king_pos_x - 2)
            board[king_pos_y][rook_x + 3] = rook
            board[king_pos_y][rook_x] = None
        return board


board = Board(RANKS, FILES, RECT_WIDTH, RECT_HEIGHT)
board.draw_board()
actual_board = board.make_board(RANKS, FILES)
fake_board = [row[:] for row in actual_board]
board.draw_pieces(actual_board)

drag = False
clock = pygame.time.Clock()
while 1:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            previous_x, previous_y = x // 100, y // 100
            current_piece = actual_board[previous_y][previous_x]
            drag = True
            current_piece.active = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            new_x, new_y = x // 100, y // 100
            check = board.is_checked(actual_board)[0]
            # check if the pieces are king and rook and it is not in check
            if (
                isinstance(actual_board[previous_y][previous_x], King)
                and isinstance(actual_board[new_y][new_x], Rook)
                and not check
            ):
                if new_x == 7:
                    # short castle
                    short_castle_board = current_piece.short_castle(
                        actual_board, board.move_color, new_x
                    )
                    actual_board = [row[:] for row in short_castle_board]
                    board.redraw_board()
                    drag = False
                if new_x == 0:
                    # long_castle
                    long_castle_board = current_piece.long_castle(
                        actual_board, board.move_color, new_x
                    )
                    actual_board = [row[:] for row in long_castle_board]
                    board.redraw_board()
                    drag = False
            elif current_piece != None:
                if board.move_color == current_piece.color and (
                    new_y,
                    new_x,
                ) in current_piece.generated_valid_move(
                    previous_y, previous_x, fake_board
                ):
                    # play move on fake board to verify it is valid
                    fake_board[new_y][new_x] = current_piece
                    fake_board[previous_y][previous_x] = None
                    if isinstance(current_piece, Pawn):
                        current_piece.first_move = False
                    if isinstance(current_piece, King):
                        king_pos_dict[current_piece.color] = (new_y, new_x)
                        current_piece.has_moved = True
                    if isinstance(current_piece, Rook):
                        current_piece.has_moved = True
                    is_check, king_color, piece_moves, piece_y_x = board.is_checked(
                        fake_board
                    )
                    # check if king is in check
                    if is_check:
                        # if the king that is checked has the same color and the piece that moved, then it's an invalid move
                        if king_color == board.move_color:
                            # reset the board and continue
                            current_piece.active = False
                            current_piece.drag = False
                            drag = False
                            board.redraw_board()
                            fake_board = [row[:] for row in actual_board]
                            continue
                        # check if it is checkmated
                        board.move_color = move_color_dict[current_piece.color]
                        king_y, king_x = king_pos_dict[board.move_color]
                        king_moves = fake_board[king_y][king_x].generated_valid_move(
                            king_y, king_x, fake_board
                        )
                        if board.is_checkmated(
                            king_color, piece_moves, king_moves, piece_y_x
                        ):
                            # play the moves on the actual board
                            actual_board[new_y][new_x] = current_piece
                            actual_board[previous_y][previous_x] = None
                            board.redraw_board()
                            print(f"{king_color} is checkmated")
                            sys.exit()
                    # play move on actual board
                    current_piece.active = False
                    actual_board[new_y][new_x] = current_piece
                    actual_board[previous_y][previous_x] = None
                    board.move_color = move_color_dict[current_piece.color]
                    board.redraw_board()
                    fake_board = [row[:] for row in actual_board]
                    drag = False
                else:
                    current_piece.active = False
                    current_piece.drag = False
                    drag = False
                    board.redraw_board()
        elif drag and current_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            board.redraw_board()
            screen.blit(current_piece.image, [mouse_x - 50, mouse_y - 50])
        pygame.display.update()
