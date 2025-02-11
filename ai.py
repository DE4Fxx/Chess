import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch
import chess
import requests
import re


FC1 = (64,512)
FC2 = (512,256)
FC3 = (256,256)
FC4 = (256,128)
FC5 = (128,1)


piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000  # King is the most valuable
}


CHESS_AI_PATH = "models/"

class ChessAI(nn.Module):
    def __init__(self,color):
        super(ChessAI,self).__init__()
        self.fc1 = nn.Linear(FC1[0],FC1[1])
        self.fc2 = nn.Linear(FC2[0],FC2[1])
        self.fc3 = nn.Linear(FC3[0],FC3[1])
        self.fc4 = nn.Linear(FC4[0],FC4[1])
        self.fc5 = nn.Linear(FC5[0],FC5[1])
        self.opposing = chess.WHITE if color == chess.BLACK else chess.BLACK
        self.transposition_table = {}
        self.activation = nn.ReLU()


    def forward(self,x):
        print("Computing...")
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.activation(self.fc3(x))
        x = self.activation(self.fc4(x))
        x = self.fc5(x)
        return x


    # Simple evaluation function
    def evaluate_board(self,board:chess.Board):
        """Evaluate the board: Positive for White, Negative for Black."""
        score = 0
        for square, piece in board.piece_map().items():
            value = piece_value.get(piece.piece_type, 0)
            score += value if piece.color == self.opposing else -value
        return score


    def minimax(self, board:chess.Board, alpha, beta, maximizing_player, depth=1):
        """Minimax with transposition table to prevent looping moves."""
        board_hash = hash(board.fen())  # Unique position ID

        if depth == 0 or board.is_game_over():
            score = self.evaluate_board(board)
            return score

        legal_moves = self.order_moves(board)

        if maximizing_player:
            max_eval = -float('inf')
            for move in legal_moves:
                board.push(move)
                eval = self.minimax(board, alpha, beta, False, depth - 1)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval = self.minimax(board, alpha, beta, True, depth - 1)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def order_moves(self,board):
        move_scores = []
        for move in board.legal_moves:
            board.push(move)
            score = self(board_rep(board).unsqueeze(0)).item()
            move_scores.append((move, score))
            board.pop()
        
        move_scores.sort(key=lambda x: x[1], reverse=True)  # Highest scores first
        return [move[0] for move in move_scores]
    
    def save(self):
        num = 0
        with open("ai.txt","r") as f:
            num = f.read()
            if num == '':
                num = 1
            num = int(num)
        with open("ai.txt","w") as f:
            f.write(str(num + 1))
        torch.save(self.state_dict(), CHESS_AI_PATH+f"model{num}")
        print("Save successful...")
        return num
        

    def get_best_move(self,board:chess.Board,color,depth = 2):
        """Find the best move using Minimax with Alpha-Beta Pruning."""
        best_move = None
        max_eval = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for move in board.legal_moves:
            board.push(move)
            eval = self.minimax(board, alpha, beta, True,depth - 1)
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move  # Store best move

        return best_move



def board_rep(board:chess.Board):
    ''' Converts the board into something the neural network can understand '''
    board_matrix = np.zeros((8,8),dtype=int)
    piece_map = board.piece_map()

    for square,piece in piece_map.items():
        row,col = divmod(square,8)
        board_matrix[row][col] = piece.piece_type * (1 if piece.color else -1)

    return torch.tensor(board_matrix,dtype=torch.float32).flatten()

def get_stockfish_opinion(board:chess.Board):
    url = "https://stockfish.online/api/s/v2.php"
    raw = requests.get(url,params={"fen":board.fen(),"depth":1})
    json = raw.json()
    move = json["bestmove"]
    move_string = re.match(r"bestmove ([a-z]{1}\d{1}[a-z]{1}\d{1})",move).group(1)
    return move_string
    


def train(board):
    model = ChessAI()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    for epoch in range(100):
        optimizer.zero_grad()
        inputs = board_rep(board).unsqueeze(0)
        target = torch.tensor(get_stockfish_opinion(board), dtype=torch.float32)
        output = model(inputs)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

    model.save()



def main():
    i = 0
    model = ChessAI()
    board = chess.Board()

    while i < 10000:
        if board.legal_moves:
            stockfish = get_stockfish_opinion(board)
            print("Stockfish move: " + stockfish)
            board.push(chess.Move.from_uci(stockfish))
            my_ai = model.get_best_move(board,3,chess.BLACK)
            print("My AI's move: ",my_ai)
            board.push(my_ai)
        else:
            board = chess.Board()
            continue



if __name__ == "__main__":
    main()
    