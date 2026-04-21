import eel
import threading
import time
import cv2
import sys
import os
from CoreEngine import CoreEngine
from Games import Shooter
from Games import KarateChop
import Games.BubbleCatcher as bubbleCatcher
import Games.RockPaperScissors as rockPaperScissors
import Leaderboard as LB
import Games.MatchMeme as MatchMeme
import Games.AirCanvas as AirCanvas
import Games.Gesture67 as Gesture67


if hasattr(sys, '_MEIPASS'):
    eel.init(sys._MEIPASS)
else:
    eel.init('')

engine = CoreEngine()
engine_thread = threading.Thread(target=engine.run, daemon=True)
engine_thread.start()


def stop_engine():
    global engine
    if engine and engine.is_running:
        engine.is_running = False
        timeout = 0
        while engine.camera_active and timeout < 50:
            time.sleep(0.1)
            timeout += 1
        cv2.destroyAllWindows()
        time.sleep(1.5)


def restart_engine():
    global engine, engine_thread
    if engine is None or not engine.is_running:
        old_vol = engine.volume_active if engine else False
        old_mouse = engine.mouse_active if engine else False
        old_smart = getattr(engine, 'smartwatch_active', False)
        old_pres = getattr(engine, 'presentation_active', False)
        old_macro = getattr(engine, 'macro_active', False)
        old_view = engine.camera_view_active if engine else False
        old_keyb = getattr(engine, 'keyboard_active', False)

        engine = CoreEngine()

        engine.volume_active = old_vol
        engine.mouse_active = old_mouse
        engine.smartwatch_active = old_smart
        engine.presentation_active = old_pres
        engine.macro_active = old_macro
        engine.camera_view_active = old_view
        engine.keyboard_active = old_keyb

        engine_thread = threading.Thread(target=engine.run, daemon=True)
        engine_thread.start()


@eel.expose
def toggle_volume_py(state):
    engine.volume_active = state


@eel.expose
def toggle_mouse_py(state):
    engine.mouse_active = state


@eel.expose
def toggle_smartwatch_py(state):
    engine.smartwatch_active = state


@eel.expose
def toggle_camera_view_py(state):
    engine.camera_view_active = state


@eel.expose
def toggle_keyboard_py(state):
    engine.keyboard_active = state


@eel.expose
def check_camera_py():
    if engine is not None:
        return getattr(engine, 'camera_active', False)
    return False


@eel.expose
def run_shooter_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    game = Shooter.Shooter()
    final_score = game.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("SHOOTING RANGE", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_karate_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    game = KarateChop.KarateChop()
    final_score = game.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("KARATE CHOP", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_bubble_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    final_score = bubbleCatcher.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("BUBBLE CATCHER", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_rps_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    final_score = rockPaperScissors.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("R.P.S. GAME", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_meme_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    game = MatchMeme.MatchMeme()
    final_score = game.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("MEME MATCH", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_gesture67_py(player_name=None):
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    game = Gesture67.Gesture67()
    final_score = game.run(should_quit)
    if final_score > 0 and player_name:
        LB.save_score("GESTURE 67", player_name, "N/A", final_score)
    restart_engine()
    return final_score if not game_quit_flag else 0


@eel.expose
def run_canvas_py():
    global game_quit_flag
    game_quit_flag = False
    stop_engine()
    time.sleep(1.5)
    canvas = AirCanvas.AirCanvas()
    canvas.run(should_quit)
    restart_engine()


@eel.expose
def toggle_macros_py(state):
    engine.macro_active = state


@eel.expose
def save_macro_links_py(l1, l2, l3):
    engine.macro_module.update_links(l1, l2, l3)


@eel.expose
def get_macro_links_py():
    return engine.macro_module.links


@eel.expose
def toggle_presentation_py(state):
    engine.presentation_active = state


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


def should_quit():
    return game_quit_flag


if __name__ == '__main__':
    eel.start('index.html', cmdline_args=['--start-maximized'])
