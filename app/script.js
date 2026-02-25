// --- FUNKCE PRO ZOBRAZENÍ CHYBOVÉHO OKNA ---
function showCameraError() {
    const modal = document.getElementById('cameraModal');
    modal.classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('cameraModal');
    modal.classList.add('hidden');

    // Vrácení přepínačů zpět, pokud jsme na ně klikli bez kamery
    const toggles = ['volumeToggle', 'smartwatchToggle', 'mouseToggle', 'presentationToggle', 'macroToggle'];
    toggles.forEach(id => {
        let toggle = document.getElementById(id);
        if (toggle && toggle.checked) toggle.checked = false;
    });
}

function closeModalOnOutsideClick(event) {
    const modalContent = document.querySelector('.modal-content');
    if (!modalContent.contains(event.target)) {
        closeModal();
    }
}

// --- PŘÍJEM OBRAZU Z PYTHONU ---
eel.expose(update_camera_frame);
function update_camera_frame(base64_str) {
    let img = document.getElementById('cam-preview');
    if (img) img.src = "data:image/jpeg;base64," + base64_str;
}

eel.expose(update_game_frame);
function update_game_frame(base64_str) {
    let img = document.getElementById('game-stream');
    if (img) img.src = "data:image/jpeg;base64," + base64_str;
}

// --- UKONČENÍ HRY KLÁVESOU 'Q' ---
document.addEventListener('keydown', function(event) {
    if (event.key.toLowerCase() === 'q') {
        if (!document.getElementById('gameModal').classList.contains('hidden')) {
            eel.quit_game_py()();
            document.getElementById('gameModal').classList.add('hidden');
        }
    }
});

// Pomocná funkce pro zobrazení skóre po hře
let currentGameForScore = "";
let currentScore = 0;

async function showScoreModal(gameName, score) {
    currentGameForScore = gameName;
    currentScore = score;
    document.getElementById("finalScoreDisplay").innerText = "SCORE: " + score;
    document.getElementById("scoreModal").classList.remove("hidden");

    let topScores = await eel.get_leaderboard_py(gameName)();
    let listEl = document.getElementById("leaderboardList");
    listEl.innerHTML = "";

    if (topScores && topScores.length > 0) {
        topScores.forEach((entry, index) => {
            listEl.innerHTML += `<li style="margin-bottom: 8px;"><b>${index + 1}.</b> <span style="color:var(--neon-cyan)">${entry.name}</span> (${entry.p_class}) - <b>${entry.score} pts</b></li>`;
        });
    } else {
        listEl.innerHTML = "<li>No scores yet. Be the first!</li>";
    }
}

// ==========================================
// --- HERNÍ FUNKCE (S KONTROLOU KAMERY!) ---
// ==========================================

async function runShooter() {
    if (!(await eel.check_camera_py())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ SHOOTING RANGE ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    let score = await eel.run_shooter_py();

    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) showScoreModal("SHOOTING RANGE", score);
}

async function runKarate() {
    if (!(await eel.check_camera_py())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ KARATE CHOP ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    let score = await eel.run_karate_py();

    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) showScoreModal("KARATE CHOP", score);
}

async function runBubble() {
    if (!(await eel.check_camera_py())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ BUBBLE CATCHER ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    let score = await eel.run_bubble_py();

    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) showScoreModal("BUBBLE CATCHER", score);
}

async function runRPS() {
    if (!(await eel.check_camera_py())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ R.P.S. GAME ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    let score = await eel.run_rps_py();

    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) showScoreModal("R.P.S. GAME", score);
}

async function runMeme() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ MEME MATCH ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    let score = await eel.run_meme_py()();

    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) showScoreModal("MEME MATCH", score);
}

async function runCanvas() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }

    document.getElementById('gameTitle').innerText = "[ AIR CANVAS ]";
    document.getElementById('gameModal').classList.remove('hidden');
    document.getElementById('game-stream').src = "";

    await eel.run_canvas_py()();
    document.getElementById('gameModal').classList.add('hidden');
}


// ==========================================
// --- FUNKCE V MODULECH (PŘEPÍNAČE) ---
// ==========================================

async function runVolume() {
    let toggle = document.getElementById('volumeToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_volume_py(toggle.checked)();
}

async function runSmartWatch() {
    let toggle = document.getElementById('smartwatchToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_smartwatch_py(toggle.checked)();
}

async function runMouse() {
    let toggle = document.getElementById('mouseToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_mouse_py(toggle.checked)();
}

async function runPresentation() {
    let toggle = document.getElementById('presentationToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_presentation_py(toggle.checked)();
}

async function runMacros() {
    let toggle = document.getElementById('macroToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_macros_py(toggle.checked)();
}

// --- CALIBRATE (CAMERA VIEW) ---
async function runCameraView() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }

    document.getElementById('cameraPreviewModal').classList.remove('hidden');
    eel.toggle_camera_view_py(true)();
}

function closeCameraView() {
    document.getElementById('cameraPreviewModal').classList.add('hidden');
    document.getElementById('cam-preview').src = "";
    eel.toggle_camera_view_py(false)();
}

// --- OSTATNÍ FUNKCE (Skóre, Makra) ---
async function submitScore() {
    let name = document.getElementById("playerName").value;
    let pClass = document.getElementById("playerClass").value;
    if (name === "") name = "Anonymous";
    eel.save_score_py(currentGameForScore, name, pClass, currentScore)();
    closeScoreModal();
}

function closeScoreModal() {
    document.getElementById("scoreModal").classList.add("hidden");
    document.getElementById("playerName").value = "";
    document.getElementById("playerClass").value = "";
}

function openMacroConfig() { document.getElementById('macroConfigModal').classList.remove('hidden'); }
function saveMacroConfig() {
    eel.save_macro_links_py(document.getElementById('link1').value, document.getElementById('link2').value, document.getElementById('link3').value)();
    document.getElementById('macroConfigModal').classList.add('hidden');
}

// --- STATUS KAMERY (PRAVÝ HORNÍ ROH) ---
async function updateCameraStatus() {
    try {
        let isOnline = await eel.check_camera_py()();
        let statusBox = document.getElementById("camera-status");
        let dot = document.getElementById("cam-dot");
        let text = document.getElementById("cam-text");

        if (isOnline) {
            statusBox.className = "cyber-cam-status online";
            dot.className = "cam-dot-online";
            text.innerText = "CAM ONLINE";
        } else {
            statusBox.className = "cyber-cam-status offline";
            dot.className = "cam-dot-offline";
            text.innerText = "CAM OFFLINE";
        }
    } catch (e) {
        document.getElementById("camera-status").className = "cyber-cam-status offline";
        document.getElementById("cam-dot").className = "cam-dot-offline";
        document.getElementById("cam-text").innerText = "SYS ERROR";
    }
}

setInterval(updateCameraStatus, 2000);
updateCameraStatus();

async function loadSavedMacros() {
    try {
        let links = await eel.get_macro_links_py()();
        if (links && links.length === 3) {
            document.getElementById('link1').value = links[0];
            document.getElementById('link2').value = links[1];
            document.getElementById('link3').value = links[2];
        }
    } catch (e) {
        console.log("Makra zatím nenastavena.");
    }
}

loadSavedMacros();

// --- TUTORIAL DATABASE ---
const tutorialData = {
    "Shooter": {
        title: "[ SHOOTING RANGE ]",
        text: "> Pinch your thumb and index finger together to shoot.\n> Aim at the targets and destroy as many as possible within the time limit!\n Show your palm to reload."
    },
    "Karate": {
        title: "[ KARATE CHOP ]",
        text: "> Your weapon is your pinky finger!\n> Chop with your hand like a sword to slice the falling fruit.\n> Avoid the black bombs with an 'X', or the game ends immediately."
    },
    "Bubble": {
        title: "[ BUBBLE CATCHER ]",
        text: "> Catch the falling bubbles directly into your palm.\n> Just position your hand so the bubble falls into it."
    },
    "RPS": {
        title: "[ R.P.S. GAME ]",
        text: "> Let's play Rock, Paper, Scissors!\n> Wait for the 3.. 2.. 1.. countdown.\n> Show a fist (Rock), V-sign (Scissors), or open palm (Paper)."
    },
    "Meme": {
        title: "[ MEME MATCH ]",
        text: "> You will see a Meme face in the right corner.\n> Imitate its expression (smile, surprise, open mouth) as quickly and accurately as possible.\n> The AI will compare your face and award you a score."
    },
    "Canvas": {
        title: "[ AIR CANVAS ]",
        text: "> Raise ONLY your INDEX finger to draw.\n> Raise two fingers (Peace sign ✌️) to pause drawing and select a color from the top menu."
    },
    "Volume": {
        title: "[ VOLUME CONTROL ]",
        text: "> You need two hands for this one.\n> Show your palm on one hand and thumb up on the other.\n Gently turn (angle) your thumb up and down."
    },
    "SmartWatch": {
        title: "[ SMARTWATCH ]",
        text: "> Bring the index finger of one hand close to the wrist of your other hand.\n> A holographic watch will instantly activate and show the current time."
    },
    "Mouse": {
        title: "[ MOUSE CONTROL ]",
        text: "> Move your raised index finger to move the mouse cursor.\n> A quick pinch of your thumb and index finger acts as a left click."
    },
    "Presentation": {
        title: "[ PRESENTATION SWIPE ]",
        text: "> Perfect for PowerPoint or viewing photos.\n> Swipe your whole hand from left to right (or right to left) to move to the next/previous slide."
    },
    "Macro": {
        title: "[ MACRO LINKS ]",
        text: "> A quick hand swipe from bottom to top brings up the Virtual Keyboard.\n> Raise your fingers in a ✌️, 👍, or 🤘 shape to instantly open your saved links."
    }
};

function openTutorial(moduleId, event) {
    if (event) event.stopPropagation();

    let data = tutorialData[moduleId];
    if (data) {
        document.getElementById('tutTitle').innerText = data.title;
        document.getElementById('tutText').innerHTML = data.text.replace(/\n/g, "<br><br>");
        document.getElementById('tutorialModal').classList.remove('hidden');
    }
}

function closeTutorial() {
    document.getElementById('tutorialModal').classList.add('hidden');
}

function closeTutorialOnOutsideClick(event) {
    const modalContent = document.querySelector('#tutorialModal .modal-content');
    if (!modalContent.contains(event.target)) {
        closeTutorial();
    }
}

// --- SMARTWATCH WEB OVERLAY ---
let smartwatchTimeout;

eel.expose(show_smartwatch_web);
function show_smartwatch_web(time_str) {
    let watchDiv = document.getElementById('smartwatchOverlay');
    document.getElementById('smartwatchTime').innerText = time_str;

    watchDiv.classList.remove('hidden');
    watchDiv.style.opacity = "1";

    clearTimeout(smartwatchTimeout);
    smartwatchTimeout = setTimeout(() => {
        watchDiv.style.opacity = "0";
        setTimeout(() => watchDiv.classList.add('hidden'), 300);
    }, 3000);
}


