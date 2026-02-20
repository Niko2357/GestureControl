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

async function runVolume() {
    const volumeToggle = document.getElementById('volumeToggle');
    if (volumeToggle.checked) {
        try {
            let camOk = await eel.check_camera_py()();
            if (camOk) {
                eel.run_volume()();
            } else {
                showCameraError();
            }
        } catch (e) {
            console.error("Chyba komunikace s Pythonem:", e);
            showCameraError();
            volumeToggle.checked = false;
        }
    } else {
        console.log("Volume module disabled.");
    }
}

async function runWatch() {
    try {
        let camOk = await eel.check_camera_py()();
        if (camOk) { eel.run_watch()(); } else { showCameraError(); }
    } catch (e) { console.error("Chyba komunikace s Pythonem:", e); showCameraError(); }
}
