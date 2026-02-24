// Funkce pro zobrazení chybového okna
function showCameraError() {
    const modal = document.getElementById('cameraModal');
    modal.classList.remove('hidden');
}

// Funkce pro zavření okna tlačítkem
function closeModal() {
    const modal = document.getElementById('cameraModal');
    modal.classList.add('hidden');

    // Pokud jsme modal otevřeli přes přepínač hlasitosti, vrátíme ho zpět
    const volumeToggle = document.getElementById('volumeToggle');
    if (volumeToggle && volumeToggle.checked) {
        volumeToggle.checked = false;
    }
}

// Funkce pro zavření okna kliknutím mimo něj (na tmavé pozadí)
function closeModalOnOutsideClick(event) {
    const modalContent = document.querySelector('.modal-content');
    // Pokud kliknutí NEBYLO uvnitř obsahu modalu, zavři ho
    if (!modalContent.contains(event.target)) {
        closeModal();
    }
}

// --- HERNÍ FUNKCE ---

async function runShooter() {
    try {
        let camOk = await eel.check_camera_py()();
        if (camOk) { eel.run_shooting()(); } else { showCameraError(); }
    } catch (e) { console.error("Chyba komunikace s Pythonem:", e); showCameraError(); }
}

async function runKatana() {
    try {
        let camOk = await eel.check_camera_py()();
        if (camOk) { eel.run_karate()(); } else { showCameraError(); }
    } catch (e) { console.error("Chyba komunikace s Pythonem:", e); showCameraError(); }
}

async function runBubble() {
    try {
        let camOk = await eel.check_camera_py()();
        if (camOk) { eel.run_bubbles()(); } else { showCameraError(); }
    } catch (e) { console.error("Chyba komunikace s Pythonem:", e); showCameraError(); }
}

async function runRPS() {
    try {
        let camOk = await eel.check_camera_py()();
        if (camOk) { eel.run_rps()(); } else { showCameraError(); }
    } catch (e) { console.error("Chyba komunikace s Pythonem:", e); showCameraError(); }
}


async function runSmartWatch() {
    let isChecked = document.getElementById('smartwatchToggle').checked;
    eel.toggle_smartwatch_py(isChecked)();
}

// Odesílání snímků pro kameru
eel.expose(update_camera_frame);
async function update_camera_frame(base64_str) {
    let img = document.getElementById('cam-preview');
    if (img) { img.src = "data:image/jpeg;base64," + base64_str; }
}

// Funkce pro zapnutí/vypnutí náhledu kamery
async function runCameraView() {
    document.getElementById('cameraPreviewModal').classList.remove('hidden');
    eel.toggle_camera_view_py(true)(); // Zapne v Pythonu
}

async function closeCameraView() {
    document.getElementById('cameraPreviewModal').classList.add('hidden');
    document.getElementById('cam-preview').src = "";
    eel.toggle_camera_view_py(false)(); // Vypne v Pythonu
}

// Funkce pro přepínač hlasitosti
async function runVolume() {
    // Najde tvůj přepínač a zjistí, jestli je zaškrtnutý (True/False)
    let isChecked = document.querySelector('.cyber-switch input').checked;
    eel.toggle_volume_py(isChecked)();
}

// Odeslani stavu prepinace pro mys
async function runMouse() {
    let isChecked = document.getElementById('mouseToggle').checked;
    eel.toggle_mouse_py(isChecked)();
}

let currentGameForScore = "";
let currentScore = 0;

// Upravená funkce pro spuštění hry (Příklad pro Střelnici)
async function runShooter() {
    let score = await eel.run_shooter_py();
    if (score > 0) {
        currentGameForScore = "Shooter";
        currentScore = score;
        document.getElementById("finalScoreDisplay").innerText = "SKÓRE: " + score;
        document.getElementById("scoreModal").classList.remove("hidden");
    }
}

async function submitScore() {
    let name = document.getElementById("playerName").value;
    let pClass = document.getElementById("playerClass").value;

    if (name === "") name = "Anonymus";

    eel.save_score_py(currentGameForScore, name, pClass, currentScore)();
    closeScoreModal();
    alert("Noted!");
}

async function closeScoreModal() {
    document.getElementById("scoreModal").classList.add("hidden");
    document.getElementById("playerName").value = "";
    document.getElementById("playerClass").value = "";
}

async function runMeme() {
    let score = await eel.run_meme_py();
    if (score > 0) {
        currentGameForScore = "MemeMatch";
        currentScore = score;
        document.getElementById("finalScoreDisplay").innerText = "SCORE: " + score;
        document.getElementById("scoreModal").classList.remove("hidden");
    }
}

async function runCanvas() {
    eel.run_canvas_py();
}

async function runPresentation() {
    let isChecked = document.getElementById('presentationToggle').checked;
    eel.toggle_presentation_py(isChecked);
}

async function runMacros() {
    let isChecked = document.getElementById('macroToggle').checked;
    eel.toggle_macros_py(isChecked)();
}

async function openMacroConfig() {
    document.getElementById('macroConfigModal').classList.remove('hidden');
}

async function saveMacroConfig() {
    let l1 = document.getElementById('link1').value;
    let l2 = document.getElementById('link2').value;
    let l3 = document.getElementById('link3').value;
    eel.save_macro_links_py(l1, l2, l3)();
    document.getElementById('macroConfigModal').classList.add('hidden');
}
