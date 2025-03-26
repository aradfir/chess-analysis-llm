

import chess
import chess.engine

stockfish = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
stockfish.configure({"Threads": 8})
empty_board = chess.Board()

last_eval = stockfish.analyse(empty_board, chess.engine.Limit(depth=20))

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

def get_game_stage(board: chess.Board):
    # check if the game is in the opening stage, middle game stage or end game stage
    # Basically the late game starts when there are 6 or fewer major or minor pieces, and the midgame starts when there are 10 or fewer major or minors OR the back rank is sparse OR the white and black pieces are sufficiently mixed on the board.

    # Major pieces are the queen and rooks
    # Minor pieces are the bishops and knights
    # Pawns are not considered major or minor pieces
    major_pieces = 0
    minor_pieces = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        if piece.piece_type == chess.PAWN:
            continue
        if piece.piece_type == chess.QUEEN or piece.piece_type == chess.ROOK:
            major_pieces += 1
        else:
            minor_pieces += 1
    if major_pieces + minor_pieces <= 6:
        return "late"
    if major_pieces + minor_pieces <= 10 or board.is_check():
        return "middle"
    return "opening"


def analyze_board(fen, depth_limit, num_variations, last_move):
    # last_move_source = last_move[0]
    # last_move_target = last_move[1]
    board = chess.Board(fen)
    analysed_variations = stockfish.analyse(
        board,
        limit=chess.engine.Limit(depth=depth_limit),
        multipv=num_variations
        )
    
    last_move_san = last_move
    last_move_turn = "New Game"
    if last_move != "":
        last_move_turn = "White" if board.turn == chess.BLACK else "Black"

    best_move = analysed_variations[0]["pv"][0]
    best_move_piece = board.piece_at(best_move.from_square)
    best_move_san = board.san(best_move)  # Standard Algebraic Notation
    # Iterate over the variations
    variations = []
    prompt_variations = []
    
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
        prompt_var_dict = var_dict.copy()
        if pov_wdl.white().winning_chance() or pov_wdl.white().losing_chance():
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
        
        line_moves = []
        for move_made in variation["pv"]:
            piece = board_copy.piece_at(move_made.from_square)
            san = board_copy.san(move_made)  # Standard Algebraic Notation
            line_moves.append(f"{board_copy.fullmove_number}. {san} ({piece.unicode_symbol()}{move_made.uci()})")
            
            # print(f"{board_copy.fullmove_number}. {san} ({piece.symbol().upper()} from {move.uci()[:2]} to {move.uci()[2:]})")
            board_copy.push(move_made)
        var_dict["line"] = " ".join(line_moves)
        prompt_var_dict["line"] = " ".join(line_moves[:5])
        variations.append(var_dict)
        prompt_variations.append(prompt_var_dict)
    
    frontend_dict = {
        "best_move": best_move.uci(),
        "best_move_san": best_move_san,
        "best_move_piece": best_move_piece.unicode_symbol(),
        "variations": variations,
    }
    
    analysis_dict = {
        "best next move": best_move.uci(),
        "best next move San": best_move_san,
        "best next move Piece": chess.piece_name(best_move_piece.piece_type),
        "current turn": "White" if board.turn == chess.WHITE else "Black",
        "latest move": last_move_san,
        "latest move done by": last_move_turn,
        "FEN": board.fen(),
        "Board Representation": str(board),
        "Current Score": variations[0]["score"],
        "variations": prompt_variations,
        "game stage": get_game_stage(board),
        "check": board.is_check(),
        "move number": board.fullmove_number,
    }



    return frontend_dict, analysis_dict