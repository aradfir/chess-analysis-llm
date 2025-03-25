from flask import Flask, render_template, request, jsonify, session
import chess
import chess.engine
import os

import chess_analysis
import llm_integration

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session handling


num_variations = 3
depth_limit = 20

latest_analysis = None
old_analysis = None


def get_board():
    if "board_fen" not in session:
        session["board_fen"] = chess.Board().fen()
    return chess.Board(session["board_fen"])

@app.route("/")
def index():
    board = get_board()
    return render_template("index.html", fen=board.fen())



@app.route("/move", methods=["POST"])
def move():
    global old_analysis, latest_analysis, num_variations, depth_limit
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
    old_analysis = latest_analysis
    print("DEPTHLIMIT", depth_limit)
    print("NUMVARIATIONS", num_variations)
    res_dict, latest_analysis  = chess_analysis.analyze_board(fen, depth_limit, num_variations)
    return jsonify(res_dict)

@app.route("/generate_commentary", methods=["GET"])
def generate_commentary():
    global latest_analysis
    if latest_analysis is None:
        return jsonify({"commentary": "No analysis available."})
    return jsonify({"commentary": llm_integration.mock_get_commentary(old_analysis, latest_analysis)})

@app.route("/update_engine", methods=["POST"])
def update_engine():
    data = request.get_json()
    global num_variations, depth_limit
    num_variations = data["num_variations"]
    depth_limit = data["depth_limit"]
    print("NUMVARIATIONS SET", num_variations)
    print("DEPTHLIMIT SET", depth_limit)
    return jsonify({"num_variations": num_variations, "depth_limit": depth_limit})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("board_fen", None)
    return jsonify({"fen": chess.Board().fen()})

if __name__ == "__main__":
    app.run(debug=True)
