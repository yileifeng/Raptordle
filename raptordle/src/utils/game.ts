import type { NBAPlayer } from '@/types/player';
import type { GuessFeedback, FeedbackStatus } from '@/types/game';

function compareNumber(guess: number | null, target: number | null, closeDiff = 1): FeedbackStatus {
    if (guess == null || target == null) return 'wrong';
    if (guess === target) return 'correct';
    if (Math.abs(guess - target) <= closeDiff) return 'close';
    return 'wrong';
}

function comparePosition(guess: string, target: string): FeedbackStatus {
    if (guess === target) return 'correct';

    const guessParts = new Set(
        guess
            .split('-')
            .map((value) => value.trim())
            .filter(Boolean)
    );

    const targetParts = new Set(
        target
            .split('-')
            .map((value) => value.trim())
            .filter(Boolean)
    );

    for (const part of guessParts) {
        if (targetParts.has(part)) {
            return 'close';
        }
    }

    return 'wrong';
}

export function getFeedback(guess: NBAPlayer, target: NBAPlayer): GuessFeedback {
    return {
        team: guess.team === target.team ? 'correct' : 'wrong',
        conference: guess.conference === target.conference ? 'correct' : 'wrong',
        division: guess.division === target.division ? 'correct' : 'wrong',
        position: comparePosition(guess.position, target.position),
        height: compareNumber(guess.heightInches, target.heightInches, 1),
        age: compareNumber(guess.age, target.age, 1),
        jersey: compareNumber(guess.jersey, target.jersey, 1)
    };
}

export function isWinningFeedback(feedback: GuessFeedback): boolean {
    return Object.values(feedback).every((value) => value === 'correct');
}
