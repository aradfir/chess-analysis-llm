import json
from flask import Flask, Response, render_template, request, jsonify, session, stream_with_context
import chess
import chess.engine
import os

import chess_analysis
import llm_integration

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session handling


num_variations = 3
depth_limit = 20

latest_analysis:dict = None
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
    last_san = data["last_san"]
    if last_san == "":
        # board was reset or FEN was loaded
        last_san = None
        old_analysis = None
    if latest_analysis is not None:
        old_analysis = latest_analysis.copy()
        old_analysis.pop("variations", None)
    else:
        old_analysis = None
    
    # remove variations from old analysis to avoid confusion
    
    print("DEPTHLIMIT", depth_limit)
    print("NUMVARIATIONS", num_variations)
    res_dict, latest_analysis  = chess_analysis.analyze_board(fen, depth_limit, num_variations, last_san)
    return jsonify(res_dict)


@app.route("/generate_commentary", methods=["GET"])
def generate_commentary():
    global latest_analysis
    if latest_analysis is None:
        return jsonify({"commentary": "No analysis available."})
    
    # Get streaming response
    response_stream = llm_integration.get_commentary(old_analysis, latest_analysis)
    
    def generate():
        # Initialize an empty string to accumulate the response
        commentary_text = ""
        
        try:
            # Iterate through the streaming response
            for chunk in response_stream:
                # Add new content to the accumulated text
                new_content = chunk['response']
                commentary_text += new_content
                
                # Yield the current accumulated text as a server-sent event
                yield f"data: {json.dumps({'commentary': commentary_text})}\n\n"
                
            # Send a final message to signal completion
            yield f"data: {json.dumps({'commentary': commentary_text, 'complete': True})}\n\n"
        except Exception as e:
            print(f"Error in commentary stream: {e}")
            # Send error information in the stream
            yield f"data: {json.dumps({'commentary': commentary_text, 'error': str(e), 'complete': True})}\n\n"
    
    # Return a streaming response
    return Response(stream_with_context(generate()), 
                   content_type='text/event-stream')

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
