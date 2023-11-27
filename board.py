from square import *
from piece import *

COLS = ["A", "B", "C", "D", "E", "F", "G", "H"]
ROWS = [1, 2, 3, 4, 5, 6, 7, 8]

class Board:
    __slots__ = ["__imagefile", "__board", "captured_white", "captured_black"]

    def __init__(self):
        self.__board = []
        for y in range(8):
            row = (ROWS[y], [])
            for i in range(8):
                row[1].append(Square(f"{COLS[i]}{ROWS[y]}"))
            self.__board.append(row)
        self.__imagefile = "assets/pixel chess/extras/board3.png"
        self.captured_white = []
        self.captured_black = []


    def capture_piece(self, piece):
        """Stores the captured pieces."""
        if piece.color() == "W":
            self.captured_white.append(piece)
        else:
            self.captured_black.append(piece)

    def get_captured_pieces(self, color):
        """Returns the list of captured pieces based on color."""
        return self.captured_white if color == "W" else self.captured_black

    def image(self):
        return self.__imagefile
    def initialize_pieces(self, first_player = None):
        """Populate the board with initial chess pieces based on the first player."""
        second_player = "B" if first_player == "W" else "W"  # Determine the second player
        if first_player == None:
            first_player = "W"
            second_player = "B"

        # Pawns
        for col in COLS:
            self.get_square(f"{col}2").set_piece(Piece(first_player, "Pawn"))
            self.get_square(f"{col}7").set_piece(Piece(second_player, "Pawn"))

        # Rooks
        self.get_square("A1").set_piece(Piece(first_player, "Rook"))
        self.get_square("H1").set_piece(Piece(first_player, "Rook"))
        self.get_square("A8").set_piece(Piece(second_player, "Rook"))
        self.get_square("H8").set_piece(Piece(second_player, "Rook"))

        # Knights
        self.get_square("B1").set_piece(Piece(first_player, "Knight"))
        self.get_square("G1").set_piece(Piece(first_player, "Knight"))
        self.get_square("B8").set_piece(Piece(second_player, "Knight"))
        self.get_square("G8").set_piece(Piece(second_player, "Knight"))

        # Bishops
        self.get_square("C8").set_piece(Piece(second_player, "Bishop"))
        self.get_square("F8").set_piece(Piece(second_player, "Bishop"))
        self.get_square("C1").set_piece(Piece(first_player, "Bishop"))
        self.get_square("F1").set_piece(Piece(first_player, "Bishop"))

        # Kings and Queens
        self.get_square("E1").set_piece(Piece(first_player, "King"))
        self.get_square("D1").set_piece(Piece(first_player, "Queen"))
        self.get_square("E8").set_piece(Piece(second_player, "King"))
        self.get_square("D8").set_piece(Piece(second_player, "Queen"))



    def get_square(self, notation):
        """Returns the Square object based on chess notation."""
        col, row = notation[0], int(notation[1])
        return self.__board[ROWS.index(row)][1][COLS.index(col.upper())]


    def __str__(self):
        return_string = "  " + " ".join(COLS)
        for row in ROWS:
            return_string += f"\n{row} "
            for col in COLS:
                square = self.get_square(f"{col}{row}")
                piece = square.get_piece()
                piece_char = piece.get_type()[0] if piece else "."  # Using first char of piece type
                if piece:
                    if piece.get_type() == "king":
                        return_string += "kg" + " "
                    else:
                        return_string += piece_char + " "
                else:
                    return_string += piece_char + " "
        return return_string
    
def main():
    board = Board()
    board.initialize_pieces()
    print(board)

if __name__ == "__main__":
    main()

            

    