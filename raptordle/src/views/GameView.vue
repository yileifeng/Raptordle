<script setup lang="ts">
import { computed, ref } from 'vue';
import { getFeedback, isWinningFeedback } from '@/utils/game';
import type { NBAPlayer } from '@/types/player';
import type { GuessFeedback, FeedbackStatus } from '@/types/game';

import HiddenPlayerCard from '@/components/HiddenPlayerCard.vue';
import playersData from '@/data/players.json';

type GuessRow = {
    player: NBAPlayer;
    feedback: GuessFeedback;
};

const MAX_GUESSES = 8;

const query = ref('');
const guessedRows = ref<GuessRow[]>([]);

const players = playersData as NBAPlayer[];
const targetPlayer = ref(players[Math.floor(Math.random() * players.length)]);
const revealPlayer = computed(() => gameOver.value);

const gameWon = computed(() => {
    return guessedRows.value.some((row) => isWinningFeedback(row.feedback));
});

const gameLost = computed(() => {
    return !gameWon.value && guessedRows.value.length >= MAX_GUESSES;
});

const gameOver = computed(() => {
    return gameWon.value || gameLost.value;
});

const guessedIds = computed(() => {
    return new Set(guessedRows.value.map((row) => row.player.id));
});

const remainingGuesses = computed(() => {
    return Math.max(0, MAX_GUESSES - guessedRows.value.length);
});

const getDirectionalHint = (guess: number | null, target: number | null): string => {
    if (guess == null || target == null) return '';
    if (guess === target) return '✓';
    return guess < target ? '↑' : '↓';
};

const getJerseyDisplay = (player: NBAPlayer): string => {
    return player.jersey == null ? '—' : `#${player.jersey}`;
};

const getHeightHint = (player: NBAPlayer): string => {
    return getDirectionalHint(player.heightInches, targetPlayer.value.heightInches);
};

const getAgeHint = (player: NBAPlayer): string => {
    return getDirectionalHint(player.age, targetPlayer.value.age);
};

const getJerseyHint = (player: NBAPlayer): string => {
    return getDirectionalHint(player.jersey, targetPlayer.value.jersey);
};

const statusMessage = computed(() => {
    if (gameWon.value) {
        return `You got it! The hidden player is ${targetPlayer.value.name}.`;
    }

    if (gameLost.value) {
        return `Out of guesses. The hidden player was ${targetPlayer.value.name}.`;
    }

    return `${remainingGuesses.value} guesses remaining.`;
});

const filteredPlayers = computed(() => {
    const trimmedQuery = query.value.trim().toLowerCase();

    return playersData
        .filter((player) => !guessedIds.value.has(player.id))
        .filter((player) => {
            if (!trimmedQuery || gameOver.value) return false;
            return player.name.toLowerCase().includes(trimmedQuery);
        })
        .slice(0, 8);
});

const submitGuess = (player: NBAPlayer) => {
    if (gameOver.value) return;

    guessedRows.value.push({
        player,
        feedback: getFeedback(player, targetPlayer.value)
    });

    query.value = '';
};

const getRandomPlayer = (excludeId?: string): NBAPlayer => {
    if (players.length === 1) return players[0];

    let nextPlayer = players[Math.floor(Math.random() * players.length)];

    while (excludeId && nextPlayer.id === excludeId) {
        nextPlayer = players[Math.floor(Math.random() * players.length)];
    }

    return nextPlayer;
};

const resetRound = () => {
    const previousId = targetPlayer.value.id;
    guessedRows.value = [];
    query.value = '';
    targetPlayer.value = getRandomPlayer(previousId);
};

const formatHeight = (heightInches: number): string => {
    const feet = Math.floor(heightInches / 12);
    const inches = heightInches % 12;
    return `${feet}'${inches}"`;
};

const feedbackClass = (status: FeedbackStatus): string => {
    if (status === 'correct') return 'is-correct';
    if (status === 'close') return 'is-close';
    return 'is-wrong';
};
</script>

<template>
    <div class="game-container">
        <h1>Raptordle</h1>

        <HiddenPlayerCard :image-url="targetPlayer.imageUrl" :revealed="revealPlayer" />

        <div class="top-panel">
            <div class="top-stats">
                <div class="pill">Guesses: {{ guessedRows.length }}/{{ MAX_GUESSES }}</div>
                <div class="pill">Remaining: {{ remainingGuesses }}</div>
                <div class="pill" v-if="gameWon">Win</div>
                <div class="pill" v-else-if="gameLost">Loss</div>
            </div>

            <!-- For infinite plays -->
            <button type="button" class="reset-button" @click="resetRound">Reset Round</button>
        </div>

        <div class="guess-section compact">
            <input
                v-model="query"
                class="guess-input"
                type="text"
                placeholder="Type a player name..."
                :disabled="gameOver"
            />

            <div v-if="filteredPlayers.length > 0" class="results-list">
                <button
                    v-for="player in filteredPlayers"
                    :key="player.id"
                    class="result-item"
                    type="button"
                    @click="submitGuess(player)"
                >
                    {{ player.name }} — {{ player.team }} — {{ player.position }}
                </button>
            </div>
        </div>

        <div class="status-message" v-if="gameWon || gameLost">
            {{ statusMessage }}
        </div>

        <div class="guesses-section">
            <h2>Guesses</h2>

            <p v-if="guessedRows.length === 0">No guesses yet.</p>

            <div v-else class="guess-table-wrap">
                <div class="guess-table">
                    <div class="guess-row guess-header">
                        <div class="guess-cell name-col">Player</div>
                        <div class="guess-cell">Team</div>
                        <div class="guess-cell">Conf</div>
                        <div class="guess-cell">Division</div>
                        <div class="guess-cell">Pos</div>
                        <div class="guess-cell">Height</div>
                        <div class="guess-cell">Age</div>
                        <div class="guess-cell">Jersey</div>
                    </div>

                    <div v-for="row in guessedRows" :key="row.player.id" class="guess-row">
                        <div class="guess-cell name-col player-name-cell">
                            {{ row.player.name }}
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.team)">
                            <span class="cell-label">Team</span>
                            <span>{{ row.player.team }}</span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.conference)">
                            <span class="cell-label">Conf</span>
                            <span>{{ row.player.conference }}</span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.division)">
                            <span class="cell-label">Division</span>
                            <span>{{ row.player.division }}</span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.position)">
                            <span class="cell-label">Pos</span>
                            <span>{{ row.player.position }}</span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.height)">
                            <span class="cell-label">Height</span>
                            <span>
                                {{ formatHeight(row.player.heightInches) }}
                                {{ row.feedback.height === 'correct' ? '✓' : getHeightHint(row.player) }}
                            </span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.age)">
                            <span class="cell-label">Age</span>
                            <span>
                                {{ row.player.age }}
                                {{ row.feedback.age === 'correct' ? '✓' : getAgeHint(row.player) }}
                            </span>
                        </div>

                        <div class="guess-cell" :class="feedbackClass(row.feedback.jersey)">
                            <span class="cell-label">Jersey</span>
                            <span>
                                {{ getJerseyDisplay(row.player) }}
                                {{ row.feedback.jersey === 'correct' ? '✓' : getJerseyHint(row.player) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.top-panel {
    max-width: 900px;
    margin: 20px auto 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.top-stats {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.guess-section.compact {
    max-width: 900px;
    margin: 14px auto 0;
    position: relative;
}

.status-message {
    max-width: 900px;
    margin: 12px auto 0;
    padding: 12px 14px;
    border: 1px solid #d4d4d8;
    border-radius: 12px;
    background: #fafafa;
    text-align: left;
}

.game-container {
    max-width: 900px;
    margin: 40px auto;
    text-align: center;
}

.status-bar {
    max-width: 700px;
    margin: 24px auto 0;
    padding: 14px 16px;
    border: 1px solid #d4d4d8;
    border-radius: 12px;
    background: #fafafa;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}

.reset-button {
    border: 1px solid #d4d4d8;
    background: white;
    border-radius: 10px;
    padding: 8px 12px;
    cursor: pointer;
}

.reset-button:hover {
    background: #f4f4f5;
}

.guess-input {
    width: 100%;
    padding: 12px 14px;
    font-size: 16px;
    border: 1px solid #d4d4d8;
    border-radius: 10px;
    outline: none;
}

.guess-input:focus {
    border-color: #18181b;
}

.guess-input:disabled {
    background: #f4f4f5;
    cursor: not-allowed;
}

.results-list {
    margin-top: 8px;
    border: 1px solid #d4d4d8;
    border-radius: 10px;
    overflow: hidden;
    background: white;
    text-align: left;
}

.result-item {
    display: block;
    width: 100%;
    padding: 12px 14px;
    border: none;
    background: white;
    text-align: left;
    cursor: pointer;
    font-size: 15px;
}

.result-item:hover {
    background: #f4f4f5;
}

.meta-row {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
}

.pill {
    border: 1px solid #d4d4d8;
    border-radius: 999px;
    padding: 8px 14px;
    background: white;
    font-size: 14px;
}

.guesses-section {
    margin-top: 28px;
    text-align: left;
}

.guess-table-wrap {
    border: 1px solid #d4d4d8;
    border-radius: 14px;
    background: white;
}

.guess-table {
    min-width: 980px;
}

.guess-row {
    display: grid;
    grid-template-columns: 190px repeat(7, minmax(90px, 1fr));
    border-bottom: 1px solid #e4e4e7;
}

.guess-row:last-child {
    border-bottom: none;
}

.guess-header {
    background: #f4f4f5;
    font-weight: 700;
}

.guess-cell {
    padding: 10px 12px;
    border-right: 1px solid #e4e4e7;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    min-height: 58px;
}

.guess-cell:last-child {
    border-right: none;
}

.name-col {
    font-weight: 600;
    background: #fafafa;
}

.player-name-cell {
    justify-content: center;
}

.cell-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #71717a;
}

.is-correct {
    background: #dcfce7;
    border-color: #86efac;
}

.is-close {
    background: #fef3c7;
    border-color: #fcd34d;
}

.is-wrong {
    background: #f4f4f5;
    border-color: #d4d4d8;
}

.guess-cards {
    display: grid;
    gap: 16px;
}

.guess-card {
    border: 1px solid #d4d4d8;
    border-radius: 12px;
    padding: 16px;
}

.feedback-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 12px;
}

.feedback-cell {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 12px;
    border: 1px solid #e4e4e7;
    border-radius: 10px;
}
</style>
