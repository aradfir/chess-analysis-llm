# # import chess
# # import chess.engine

# # curr_board = chess.Board()
# # stockfish = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
# # stockfish.configure({"Threads": 4})
# # # res = stockfish.analyse(curr_board, chess.engine.Limit(time=0.4))

# # analysed_variations = stockfish.analyse(chess.Board(), limit=chess.engine.Limit(depth=20), multipv=5)

# # for variation in analysed_variations:
# #     print(variation["score"])
# #     print(variation["pv"])
# #     print(variation)
# #     print("\n\n\n\n\n\n")
# # top_five_moves = [variation["pv"][0] for variation in analysed_variations]
# # # print(top_five_moves[0].drop)
# # # top_five_mo
# # # res = engine.play(curr_board, chess.engine.Limit(time=0.1))
# # print(top_five_moves)


# import chess
# import chess.engine

# stockfish = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
# stockfish.configure({"Threads": 8})
# board = chess.Board("2q5/8/8/1r6/8/7k/K7/8 w - - 0 1")
# # board.push_san("Nf6+")
# # Get the top 5 variations at depth 20
# analysed_variations = stockfish.analyse(
#     board=board,
#     limit=chess.engine.Limit(depth=20),
#     multipv=5
# )
# pov_score = analysed_variations[0]["score"]
# print(pov_score)
# if pov_score.is_mate():
#     print(f"Checkmate in {abs(pov_score.white().mate())} moves.")

# if pov_score.is_mate():
#     print(f"Checkmate in {abs(pov_score.black().score())} moves.")



# if pov_score.is_mate():
#     print(f"Checkmate in {abs(pov_score.black().mate())} moves.")
# print(pov_score.white().score())
# # Iterate over the variations
# for idx, variation in enumerate(analysed_variations):
#     print(f"\nVariation {idx + 1} (Score: {variation['score']}):")
#     board_copy = board.copy()
#     for move in variation["pv"]:
#         print(move)
#         piece = board_copy.piece_at(move.from_square)
#         san = board_copy.san(move)  # Standard Algebraic Notation
#         print(f"{board_copy.fullmove_number}. {san} ({piece.symbol().upper()} from {move.uci()[:2]} to {move.uci()[2:]})")
#         board_copy.push(move)



# def mock_get_commentary():
#     sleep(2)

import time

import ollama
num = 0


def get_prompt(old_analysis, latest_analysis):
    return f"""
    You are a chess expert who is a caster, commentator and analyst.
    You have to provide analysis on the latest move, as well as the ongoing position.
    You are given the position as an ascii representation,
    where the pieces are represented by their standard algebraic notation letters (e.g., K for king, Q for queen, R for rook, B for bishop, N for knight, and P for pawn) and empty squares represented by dots.
    Upper case letters represent white pieces, and lower case letters represent black pieces.
    You are also provided who's turn it is, a chess engine's calculation of the best move, the best move piece, the current score, multiple lines of continuation, which are ordered by the best moves in order for the current player. Note that these continuations are not what has been played, but what the engine thinks is the best move and their followups.
    These lines also have the score of the position from the perspective of white in pawns, meaning a +1.5 means the position is 1.5 pawns better for white. The score of -1.5 would mean that the position is better for black with 1.5 pawn advantage.
    Sometimes the score is MWx or MBx, which means mate in x moves for white or black respectively.
    If the evaluation for the top line is very different from the second line, or the first line is the only one that keeps the advantage, this is called a critical position and you should mention that if that is the case.
    Use chess terms in your commentary in a way relevant to the position. Justify why the given continuations are good, and feel free the look at the moves later in the continuation.
    If the previous analysis's score is much different from the current one, mention that as well, as it could be a blunder.
    Note that the current score is always equal to the score of the first variation, as it is the best move; so no need to mention that.
    Note that you should compare the old analysis's best move, with the current analysis's latest move, as the latest move is what the player played.
    Current Analysis: {latest_analysis}\n
    ========================================\n
    Old analysis: {old_analysis}
    Respond only with your commentary, and no other information (such as "Lets dive into the position", "okay, Here is the commentary", the current board, etc) as this isnt the first position you are analyzing. Respond in a manner as if you're talking.
    Remember, the current turn is indicating who is to move and has NOT played yet, not the player who played the last move. and the best move is the one that engine thinks, not the one that was played.
    """
def get_commentary(old_analysis, latest_analysis):
    print("Getting commentary?")
    prompt = get_prompt(old_analysis, latest_analysis)
    print("Got prompt")
    print(prompt)
    
    # Use streaming option with ollama
    response_stream = ollama.generate(
        "gemma3:12b",
        prompt,
        stream=True
    )
    
    # Return the stream object instead of the final response
    return response_stream

def mock_get_commentary(old_analysis, latest_analysis):
    global num
    time.sleep(2)
    num += 1
    return f"Commentary {num}"