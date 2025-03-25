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


num = 0

def mock_get_commentary(old_analysis, latest_analysis):
    global num
    time.sleep(2)
    num += 1
    return f"Commentary {num}"