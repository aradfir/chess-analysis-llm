from flask import Flask, render_template, request, jsonify, session
import chess
import chess.engine
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session handling

stockfish = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
stockfish.configure({"Threads": 8})
empty_board = chess.Board()

last_eval = stockfish.analyse(empty_board, chess.engine.Limit(depth=20))

num_variations = 3
depth_limit = 20



def get_board():
    if "board_fen" not in session:
        session["board_fen"] = chess.Board().fen()
    return chess.Board(session["board_fen"])

@app.route("/")
def index():
    board = get_board()
    return render_template("index.html", fen=board.fen())

def handle_mate_score(pov_score: chess.engine.PovScore):
    if not pov_score.is_mate():
        return None
    mate_num = pov_score.white().mate()
    mate_num = abs(mate_num)
    # the mate_num is in the pov of the player who's turn it is
    is_white_turn = pov_score.turn == chess.WHITE

    if is_white_turn:
        if pov_score.white().mate() > 0:
            return f"MW{mate_num}"
        else:
            return f"MB{mate_num}"
    else:
        if pov_score.black().mate() > 0:
            return f"MB{mate_num}"
        else:
            return f"MW{mate_num}"



@app.route("/move", methods=["POST"])
def move():
    print("Move")
    try:
        data = request.get_json()
    except Exception as e:
        data = request.form
        print(e)
    print(data)
    source = data["from"]
    target = data["to"]
    fen = data["fen"]
    board = chess.Board(fen)
    analysed_variations = stockfish.analyse(
        board,
        limit=chess.engine.Limit(depth=depth_limit),
        multipv=num_variations
        )
    best_move = analysed_variations[0]["pv"][0]
    best_move_piece = board.piece_at(best_move.from_square)
    best_move_san = board.san(best_move)  # Standard Algebraic Notation
    # Iterate over the variations
    variations = []
    
    for idx, variation in enumerate(analysed_variations):
        print(variation.keys())
        pov_score: chess.engine.PovScore = variation["score"]
        pov_wdl: chess.engine.PovWdl = pov_score.wdl()
        var_dict = {
                "best_move": variation["pv"][0].uci(),
        }

        if not pov_score.is_mate():
            var_dict["score"] = pov_score.white().score()/100
        else:
            var_dict["score"] = handle_mate_score(pov_score)

        if pov_wdl.white().winning_chance():
            wdl_dict = {
                "wdl_white": f"{pov_wdl.white().winning_chance() * 100}%",
                "wdl_black": f"{pov_wdl.black().winning_chance() * 100}%",
                "wdl_draw": f"{pov_wdl.white().drawing_chance() * 100}%",
            }
        else:
            wdl_dict = {
                "wdl_white": "Novelty",
                "wdl_black": "Novelty",
                "wdl_draw": "Novelty",
            }
        var_dict.update(wdl_dict)
        # print(f"\nVariation {idx + 1} (Score: {variation['score']}):")
        board_copy = board.copy()
        line_moves_str = ""
        for move_made in variation["pv"]:
            piece = board_copy.piece_at(move_made.from_square)
            san = board_copy.san(move_made)  # Standard Algebraic Notation
            line_moves_str += f"{board_copy.fullmove_number}. {san} ({piece.unicode_symbol()}{move_made.uci()})"
            # print(f"{board_copy.fullmove_number}. {san} ({piece.symbol().upper()} from {move.uci()[:2]} to {move.uci()[2:]})")
            board_copy.push(move_made)
        var_dict["line"] = line_moves_str
        variations.append(var_dict)
    
    res_dict = {
        "best_move": best_move.uci(),
        "best_move_san": best_move_san,
        "best_move_piece": best_move_piece.unicode_symbol(),
        "variations": variations,
    }
    return jsonify(res_dict)

@app.route("/update_engine", methods=["POST"])
def update_engine():
    data = request.get_json()
    global num_variations, depth_limit
    num_variations = data["num_variations"]
    depth_limit = data["depth_limit"]
    return jsonify({"num_variations": num_variations, "depth_limit": depth_limit})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("board_fen", None)
    return jsonify({"fen": chess.Board().fen()})

if __name__ == "__main__":
    app.run(debug=True)
