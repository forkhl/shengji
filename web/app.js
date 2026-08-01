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
let selected = [];
function cardsEqual(a, b) {
    return a.rank === b.rank && a.suit === b.suit;
}
function isSelected(card) {
    return selected.some((c) => cardsEqual(c, card));
}
function toggleCard(card) {
    if (isSelected(card)) {
        selected = selected.filter((c) => !cardsEqual(c, card));
    }
    else {
        selected = [...selected, card];
    }
    render();
}
// ---------------- actions ----------------
async function onNewGame() {
    selected = [];
    state = await apiPost("/api/new_game");
    render();
}
async function onMakeCall() {
    if (selected.length === 0) {
        alert("Select one or two cards first.");
        return;
    }
    state = await apiPost("/api/make_call", { cards: selected });
    selected = [];
    render();
}
async function onFinishCalling() {
    state = await apiPost("/api/finish_calling");
    selected = [];
    render();
}
async function onDiscardBottom() {
    if (!state)
        return;
    if (selected.length !== state.bottomCount) {
        alert(`Select exactly ${state.bottomCount} cards.`);
        return;
    }
    state = await apiPost("/api/discard_bottom", { cards: selected });
    selected = [];
    render();
}
async function onPlayMove() {
    if (selected.length === 0) {
        alert("Select cards to play first.");
        return;
    }
    state = await apiPost("/api/play_move", { cards: selected });
    selected = [];
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
    hand.forEach((card) => {
        const btn = el("button", "card-btn");
        btn.title = cardLabel(card);
        btn.appendChild(buildCardFace(card));
        if (isSelected(card))
            btn.classList.add("selected");
        btn.disabled = !selectable;
        if (selectable) {
            btn.addEventListener("click", () => toggleCard(card));
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
    const panel = el("div", "panel");
    panel.appendChild(el("h3", undefined, "Calling phase"));
    if (s.currentCall) {
        const p = el("div", undefined, `Current call: ${s.currentCall.callerName} called `);
        p.appendChild(renderCardChips(s.currentCall.cards));
        panel.appendChild(p);
    }
    panel.appendChild(el("div", "selection-count", `Selected: ${selected.length}`));
    panel.appendChild(renderHand(s.humanHand, true));
    const makeCallBtn = el("button", "action", "Make Call");
    makeCallBtn.addEventListener("click", onMakeCall);
    panel.appendChild(makeCallBtn);
    const finishBtn = el("button", "action", "Finish Calling");
    finishBtn.addEventListener("click", onFinishCalling);
    panel.appendChild(finishBtn);
    return panel;
}
function renderDiscardPanel(s) {
    const panel = el("div", "panel");
    panel.appendChild(el("h3", undefined, "Bury the bottom"));
    panel.appendChild(el("div", "selection-count", `Selected: ${selected.length} / ${s.bottomCount}`));
    panel.appendChild(renderHand(s.humanHand, true));
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
        s.currentTrick.forEach((m) => {
            const col = el("div", "trick-col");
            col.appendChild(el("div", "player-name", m.playerName));
            col.appendChild(renderCardChips(m.cards));
            row.appendChild(col);
        });
    }
    else {
        row.appendChild(el("div", undefined, "(no cards played yet)"));
    }
    panel.appendChild(row);
    const isHumanTurn = s.currentPlayerName === "You";
    panel.appendChild(el("div", undefined, `Current turn: ${(_a = s.currentPlayerName) !== null && _a !== void 0 ? _a : ""}`));
    panel.appendChild(renderHand(s.humanHand, isHumanTurn));
    if (isHumanTurn) {
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
