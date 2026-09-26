/**
 * POKER RNG — Elegant GTO Decision Engine
 * High-performance, cryptographically secure random number generator
 * designed for mixed-strategy poker play.
 */

(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // State Management
    // -------------------------------------------------------------------------
    const state = {
        min: 1,
        max: 100,
        currentRoll: 50,
        threshold: 50,
        actionAName: 'BET / RAISE',
        actionBName: 'CHECK / FOLD',
        mode: 'manual', // 'manual' | 'auto' | 'hover'
        autoIntervalSec: 2,
        isMuted: false,
        theme: 'emerald',
        isHudMode: false,
        history: [],
        totalRolls: 0,
        sumRolls: 0,
        actionACount: 0,
        // Auto-roll RAF state
        autoRafId: null,
        autoStartTime: null
    };

    // -------------------------------------------------------------------------
    // DOM Elements
    // -------------------------------------------------------------------------
    const elements = {
        body: document.body,
        appContainer: document.getElementById('appContainer'),
        rollDisplay: document.getElementById('rollDisplay'),
        dialContainer: document.getElementById('dialContainer'),
        dialFill: document.getElementById('dialFill'),
        decisionBadge: document.getElementById('decisionBadge'),
        decisionActionText: document.getElementById('decisionActionText'),
        decisionDiffText: document.getElementById('decisionDiffText'),
        btnRoll: document.getElementById('btnRoll'),
        range100: document.getElementById('range100'),
        range99: document.getElementById('range99'),
        freqSlider: document.getElementById('freqSlider'),
        thresholdDisplay: document.getElementById('thresholdDisplay'),
        actionInputA: document.getElementById('actionInputA'),
        actionInputB: document.getElementById('actionInputB'),
        actionBoxA: document.getElementById('actionBoxA'),
        actionBoxB: document.getElementById('actionBoxB'),
        tagAVal: document.querySelector('.tag-a-val'),
        tagBVal: document.querySelector('.tag-b-val'),
        historyStrip: document.getElementById('historyStrip'),
        clearHistoryBtn: document.getElementById('clearHistoryBtn'),
        statTotalCount: document.getElementById('statTotalCount'),
        statAverage: document.getElementById('statAverage'),
        statActionRate: document.getElementById('statActionRate'),
        soundBtn: document.getElementById('soundBtn'),
        soundIconOn: document.getElementById('soundIconOn'),
        soundIconOff: document.getElementById('soundIconOff'),
        popoutBtn: document.getElementById('popoutBtn'),
        compactToggleBtn: document.getElementById('compactToggleBtn'),
        compactBtnLabel: document.getElementById('compactBtnLabel'),
        intervalControls: document.getElementById('intervalControls'),
        modeTabs: document.querySelectorAll('.mode-tab'),
        themeDots: document.querySelectorAll('.theme-dot'),
        presetChips: document.querySelectorAll('.preset-chip'),
        intervalChips: document.querySelectorAll('.interval-chip')
    };

    // Circumference of 2 * PI * 110 = ~691.15
    const DIAL_CIRCUMFERENCE = 2 * Math.PI * 110;

    // -------------------------------------------------------------------------
    // Audio Synthesizer (Web Audio API - Zero External Dependencies)
    // -------------------------------------------------------------------------
    let audioCtx = null;

    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function playRollSound(isActionA) {
        if (state.isMuted) return;
        try {
            const ctx = getAudioContext();
            if (!ctx) return;

            const now = ctx.currentTime;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            // Tactile chip sound: Action A gets a crisp ascending tone, Action B a softer subtle click
            if (isActionA) {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(580, now);
                osc.frequency.exponentialRampToValueAtTime(920, now + 0.06);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
            } else {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(420, now);
                osc.frequency.exponentialRampToValueAtTime(260, now + 0.05);
                gain.gain.setValueAtTime(0.08, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
            }

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.09);
        } catch (e) {
            console.warn('Audio playback error:', e);
        }
    }

    // -------------------------------------------------------------------------
    // Cryptographically Secure RNG (CSPRNG)
    // -------------------------------------------------------------------------
    function generateCryptoRandom(min, max) {
        const range = max - min + 1;
        const maxUint32 = 0xFFFFFFFF;
        const limit = maxUint32 - (maxUint32 % range);
        const buffer = new Uint32Array(1);

        do {
            window.crypto.getRandomValues(buffer);
        } while (buffer[0] >= limit);

        return min + (buffer[0] % range);
    }

    // -------------------------------------------------------------------------
    // Core Roll Engine
    // -------------------------------------------------------------------------
    function executeRoll() {
        const newNumber = generateCryptoRandom(state.min, state.max);
        state.currentRoll = newNumber;
        const isActionA = newNumber <= state.threshold;

        // Sound feedback
        playRollSound(isActionA);

        // Visual roll tick effect
        elements.rollDisplay.classList.add('rolling');
        setTimeout(() => elements.rollDisplay.classList.remove('rolling'), 120);

        // Update displays
        elements.rollDisplay.textContent = newNumber;
        updateDecisionView(newNumber, isActionA);

        // Record in history & stats
        recordHistory(newNumber, isActionA);

        // If in manual or hover mode, update dial ring based on value
        if (state.mode !== 'auto') {
            updateDialValueProgress(newNumber);
        } else {
            // Reset auto countdown timer start
            state.autoStartTime = performance.now();
        }
    }

    function updateDialValueProgress(number) {
        const span = state.max - state.min;
        const percent = span > 0 ? (number - state.min) / span : 0.5;
        const offset = DIAL_CIRCUMFERENCE * (1 - percent);
        elements.dialFill.style.strokeDashoffset = offset;
    }

    function updateDecisionView(number, isActionA) {
        if (isActionA) {
            elements.decisionBadge.className = 'decision-badge action-a';
            elements.decisionActionText.textContent = state.actionAName || 'ACTION A';
            elements.decisionDiffText.textContent = `≤ ${state.threshold}%`;

            elements.actionBoxA.classList.add('highlight');
            elements.actionBoxB.classList.remove('highlight');
        } else {
            elements.decisionBadge.className = 'decision-badge action-b';
            elements.decisionActionText.textContent = state.actionBName || 'ACTION B';
            elements.decisionDiffText.textContent = `> ${state.threshold}%`;

            elements.actionBoxB.classList.add('highlight');
            elements.actionBoxA.classList.remove('highlight');
        }
    }

    // -------------------------------------------------------------------------
    // History & Statistics Tracker
    // -------------------------------------------------------------------------
    function recordHistory(number, isActionA) {
        state.totalRolls++;
        state.sumRolls += number;
        if (isActionA) state.actionACount++;

        state.history.unshift({ number, isActionA, time: Date.now() });
        if (state.history.length > 20) state.history.pop();

        renderHistory();
        renderStats();
    }

    function renderHistory() {
        if (state.history.length === 0) {
            elements.historyStrip.innerHTML = '<span class="history-empty">No rolls yet. Press Spacebar!</span>';
            return;
        }

        elements.historyStrip.innerHTML = state.history.map(item => `
            <div class="history-pill ${item.isActionA ? 'pill-action-a' : 'pill-action-b'}" title="${item.isActionA ? state.actionAName : state.actionBName}">
                ${item.number}
            </div>
        `).join('');
    }

    function renderStats() {
        elements.statTotalCount.textContent = state.totalRolls;
        if (state.totalRolls > 0) {
            const avg = (state.sumRolls / state.totalRolls).toFixed(1);
            const rate = ((state.actionACount / state.totalRolls) * 100).toFixed(0);
            elements.statAverage.textContent = avg;
            elements.statActionRate.textContent = `${rate}%`;
        } else {
            elements.statAverage.textContent = '—';
            elements.statActionRate.textContent = '—';
        }
    }

    function clearHistory() {
        state.history = [];
        state.totalRolls = 0;
        state.sumRolls = 0;
        state.actionACount = 0;
        renderHistory();
        renderStats();
    }

    // -------------------------------------------------------------------------
    // Auto-Roll Animation (RequestAnimationFrame Ring Countdown)
    // -------------------------------------------------------------------------
    function startAutoRoll() {
        stopAutoRoll();
        state.autoStartTime = performance.now();

        function tick(now) {
            if (state.mode !== 'auto') return;

            const elapsed = now - state.autoStartTime;
            const durationMs = state.autoIntervalSec * 1000;
            const progress = Math.min(elapsed / durationMs, 1);

            // Animate countdown ring draining or filling
            const offset = DIAL_CIRCUMFERENCE * (1 - progress);
            elements.dialFill.style.strokeDashoffset = offset;

            if (elapsed >= durationMs) {
                executeRoll();
                state.autoStartTime = now;
            }

            state.autoRafId = requestAnimationFrame(tick);
        }

        state.autoRafId = requestAnimationFrame(tick);
    }

    function stopAutoRoll() {
        if (state.autoRafId) {
            cancelAnimationFrame(state.autoRafId);
            state.autoRafId = null;
        }
    }

    // -------------------------------------------------------------------------
    // Mode Switching
    // -------------------------------------------------------------------------
    function setMode(newMode) {
        state.mode = newMode;

        elements.modeTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === newMode);
        });

        if (newMode === 'auto') {
            elements.intervalControls.classList.remove('hidden');
            startAutoRoll();
        } else {
            elements.intervalControls.classList.add('hidden');
            stopAutoRoll();
            updateDialValueProgress(state.currentRoll);
        }
    }

    // -------------------------------------------------------------------------
    // Threshold & Action Presets
    // -------------------------------------------------------------------------
    function setThreshold(val) {
        const num = Math.max(0, Math.min(100, parseInt(val, 10) || 0));
        state.threshold = num;
        elements.freqSlider.value = num;
        elements.thresholdDisplay.textContent = num;

        // Update action tags
        elements.tagAVal.textContent = num;
        elements.tagBVal.textContent = Math.min(num + 1, 100);

        // Preset chips active state
        elements.presetChips.forEach(chip => {
            chip.classList.toggle('active', parseInt(chip.dataset.val, 10) === num);
        });

        // Re-evaluate current roll against new threshold
        updateDecisionView(state.currentRoll, state.currentRoll <= state.threshold);
    }

    // -------------------------------------------------------------------------
    // Theme Management
    // -------------------------------------------------------------------------
    function setTheme(themeName) {
        state.theme = themeName;
        elements.body.setAttribute('data-theme', themeName);
        elements.themeDots.forEach(dot => {
            dot.classList.toggle('active', dot.dataset.color === themeName);
        });
        localStorage.setItem('poker_rng_theme', themeName);
    }

    // -------------------------------------------------------------------------
    // HUD / Compact Mode & Pop-out Window
    // -------------------------------------------------------------------------
    function toggleHudMode(forceState) {
        const isHud = typeof forceState === 'boolean' ? forceState : !state.isHudMode;
        state.isHudMode = isHud;
        elements.body.classList.toggle('hud-mode', isHud);
        elements.compactToggleBtn.classList.toggle('active', isHud);
        elements.compactBtnLabel.textContent = isHud ? 'Full View' : 'HUD Mode';
    }

    function openPopoutWindow() {
        const width = 340;
        const height = 460;
        const left = window.screen.width - width - 40;
        const top = 100;
        window.open(
            window.location.pathname + '?mode=hud',
            'PokerRNG_MiniHUD',
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=no,status=no,location=no,toolbar=no,menubar=no`
        );
    }

    // -------------------------------------------------------------------------
    // Event Listeners Setup
    // -------------------------------------------------------------------------
    function setupEventListeners() {
        // Roll CTA button click
        elements.btnRoll.addEventListener('click', () => {
            executeRoll();
        });

        // Click dial directly to roll
        elements.dialContainer.addEventListener('click', () => {
            executeRoll();
        });

        // Hover mode trigger
        let lastHoverRoll = 0;
        elements.dialContainer.addEventListener('mousemove', () => {
            if (state.mode === 'hover') {
                const now = Date.now();
                if (now - lastHoverRoll > 320) {
                    lastHoverRoll = now;
                    executeRoll();
                }
            }
        });

        // Mode tabs
        elements.modeTabs.forEach(tab => {
            tab.addEventListener('click', () => setMode(tab.dataset.mode));
        });

        // Interval chips
        elements.intervalChips.forEach(chip => {
            chip.addEventListener('click', () => {
                elements.intervalChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                state.autoIntervalSec = parseInt(chip.dataset.sec, 10);
                if (state.mode === 'auto') {
                    startAutoRoll();
                }
            });
        });

        // Range 100 vs 99 buttons
        elements.range100.addEventListener('click', () => {
            elements.range100.classList.add('active');
            elements.range99.classList.remove('active');
            state.min = 1;
            state.max = 100;
            executeRoll();
        });

        elements.range99.addEventListener('click', () => {
            elements.range99.classList.add('active');
            elements.range100.classList.remove('active');
            state.min = 0;
            state.max = 99;
            executeRoll();
        });

        // Frequency Slider
        elements.freqSlider.addEventListener('input', (e) => {
            setThreshold(e.target.value);
        });

        // Preset Chips
        elements.presetChips.forEach(chip => {
            chip.addEventListener('click', () => {
                setThreshold(chip.dataset.val);
            });
        });

        // Action Name Inputs
        elements.actionInputA.addEventListener('input', (e) => {
            state.actionAName = e.target.value.trim() || 'AKTION A';
            updateDecisionView(state.currentRoll, state.currentRoll <= state.threshold);
        });

        elements.actionInputB.addEventListener('input', (e) => {
            state.actionBName = e.target.value.trim() || 'AKTION B';
            updateDecisionView(state.currentRoll, state.currentRoll <= state.threshold);
        });

        // Clear History
        elements.clearHistoryBtn.addEventListener('click', clearHistory);

        // Sound Toggle
        elements.soundBtn.addEventListener('click', () => {
            state.isMuted = !state.isMuted;
            elements.soundIconOn.classList.toggle('hidden', state.isMuted);
            elements.soundIconOff.classList.toggle('hidden', !state.isMuted);
            localStorage.setItem('poker_rng_mute', state.isMuted ? 'true' : 'false');
            if (!state.isMuted) {
                playRollSound(true);
            }
        });

        // Theme Dots
        elements.themeDots.forEach(dot => {
            dot.addEventListener('click', () => setTheme(dot.dataset.color));
        });

        // HUD compact toggle & Popout
        elements.compactToggleBtn.addEventListener('click', () => toggleHudMode());
        elements.popoutBtn.addEventListener('click', openPopoutWindow);

        // Keyboard Shortcuts
        window.addEventListener('keydown', (e) => {
            // Ignore when typing inside input fields
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                return;
            }

            if (e.code === 'Space') {
                e.preventDefault();
                executeRoll();
            } else if (e.code === 'KeyA') {
                e.preventDefault();
                setMode(state.mode === 'auto' ? 'manual' : 'auto');
            } else if (e.code === 'KeyH') {
                e.preventDefault();
                toggleHudMode();
            } else if (e.code === 'KeyM') {
                e.preventDefault();
                elements.soundBtn.click();
            } else if (e.code === 'ArrowUp') {
                e.preventDefault();
                setThreshold(Math.min(100, state.threshold + 5));
            } else if (e.code === 'ArrowDown') {
                e.preventDefault();
                setThreshold(Math.max(0, state.threshold - 5));
            } else if (['Digit1', 'Digit2', 'Digit3', 'Digit4', 'Digit5'].includes(e.code)) {
                const sec = parseInt(e.key, 10);
                const chip = document.querySelector(`.interval-chip[data-sec="${sec}"]`);
                if (chip) chip.click();
            }
        });
    }

    // -------------------------------------------------------------------------
    // Initialization
    // -------------------------------------------------------------------------
    function init() {
        // Load saved theme
        const savedTheme = localStorage.getItem('poker_rng_theme') || 'emerald';
        setTheme(savedTheme);

        // Load saved mute
        const savedMute = localStorage.getItem('poker_rng_mute') === 'true';
        if (savedMute) {
            state.isMuted = true;
            elements.soundIconOn.classList.add('hidden');
            elements.soundIconOff.classList.remove('hidden');
        }

        // Check if opened as HUD popup via URL params
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('mode') === 'hud' || window.innerWidth < 450) {
            toggleHudMode(true);
        }

        // Setup Event Listeners
        setupEventListeners();

        // Initial setup
        setThreshold(50);
        executeRoll();
    }

    // Boot on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
