import type { NBAPlayer } from '@/types/player';

const TIME_ZONE = 'America/Toronto';

const getTodayKeyEST = () => {
    const formatter = new Intl.DateTimeFormat('en-CA', {
        timeZone: TIME_ZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });

    return formatter.format(new Date()); // "YYYY-MM-DD"
};

const hashString = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
    }
    return hash;
};

export const getDailyRandomPlayer = (players: NBAPlayer[]) => {
    const dayKey = getTodayKeyEST();
    const seed = hashString(dayKey);

    const index = seed % players.length;

    return {
        player: players[index],
        dayKey
    };
};

export const getMsUntilNextMidnightEST = () => {
    const now = new Date();

    const formatter = new Intl.DateTimeFormat('en-CA', {
        timeZone: TIME_ZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });

    const parts = formatter.formatToParts(now);

    const year = Number(parts.find((p) => p.type === 'year')?.value);
    const month = Number(parts.find((p) => p.type === 'month')?.value);
    const day = Number(parts.find((p) => p.type === 'day')?.value);

    const nextMidnightUTC = Date.UTC(year, month - 1, day + 1);

    return Math.max(1000, nextMidnightUTC - Date.now());
};
