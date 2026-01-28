# === app.py ===
from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'tic_tac_toe_secret_2026'

# Минимакс-алгоритм
def minimax(board, is_maximizing, ai_symbol, human_symbol):
    winner = check_winner(board)
    if winner == ai_symbol:
        return 1
    elif winner == human_symbol:
        return -1
    elif '' not in board:
        return 0  # ничья

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = ai_symbol
                score = minimax(board, False, ai_symbol, human_symbol)
                board[i] = ''
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = human_symbol
                score = minimax(board, True, ai_symbol, human_symbol)
                board[i] = ''
                best_score = min(score, best_score)
        return best_score

def ai_move(board, ai_symbol, human_symbol):
    best_score = -float('inf')
    best_move = None
    for i in range(9):
        if board[i] == '':
            board[i] = ai_symbol
            score = minimax(board, False, ai_symbol, human_symbol)
            board[i] = ''
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

def check_winner(board):
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for a,b,c in win_patterns:
        if board[a] == board[b] == board[c] and board[a] != '':
            return board[a]
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    data = request.get_json()
    mode = data.get('mode')  # '1p' или '2p'
    session['mode'] = mode
    session['board'] = [''] * 9
    session['current_player'] = 'X'
    session['game_over'] = False
    return jsonify({'status': 'ok'})

@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    cell_index = data['cell']
    board = session['board']

    if session['game_over']:
        return jsonify({'error': 'Игра завершена'})

    if board[cell_index] != '':
        return jsonify({'error': 'Ячейка занята'})

    # Ход игрока
    board[cell_index] = session['current_player']
    session['board'] = board

    winner = check_winner(board)
    if winner:
        session['game_over'] = True
        return jsonify({
            'status': 'win',
            'winner': winner,
            'board': board
        })

    if '' not in board:
        session['game_over'] = True
        return jsonify({
            'status': 'draw',
            'board': board
        })

    # Если режим "1 игрок" и сейчас ходил человек (X), то делаем ход AI (O)
    if session['mode'] == '1p' and session['current_player'] == 'X':
        ai_cell = ai_move(board, 'O', 'X')
        if ai_cell is not None:
            board[ai_cell] = 'O'
            session['board'] = board

            # Проверка после хода AI
            winner = check_winner(board)
            if winner:
                session['game_over'] = True
                return jsonify({
                    'status': 'win',
                    'winner': winner,
                    'board': board,
                    'ai_move': ai_cell
                })

            if '' not in board:
                session['game_over'] = True
                return jsonify({
                    'status': 'draw',
                    'board': board,
                    'ai_move': ai_cell
                })

            # После хода AI — снова очередь X
            session['current_player'] = 'X'
            return jsonify({
                'status': 'continue',
                'board': board,
                'ai_move': ai_cell
            })
    else:
        # Режим 2 игроков: просто меняем ход
        session['current_player'] = 'O' if session['current_player'] == 'X' else 'X'
        return jsonify({
            'status': 'continue',
            'board': board,
            'current_player': session['current_player']
        })

    # На случай, если что-то пошло не так
    return jsonify({'error': 'Неизвестная ошибка'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)