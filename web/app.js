"use strict";
// Sheng Ji frontend.
//
// This file contains NO game rules. It only:
//   - renders whatever GameState the server sends
//   - lets the user select cards from their own hand
//   - POSTs the selection to the server and re-renders with the response
//
// All legality checks, scoring, and rule logic live in the Python backend
// (round.py / trick.py / move.py / rules.py) via server.py.
// ---------------- API client ----------------
async function apiGet(path) {
    const res = await fetch(path);
    return (await res.json());
}
async function apiPost(path, body = {}) {
    const res = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    return (await res.json());
}
// ---------------- app state ----------------
let state = null;
// Selection is tracked by INDEX into state.humanHand, not by card value.
// With two decks, duplicate cards (same rank+suit) are common, and
// tracking by value made every copy of a duplicate toggle together.
let selectedIndices = [];
function isSelected(index) {
    return selectedIndices.includes(index);
}
function toggleIndex(index) {
    if (isSelected(index)) {
        selectedIndices = selectedIndices.filter((i) => i !== index);
    }
    else {
        selectedIndices = [...selectedIndices, index];
    }
    render();
}
function selectedCards() {
    if (!state)
        return [];
    return selectedIndices.map((i) => state.activeHand[i]);
}
// ---------------- actions ----------------
async function onNewGame() {
    selectedIndices = [];
    state = await apiPost("/api/new_game");
    render();
}
async function onCallingCall() {
    if (selectedIndices.length === 0) {
        alert("Select one or two cards first.");
        return;
    }
    state = await apiPost("/api/calling_action", { action: "call", cards: selectedCards() });
    selectedIndices = [];
    render();
}
async function onCallingPass() {
    state = await apiPost("/api/calling_action", { action: "pass", cards: [] });
    selectedIndices = [];
    render();
}
async function onDiscardBottom() {
    if (!state)
        return;
    if (selectedIndices.length !== state.bottomCount) {
        alert(`Select exactly ${state.bottomCount} cards.`);
        return;
    }
    state = await apiPost("/api/discard_bottom", { cards: selectedCards() });
    selectedIndices = [];
    render();
}
async function onPlayMove() {
    if (selectedIndices.length === 0) {
        alert("Select cards to play first.");
        return;
    }
    state = await apiPost("/api/play_move", { cards: selectedCards() });
    selectedIndices = [];
    render();
}
// ---------------- rendering ----------------
function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className)
        node.className = className;
    if (text !== undefined)
        node.textContent = text;
    return node;
}
function cardLabel(card) {
    return `${card.rank} of ${card.suit}`;
}
function suitSymbol(suit) {
    switch (suit) {
        case "Hearts":
            return "\u2665"; // ♥
        case "Diamonds":
            return "\u2666"; // ♦
        case "Clubs":
            return "\u2663"; // ♣
        case "Spades":
            return "\u2660"; // ♠
        case "Joker":
            return "\u2605"; // ★
        default:
            return suit;
    }
}
function isRedCard(card) {
    if (card.suit === "Hearts" || card.suit === "Diamonds")
        return true;
    if (card.suit === "Joker" && card.rank === "Big")
        return true;
    return false;
}
function cardCornerLabel(card) {
    if (card.suit === "Joker") {
        return card.rank === "Big" ? "BIG" : "SM";
    }
    return card.rank;
}
/** Builds a small playing-card-style visual for one card (no game logic). */
function buildCardFace(card) {
    const face = el("div", "card-face");
    face.classList.add(isRedCard(card) ? "card-red" : "card-black");
    if (card.suit === "Joker")
        face.classList.add("card-joker");
    face.appendChild(el("div", "card-corner", cardCornerLabel(card)));
    face.appendChild(el("div", "card-center", suitSymbol(card.suit)));
    face.appendChild(el("div", "card-corner card-corner-bottom", cardCornerLabel(card)));
    return face;
}
function renderCardChips(cards) {
    const wrap = el("div", "chip-row");
    cards.forEach((c) => {
        const chip = el("div", "card-chip");
        chip.appendChild(buildCardFace(c));
        wrap.appendChild(chip);
    });
    return wrap;
}
function renderHand(hand, selectable) {
    const wrap = el("div", "hand");
    hand.forEach((card, index) => {
        const btn = el("button", "card-btn");
        btn.title = cardLabel(card);
        btn.appendChild(buildCardFace(card));
        if (isSelected(index))
            btn.classList.add("selected");
        btn.disabled = !selectable;
        if (selectable) {
            btn.addEventListener("click", () => toggleIndex(index));
        }
        wrap.appendChild(btn);
    });
    return wrap;
}
function renderHeader(s) {
    var _a;
    const header = el("div", "header");
    header.appendChild(el("h2", undefined, "Sheng Ji"));
    header.appendChild(el("div", undefined, `Level: ${s.level}`));
    header.appendChild(el("div", undefined, `Trump: ${(_a = s.trumpSuit) !== null && _a !== void 0 ? _a : "(none called)"}`));
    header.appendChild(el("div", undefined, `Attacker points: ${s.attackerPoints}`));
    return header;
}
function renderHandSizes(s) {
    const wrap = el("div", "hand-sizes");
    s.handSizes.forEach((h) => {
        wrap.appendChild(el("span", undefined, `${h.name}: ${h.count} cards`));
    });
    return wrap;
}
function renderCallingPanel(s) {
    var _a;
    const panel = el("div", "panel reveal");
    panel.appendChild(el("h3", undefined, `Calling phase \u2014 ${(_a = s.activePlayerName) !== null && _a !== void 0 ? _a : ""}'s turn`));
    if (s.currentCall) {
        const p = el("div", undefined, `Current call: ${s.currentCall.callerName} called `);
        p.appendChild(renderCardChips(s.currentCall.cards));
        panel.appendChild(p);
    }
    panel.appendChild(el("div", "selection-count", `Selected: ${selectedIndices.length}`));
    panel.appendChild(renderHand(s.activeHand, true));
    const callBtn = el("button", "action", "Call");
    callBtn.addEventListener("click", onCallingCall);
    panel.appendChild(callBtn);
    const passBtn = el("button", "action", "Pass");
    passBtn.addEventListener("click", onCallingPass);
    panel.appendChild(passBtn);
    return panel;
}
function renderDiscardPanel(s) {
    var _a;
    const panel = el("div", "panel reveal");
    panel.appendChild(el("h3", undefined, `Bury the bottom \u2014 ${(_a = s.activePlayerName) !== null && _a !== void 0 ? _a : ""}`));
    panel.appendChild(el("div", "selection-count", `Selected: ${selectedIndices.length} / ${s.bottomCount}`));
    panel.appendChild(renderHand(s.activeHand, true));
    const buryBtn = el("button", "action", "Bury Selected Cards");
    buryBtn.addEventListener("click", onDiscardBottom);
    panel.appendChild(buryBtn);
    return panel;
}
function renderTrickPanel(s) {
    var _a;
    const panel = el("div", "panel");
    panel.appendChild(el("h3", undefined, "Current trick"));
    const row = el("div", "trick-row");
    if (s.currentTrick && s.currentTrick.length > 0) {
        s.currentTrick.forEach((m, i) => {
            const col = el("div", "trick-col reveal");
            // stagger each play's entrance slightly so they visibly appear
            // one at a time rather than all at once
            col.style.animationDelay = `${i * 60}ms`;
            col.appendChild(el("div", "player-name", m.playerName));
            col.appendChild(renderCardChips(m.cards));
            row.appendChild(col);
        });
    }
    else {
        row.appendChild(el("div", undefined, "(no cards played yet)"));
    }
    panel.appendChild(row);
    const canAct = s.activePlayerName !== null;
    panel.appendChild(el("div", undefined, `Current turn: ${(_a = s.activePlayerName) !== null && _a !== void 0 ? _a : ""}`));
    panel.appendChild(renderHand(s.activeHand, canAct));
    if (canAct) {
        const playBtn = el("button", "action", "Play Selected Cards");
        playBtn.addEventListener("click", onPlayMove);
        panel.appendChild(playBtn);
    }
    return panel;
}
function renderRoundSummary(summary) {
    const panel = el("div", "panel");
    panel.appendChild(el("h3", undefined, "Last round"));
    panel.appendChild(el("div", undefined, `Attacker points: ${summary.attackerPoints}`));
    panel.appendChild(el("div", undefined, `Defending team level: ${summary.defendingLevel}`));
    panel.appendChild(el("div", undefined, `Attacking team level: ${summary.attackingLevel}`));
    return panel;
}
function render() {
    const root = document.getElementById("root");
    if (!root || !state)
        return;
    root.innerHTML = "";
    const s = state;
    root.appendChild(renderHeader(s));
    if (s.message) {
        root.appendChild(el("div", "message", s.message));
    }
    root.appendChild(renderHandSizes(s));
    if (s.lastRoundSummary) {
        root.appendChild(renderRoundSummary(s.lastRoundSummary));
    }
    if (s.phase === "calling") {
        root.appendChild(renderCallingPanel(s));
    }
    else if (s.phase === "discard") {
        root.appendChild(renderDiscardPanel(s));
    }
    else if (s.phase === "trick") {
        root.appendChild(renderTrickPanel(s));
    }
    const newGameBtn = el("button", "action", "New Game");
    newGameBtn.addEventListener("click", onNewGame);
    root.appendChild(newGameBtn);
}
// ---------------- boot ----------------
async function boot() {
    state = await apiGet("/api/state");
    render();
}
boot();
