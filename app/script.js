let promptPromiseResolve;

function getPlayerName() {
    return new Promise((resolve) => {
        let modal = document.getElementById('customPromptModal');
        let input = document.getElementById('customPromptInput');
        if(!modal) { resolve("Guest"); return; }
        modal.classList.remove('hidden');
        input.value = "Player1";
        input.focus();
        promptPromiseResolve = resolve;
    });
}

function submitCustomPrompt() {
    document.getElementById('customPromptModal').classList.add('hidden');
    if (promptPromiseResolve) promptPromiseResolve(document.getElementById('customPromptInput').value);
}

function cancelCustomPrompt() {
    document.getElementById('customPromptModal').classList.add('hidden');
    if (promptPromiseResolve) promptPromiseResolve(null);
}

function showCameraError() {
    document.getElementById('cameraModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('cameraModal').classList.add('hidden');
    const toggles = ['volumeToggle', 'smartwatchToggle', 'mouseToggle', 'presentationToggle', 'macroToggle', 'keyboardToggle'];
    toggles.forEach(id => {
        let toggle = document.getElementById(id);
        if (toggle && toggle.checked) toggle.checked = false;
    });
}

function closeModalOnOutsideClick(event) {
    const modalContent = document.querySelector('.modal-content');
    if (!modalContent.contains(event.target)) closeModal();
}

eel.expose(update_camera_frame);
function update_camera_frame(base64_img) {
    let camImg = document.getElementById("cam-preview");
    if (camImg) camImg.src = "data:image/jpeg;base64," + base64_img;
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        let gModal = document.getElementById('gameModal');
        if (gModal && !gModal.classList.contains('hidden')) {
            eel.quit_game_py();
            gModal.classList.add('hidden');
        }
    }
});

async function viewLeaderboard(gameName, event = null, currentScore = null) {
    if (event) event.stopPropagation();
    let topScores = await eel.get_leaderboard_py(gameName)();
    let listEl = document.getElementById("leaderboardList");
    listEl.innerHTML = "";
    document.getElementById("leaderboardGameName").innerText = gameName + " - TOP SCORES";
    let scoreDisplay = document.getElementById("finalScoreDisplay");
    if (currentScore !== null) {
        document.getElementById("leaderboardTitle").innerText = "[ GAME OVER ]";
        scoreDisplay.innerText = "SCORE: " + currentScore;
        scoreDisplay.style.display = "block";
    } else {
        document.getElementById("leaderboardTitle").innerText = "[ LEADERBOARD ]";
        scoreDisplay.style.display = "none";
    }
    document.getElementById("scoreModal").classList.remove("hidden");
    if (topScores && topScores.length > 0) {
        topScores.forEach((entry, index) => {
            listEl.innerHTML += `
                <li style="margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px;">
                    <b style="color:var(--neon-cyan)">#${index + 1}</b>
                    <span style="color:white; margin-left:10px;">${entry.name}</span>
                    <span style="float:right; color:var(--neon-cyan)">${entry.score} pts</span>
                </li>`;
        });
    } else {
        listEl.innerHTML = "<li style='text-align:center; opacity:0.5;'>No records found.</li>";
    }
}

function closeScoreModal() {
    document.getElementById("scoreModal").classList.add("hidden");
}

function closeScoreModalOnOutsideClick(event) {
    const modalContent = document.querySelector('#scoreModal .modal-content');
    if (!modalContent.contains(event.target)) closeScoreModal();
}

async function openGlobalLeaderboard() {
    viewLeaderboard("SHOOTING RANGE");
}

async function runShooter() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_shooter_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("SHOOTING RANGE", null, score);
}

async function runKarate() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_karate_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("KARATE CHOP", null, score);
}

async function runBubble() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_bubble_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("BUBBLE CATCHER", null, score);
}

async function runRPS() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_rps_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("R.P.S. GAME", null, score);
}

async function runMeme() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_meme_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("MEME MATCH", null, score);
}

async function runGesture67() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    let playerName = await getPlayerName();
    if (playerName === null) return;
    if (playerName === "") playerName = "Guest";
    document.getElementById('gameModal').classList.remove('hidden');
    let score = await eel.run_gesture67_py(playerName)();
    document.getElementById('gameModal').classList.add('hidden');
    if (score > 0) viewLeaderboard("GESTURE 67", null, score);
}

async function runCanvas() {
    if (!(await eel.check_camera_py()())) { showCameraError(); return; }
    document.getElementById('gameModal').classList.remove('hidden');
    await eel.run_canvas_py()();
    document.getElementById('gameModal').classList.add('hidden');
}

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

async function runKeyboard() {
    let toggle = document.getElementById('keyboardToggle');
    if (toggle.checked && !(await eel.check_camera_py()())) { showCameraError(); return; }
    eel.toggle_keyboard_py(toggle.checked)();
}

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

function openMacroConfig() { document.getElementById('macroConfigModal').classList.remove('hidden'); }
function saveMacroConfig() {
    eel.save_macro_links_py(document.getElementById('link1').value, document.getElementById('link2').value, document.getElementById('link3').value)();
    document.getElementById('macroConfigModal').classList.add('hidden');
}

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
        let statusBox = document.getElementById("camera-status");
        if(statusBox) statusBox.className = "cyber-cam-status offline";
        let dot = document.getElementById("cam-dot");
        if(dot) dot.className = "cam-dot-offline";
        let text = document.getElementById("cam-text");
        if(text) text.innerText = "SYS ERROR";
    }
}

setInterval(updateCameraStatus, 2000);
setTimeout(updateCameraStatus, 500);

async function loadSavedMacros() {
    try {
        let links = await eel.get_macro_links_py()();
        if (links && links.length === 3) {
            document.getElementById('link1').value = links[0];
            document.getElementById('link2').value = links[1];
            document.getElementById('link3').value = links[2];
        }
    } catch (e) {}
}
setTimeout(loadSavedMacros, 1000);

const tutorialData = {
    "Shooter": { title: "[ SHOOTING RANGE ]", text: "> Pinch your thumb and index finger together to shoot.<br>> Aim at the targets and destroy as many as possible within the time limit!" },
    "Karate": { title: "[ KARATE CHOP ]", text: "> Your weapon is your pinky finger!<br>> Chop with your hand like a sword to slice the falling fruit." },
    "Bubble": { title: "[ BUBBLE CATCHER ]", text: "> Catch the falling bubbles directly into your palm." },
    "RPS": { title: "[ R.P.S. GAME ]", text: "> Let's play Rock, Paper, Scissors!<br>> Wait for the countdown." },
    "Meme": { title: "[ MEME MATCH ]", text: "> Imitate the Meme expression quickly and accurately." },
    "Canvas": { title: "[ AIR CANVAS ]", text: "> Raise ONLY your INDEX finger to draw.<br>> Raise two fingers (peace) to pause drawing." },
    "Gesture67": { title: "[ SPEED PUMP ]", text: "> Throw both hands up above the green line and pull them down below the red line.<br>> You have exactly 20 seconds to do as many reps as possible!" },
    "Volume": { title: "[ VOLUME CONTROL ]", text: "> Show your palm on one hand and thumb up on the other.<br>> Gently turn your thumb up and down." },
    "SmartWatch": { title: "[ SMARTWATCH ]", text: "> Bring the index finger of one hand close to the wrist of your other hand." },
    "Mouse": { title: "[ MOUSE CONTROL ]", text: "> Move your raised index finger to move the mouse cursor.<br>> Pinch your thumb and index finger to left click." },
    "Presentation": { title: "[ PRESENTATION SWIPE ]", text: "> Swipe your whole hand from left to right to move to the next/previous slide." },
    "Macro": { title: "[ MACRO LINKS ]", text: "> Raise your fingers in a peace, thumbs up, or rock shape to instantly open your saved links." },
    "Keyboard": { title: "[ VIRTUAL KEYBOARD ]", text: "> Click into any text field.<br>> Show the ASL letter gesture on camera and hold it for 2 seconds." }
};

function openTutorial(moduleId, event) {
    if (event) event.stopPropagation();
    let data = tutorialData[moduleId];
    if (data) {
        document.getElementById('tutTitle').innerText = data.title;
        document.getElementById('tutText').innerHTML = data.text;
        document.getElementById('tutorialModal').classList.remove('hidden');
    }
}

function closeTutorial() { document.getElementById('tutorialModal').classList.add('hidden'); }

function closeTutorialOnOutsideClick(event) {
    const modalContent = document.querySelector('#tutorialModal .modal-content');
    if (!modalContent.contains(event.target)) closeTutorial();
}

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

let keyboardHudTimeout;
eel.expose(show_keyboard_hud_web);
function show_keyboard_hud_web(mode, text, progress) {
    let overlay = document.getElementById('keyboardOverlay');
    document.getElementById('keyboardMode').innerText = "[ " + mode + " ]";
    document.getElementById('keyboardText').innerText = text;
    document.getElementById('keyboardProgress').style.width = (progress * 100) + "%";

    overlay.classList.remove('hidden');
    overlay.style.opacity = "1";

    clearTimeout(keyboardHudTimeout);
    keyboardHudTimeout = setTimeout(() => {
        overlay.style.opacity = "0";
        setTimeout(() => overlay.classList.add('hidden'), 300);
    }, 1500);
}

eel.expose(hide_keyboard_hud_web);
function hide_keyboard_hud_web() {
    let overlay = document.getElementById('keyboardOverlay');
    if (overlay) {
        overlay.style.opacity = "0";
        setTimeout(() => overlay.classList.add('hidden'), 300);
    }
}

