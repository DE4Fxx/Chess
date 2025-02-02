import time
from board import *
import requests
import chess
import warnings
import re
import json
import random



# This engine is for the stockfish engine which is downloadable at https://stockfishchess.org/download/windows/



warnings.simplefilter("ignore")


import pygame
from pygame.locals import QUIT

# Initialize pygame
pygame.init()


WHITE_GRAVEYARD_POS = (600, 0)  
BLACK_GRAVEYARD_POS = (600, 200)  
GRAY = (192, 192, 192)
GRAVEYARD_WIDTH = 200
GRAVEYARD_HEIGHT = 400
SQUARE_SIZE = 60  

BUTTON_COLOR =  (0, 0, 0)  # Black
HOVER_COLOR = (255, 255, 255)  # White
TEXT_COLOR = (128, 0, 128)  # Purple

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

SQUARE_WIDTH = 600 // 8
SQUARE_HEIGHT = 600 // 8
AI_DELAY = 0.1


# Colors
BLACK = (0, 0, 0)

def draw_button(screen, text, x, y, w, h, active_color, inactive_color):
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()

    # Check if mouse is over the button
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if clicked[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    font = pygame.font.SysFont(None, 50)
    label = font.render(text, True, TEXT_COLOR)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))

    return False

def draw_graveyard(surface, captured_pieces, piece_size=(30,45)):
    image = pygame.image.load("assets/pixel chess/extras/graveyard2.jpg")
    image = pygame.transform.scale(image,(GRAVEYARD_WIDTH, GRAVEYARD_HEIGHT))
    piece_width, piece_height = piece_size
    pieces_per_row = GRAVEYARD_WIDTH // piece_width
    max_pieces_column = GRAVEYARD_HEIGHT // piece_height

    # Define the padding or spacing between pieces if you want
    x_padding = 2.5
    y_padding = 2.5

    # Clear the graveyard area with a background color for white and black captured pieces
    surface.blit(image,(WHITE_GRAVEYARD_POS[0], WHITE_GRAVEYARD_POS[1]))
    surface.blit(image,(BLACK_GRAVEYARD_POS[0], BLACK_GRAVEYARD_POS[1]))

    # Draw captured white pieces
    white_pieces = captured_pieces['white']
    for i, piece in enumerate(white_pieces):
        row = i // pieces_per_row
        col = i % pieces_per_row
        if row < max_pieces_column:  # Ensure we do not draw beyond the graveyard's limits
            x = WHITE_GRAVEYARD_POS[0] + col * (piece_width + x_padding) + x_padding
            y = WHITE_GRAVEYARD_POS[1] + row * (piece_height + y_padding) + y_padding
            piece_image = pygame.image.load(piece.image())
            piece_image = pygame.transform.scale(piece_image,piece_size)
            surface.blit(piece_image, (x, y))

    # Draw captured black pieces
    black_pieces = captured_pieces['black']
    for i, piece in enumerate(black_pieces):
        row = i // pieces_per_row
        col = i % pieces_per_row
        if row < max_pieces_column:  
            x = BLACK_GRAVEYARD_POS[0] + col * (piece_width + x_padding) + x_padding
            y = BLACK_GRAVEYARD_POS[1] + row * (piece_height + y_padding) + y_padding + GRAVEYARD_HEIGHT // 2
            piece_image = pygame.image.load(piece.image())
            piece_image = pygame.transform.scale(piece_image,piece_size)
            surface.blit(piece_image, (x, y))

def checkmate(screen, board):

    # Find out who won

    outcome = board.outcome()

    winner = outcome.winner

    if winner == chess.WHITE:
        end_game(screen,"white")
    elif winner == chess.BLACK:
        end_game(screen,"black")

def start_screen():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess Game")

    mode = None
    player_color= None
    choosing_mode = True
    color_selected = False
    
    
    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

        if choosing_mode:
            play_player = draw_button(screen, "Play against Player", 250, 250, 350, 100, HOVER_COLOR, BUTTON_COLOR)
            play_ai = draw_button(screen, "Play against AI", 250, 400, 300, 100, HOVER_COLOR, BUTTON_COLOR)
            ai_v_ai = draw_button(screen, "AI vs AI", 250, 550, 300, 100, HOVER_COLOR, BUTTON_COLOR)
            if play_player:
                mode = "player"
                choosing_mode = False
            elif play_ai:
                mode = "ai"
                choosing_mode = False
            elif ai_v_ai:
                mode = "aivai"
                choosing_mode = False
        elif(mode == "ai"):
            if not color_selected:
                black = draw_button(screen, "Black", 250, 250, 300, 100, HOVER_COLOR, BUTTON_COLOR)
                white = draw_button(screen, "White", 250, 400, 300, 100, HOVER_COLOR, BUTTON_COLOR)

                if black:
                    player_color = "black"
                    color_selected = True
                elif white:
                    player_color = "white"
                    color_selected = True
            else:
                break
        else:
            break

    
        pygame.display.flip()
        if not choosing_mode:
            time.sleep(0.2)
    return mode, player_color


def draw_pieces(screen, board):
    """Draw the chess pieces on the board."""
    square_width = 75
    square_height = 75


    for row in ROWS:
        for col in COLS:
            square = board.get_square(f"{col}{row}")
            piece = square.get_piece()
            if piece:  # If there's a piece on the square
                piece_image = pygame.image.load(piece.image())
                piece_image = pygame.transform.scale(piece_image, (square_width,square_height))
                x = COLS.index(col) * square_width -5
                y = ROWS.index(row) * square_height -10
                screen.blit(piece_image, (x, y))

def aithinking(screen,font,color):
    text = font.render("Ai is thinking...",False,color)
    screen.blit(text,(100,700))
    pygame.display.flip()
    time.sleep(0.1)
    surface = pygame.Surface((200,100))
    surface.fill(BLACK)
    screen.blit(surface,(100,700))


def highlight_move_destination(screen, board,legal_moves, selected_piece, highlight_color, SQUARE_SIZE):
    if not legal_moves or not selected_piece:
        return
    # Create a transparent surface to overlay for highlighting
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    highlight_surface.set_alpha(128)  # Semi-transparent
    highlight_surface.fill(highlight_color)

    # Determine the original square of the selected piece

    for move in legal_moves:
        move = str(move)
        # Extract the destination square from the move string

        # Calculate the position to highlight on the screen
        # The y-position is adjusted by subtracting 1 from the row because Pygame's grid starts at 0,0 at the top-left
        highlight_pos = (get_square_at_mouse_click(screen,SQUARE_SIZE))

        # Blit the highlight surface onto the screen at the calculated position
        screen.blit(highlight_surface, highlight_pos)


    # Update the display to show the new highlights
    pygame.display.flip()

def get_square_at_mouse_click(board_rect, SQUARE_SIZE):
    mouse_pos = pygame.mouse.get_pos()
    board_rect = pygame.Rect(0, 0, SCREEN_WIDTH,SCREEN_HEIGHT)

    if board_rect.collidepoint(mouse_pos):
        # Calculate the row and column number based on the mouse position.
        column = (mouse_pos[0] - board_rect.left) // SQUARE_SIZE
        row = (mouse_pos[1] - board_rect.top) // SQUARE_SIZE
        return row, column
    else:
        return None

def end_game(screen, winner):
    # Display a message on the screen
    font = pygame.font.Font(None, 36)
    if winner == 'white':
        text = font.render("Checkmate! White wins!", True, (255, 255, 255))
    elif winner == 'black':
        text = font.render("Checkmate! Black wins!", True, (255, 255, 255))
    else:
        text = font.render("Stalemate! It's a draw.", True, (255, 255, 255))

    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()

def main():
    time_since_last_ai_move = 0
    engine = None
    engine2 = None
    chosen = None
    player = None
    # Hold AI's move
    best_move = None
    board = Board()
    checker_board = chess.Board()
    board.initialize_pieces()
    clock = pygame.time.Clock()

    # Show the start screen
    mode,player = start_screen()
    
    if player == "black":
        chosen = chess.BLACK
    else:
        chosen = chess.WHITE

    if mode == "aivai":
        colors = [chess.WHITE, chess.BLACK]
        engine = colors[random.randint(0,1)]
        if engine == chess.WHITE:
            engine2 = colors[1]
        else:
            engine2 = colors[0]


    if mode is None:
        # That just means the user closed the window
        pygame.quit()
        return
    


    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess")

    turn_display_surface = pygame.Surface((200, 200))


    # Hold pieces if they are selected
    selected_piece = None
    selected_square = None
    highlight_color = (255, 255, 0)  # Yellow for highlighting
    from_square = None
    to_square = None




    x = (SCREEN_WIDTH - 200) // 2

    y = 600





    WHITE_TURN_COLOR = (255, 255, 255)  # white color
    BLACK_TURN_COLOR = (0, 0, 0)  # black color
    FONT_COLOR = (128, 0, 128) # purple color
    font = pygame.font.SysFont(None, 36)


    # Load the chessboard background

    
    chessboard_background = pygame.image.load(board.image())

    chessboard_background = pygame.transform.scale(chessboard_background,(600+20, 600))

    # game loop

    captured = None

    captured_pieces = {
        "white" : board.get_captured_pieces("W"),
        "black" : board.get_captured_pieces("B")
    }

    running = True
    while running:



        if checker_board.turn == chess.WHITE:
            turn_display_surface.fill(WHITE_TURN_COLOR)
            text = font.render("White's Turn", True, FONT_COLOR)
        else:
            turn_display_surface.fill(BLACK_TURN_COLOR)
            text = font.render("Black's Turn", True, FONT_COLOR)

        if checker_board.is_game_over():
            outcome = checker_board.outcome()
            if outcome.winner == chess.WHITE:
                end_game(screen,"white")
            elif outcome.winner == chess.BLACK:
                end_game(screen,"black")

        # position the text to be center of the surface
        text_rect = text.get_rect(center=(100, 100))
        turn_display_surface.blit(text, text_rect)
        if mode == "player" or mode == "ai":
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # find the clicked square
                    col = event.pos[0] // SQUARE_WIDTH
                    row = event.pos[1] // SQUARE_HEIGHT
                    selected_square = board.get_square(f"{COLS[col]}{ROWS[row]}")
                    selected_piece = selected_square.get_piece()
                    legal_moves = checker_board.legal_moves              

                if event.type == pygame.MOUSEBUTTONUP and selected_piece:
                    col = event.pos[0] // SQUARE_WIDTH
                    row = event.pos[1] // SQUARE_HEIGHT
                    target_square = board.get_square(f"{COLS[col]}{ROWS[row]}")
                    
                    # validate squares
                    if target_square != selected_square:
                        move_uci = f"{selected_square.get_position().lower()}{target_square.get_position().lower()}"
                        
                        # validate move
                        if chess.Move.from_uci(move_uci) in checker_board.legal_moves:
                            checker_board.push(chess.Move.from_uci(move_uci))
                            
                            # update
                            captured = target_square.move_piece()
                            selected_square.move_piece()  
                            target_square.set_piece(selected_piece) 
                            selected_piece = None  
                            
                            # Update selected_square after a successful move
                            selected_square = target_square


                            if captured:
                                captured_piece = captured
                                board.capture_piece(captured_piece)                            
                    else:
                        selected_piece = None
                        
                elif mode == "ai" and checker_board.turn != chosen:
                    aithinking(screen, font, FONT_COLOR)
                    fen = checker_board.fen()
                    print(fen)
                    request = requests.get("https://stockfish.online/api/s/v2.php",params={"fen":fen,"depth":1})
                    print(request)
                    json_dict = request.json()
                    print(json_dict)
                    best_moves = json_dict["bestmove"]
                    best_move = best_moves.split(" ")[1]
                    best_move = chess.Move.from_uci(best_move)
                    print(best_move)
                    legal_moves = list(checker_board.legal_moves)
                    if legal_moves:
                        checker_board.push(best_move)
                        from_square = board.get_square(best_move.uci()[:2].upper())
                        to_square = board.get_square(best_move.uci()[2:].upper())
                        captured = to_square.get_piece()
                        piece = from_square.move_piece()
                        to_square.set_piece(piece)

                        if captured:
                            captured_piece = captured
                            board.capture_piece(captured_piece)
                        selected_square = from_square
                    else:
                        checkmate(screen)

                    # Introduce a delay between AI moves
                    time.sleep(1)
        elif mode == "aivai":
            dt = clock.get_time() / 1000
            time_since_last_ai_move += dt
            legal_moves = list(checker_board.legal_moves)
            fen = checker_board.fen()
            if checker_board.turn == engine and time_since_last_ai_move >= AI_DELAY:
                print("engine") 
                print("get_time:",clock.get_time())
                aithinking(screen,font,FONT_COLOR)
                print(fen)
                request = requests.get("https://stockfish.online/api/s/v2.php",params={"fen":fen,"depth":1})
                json_dict = request.json()
                best_moves = json_dict["bestmove"]
                best_move = best_moves.split(" ")[1]
                best_move = chess.Move.from_uci(best_move)
                print(best_move)
                if legal_moves:
                    checker_board.push(best_move)
                    from_square = board.get_square(best_move.uci()[:2].upper())
                    to_square = board.get_square(best_move.uci()[2:].upper())
                    captured = to_square.move_piece()
                    piece = from_square.move_piece()
                    to_square.set_piece(piece)
                    selected_square = from_square
                    if captured:
                        captured_piece = captured
                        board.capture_piece(captured_piece)
                    time_since_last_ai_move = 0
                else:
                    checkmate(screen,checker_board)
                

            elif checker_board.turn == engine2 and time_since_last_ai_move >= AI_DELAY:
                print("engine 2")
                print("get_time:",clock.get_time())
                aithinking(screen,font,FONT_COLOR)
                print(fen)
                request = requests.get("https://stockfish.online/api/s/v2.php",params={"fen":fen,"depth":1})
                json_dict = request.json()
                best_moves = json_dict["bestmove"]
                best_move = best_moves.split(" ")[1]
                best_move = chess.Move.from_uci(best_move)
                print(best_move)
                if legal_moves:
                    checker_board.push(best_move)
                    from_square = board.get_square(best_move.uci()[:2].upper())
                    to_square = board.get_square(best_move.uci()[2:].upper())
                    captured = to_square.move_piece()
                    piece = from_square.move_piece()
                    to_square.set_piece(piece)
                    selected_square = from_square
                    if captured:
                        captured_piece = captured
                        board.capture_piece(captured_piece)
                    time_since_last_ai_move = 0
                else:
                    checkmate(screen,checker_board)



        #  background
        screen.blit(chessboard_background,(-10,1))
        screen.blit(turn_display_surface, (x, y))
        draw_graveyard(screen,captured_pieces)
        draw_pieces(screen,board)
        if selected_square:
            if checker_board.turn == chess.WHITE:
                highlight_color = (0,0,0)
            else:
                highlight_color = (255,255,255)
            if from_square and to_square:
                pygame.draw.rect(screen, highlight_color, 
                                (COLS.index(from_square.get_position()[0]) * SQUARE_WIDTH,
                                (int(from_square.get_position()[1])-1) * SQUARE_HEIGHT, 
                                SQUARE_WIDTH, SQUARE_HEIGHT), 3)  # 3 pixels wide border

                pygame.draw.rect(screen, highlight_color, 
                (COLS.index(to_square.get_position()[0]) * SQUARE_WIDTH,
                (int(to_square.get_position()[1])-1) * SQUARE_HEIGHT, 
                SQUARE_WIDTH, SQUARE_HEIGHT), 3)
        # if selected_piece:
            # highlight_move_destination(screen,board,checker_board.legal_moves,selected_square,highlight_color,SQUARE_SIZE)
        draw_graveyard(screen,captured_pieces)

        # refresh
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()