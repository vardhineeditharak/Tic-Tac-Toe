from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Game logic (server-side AI) ---
def check_winner(b):
    wins = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    )
    for a, c, d in wins:
        if b[a] and b[a] == b[c] == b[d]:
            return b[a]
    # tie when all cells are filled
    if all(b[i] for i in range(9)):
        return "Tie"
    return None

def random_move(b):
    empties = [i for i in range(9) if not b[i]]
    import random
    return random.choice(empties) if empties else None

def best_move_minimax(b, ai_player):
    opponent = 'O' if ai_player == 'X' else 'X'

    def minimax(board, depth, is_maximizing):
        winner = check_winner(board)
        if winner == ai_player:
            return 10 - depth
        if winner == opponent:
            return depth - 10
        if winner == "Tie":
            return 0

        if is_maximizing:
            best = -10**9
            for i in range(9):
                if not board[i]:
                    board[i] = ai_player
                    val = minimax(board, depth + 1, False)
                    board[i] = None
                    if val > best:
                        best = val
            return best
        else:
            best = 10**9
            for i in range(9):
                if not board[i]:
                    board[i] = opponent
                    val = minimax(board, depth + 1, True)
                    board[i] = None
                    if val < best:
                        best = val
            return best

    best_score = -10**9
    move = None
    for i in range(9):
        if not b[i]:
            b[i] = ai_player
            score = minimax(b, 0, False)
            b[i] = None
            if score > best_score:
                best_score = score
                move = i
    return move

def medium_move(b, ai_player):
    import random
    # 60% chance to pick minimax, 40% random
    if random.random() < 0.6:
        return best_move_minimax(b, ai_player)
    return random_move(b)

def compute_ai_move(board, ai_player, difficulty):
    # board: list of 9 elements or falsy entries
    if difficulty == 'easy':
        return random_move(board)
    elif difficulty == 'medium':
        return medium_move(board, ai_player)
    else:
        return best_move_minimax(board, ai_player)

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai_move', methods=['POST'])
def ai_move():
    data = request.get_json(force=True, silent=True) or {}
    board = data.get('board', [None] * 9)
    ai_player = data.get('ai_player', 'O')
    difficulty = data.get('difficulty', 'hard')

    # sanitize board: ensure length 9, convert values to 'X', 'O' or None
    sanitized = []
    for i in range(9):
        if i < len(board) and board[i] in ('X', 'O'):
            sanitized.append(board[i])
        else:
            sanitized.append(None)
    board = sanitized

    move = compute_ai_move(board, ai_player, difficulty)
    # return as integer or null
    return jsonify({'move': move})

if __name__ == '__main__':
    # debug turned on for development only
    app.run(debug=True)
