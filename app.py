import eel
import threading
import time
from CoreEngine import CoreEngine
from Games import Shooter as Shooter
from Games import KarateChop as KarateChop
import Games.BubbleCatcher as bubbleCatcher
import Games.RockPaperScissors as rockPaperScissors
import Features.Leaderboard as LB
import Games.MatchMeme as MatchMeme
import Games.AirCanvas as AirCanvas

eel.init('app')

# --- 1. CORE ENGINE SETUP ---
engine = CoreEngine()
engine_thread = threading.Thread(target=engine.run, daemon=True)
engine_thread.start()


def stop_engine():
    """Safely stops the Core Engine to free up the camera for standalone games."""
    global engine
    if engine.is_running:
        print("--- PAUSING CORE ENGINE FOR GAME ---")
        engine.is_running = False
        time.sleep(1)


def restart_engine():
    """Restarts the Core Engine after a game is closed."""
    global engine, engine_thread
    if not engine.is_running:
        print("--- RESTARTING CORE ENGINE ---")
        engine = CoreEngine()
        engine_thread = threading.Thread(target=engine.run, daemon=True)
        engine_thread.start()


# --- 2. DASHBOARD TOGGLES ---
@eel.expose
def toggle_volume_py(state):
    engine.volume_active = state
    print(f"Volume Control: {'ON' if state else 'OFF'}")


@eel.expose
def toggle_mouse_py(state):
    engine.mouse_active = state
    print(f"Mouse Control: {'ON' if state else 'OFF'}")


@eel.expose
def toggle_smartwatch_py(state):
    engine.smartwatch_active = state
    print(f"Smart Watch: {'ON' if state else 'OFF'}")


@eel.expose
def toggle_camera_view_py(state):
    engine.camera_view_active = state
    print(f"Camera View: {'ON' if state else 'OFF'}")


@eel.expose
def check_camera_py():
    if engine is not None:
        return getattr(engine, 'camera_active', False)
    return False


# --- 3. STANDALONE GAMES ---
@eel.expose
def run_shooter_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    game = Shooter.Shooter()
    final_score = game.run(should_quit)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_karate_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    game = KarateChop.KarateChop()
    final_score = game.run(should_quit)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_bubble_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    final_score = bubbleCatcher.run(should_quit)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_rps_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    final_score = rockPaperScissors.run(should_quit)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_meme_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    game = MatchMeme.MatchMeme()
    final_score = game.run(should_quit)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_canvas_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    canvas = AirCanvas.AirCanvas()
    canvas.run(should_quit)
    restart_engine()


@eel.expose
def toggle_macros_py(state):
    engine.macro_active = state
    print(f"Macro Gestures: {'ON' if state else 'OFF'}")


@eel.expose
def save_macro_links_py(l1, l2, l3):
    engine.macro_module.update_links(l1, l2, l3)


@eel.expose
def get_macro_links_py():
    return engine.macro_module.links


@eel.expose
def toggle_presentation_py(state):
    engine.presentation_active = state
    print(f"Presentation Mode: {'ON' if state else 'OFF'}")


@eel.expose
def save_score_py(game, name, p_class, score):
    LB.save_score(game, name, p_class, score)


@eel.expose
def get_leaderboard_py(game):
    return LB.get_top_scores(game)


game_quit_flag = False


@eel.expose
def quit_game_py():
    global game_quit_flag
    game_quit_flag = True
    print("--- UŽIVATEL VYNUTIL UKONČENÍ HRY (KLÁVESA Q) ---")


def should_quit():
    return game_quit_flag


# --- 4. START THE APP ---
if __name__ == '__main__':
    print("--- STARTING GESTURE HUB ---")
    eel.start('index.html', cmdline_args=['--start-maximized'])
