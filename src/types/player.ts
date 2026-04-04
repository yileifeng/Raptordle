export type Conference = 'East' | 'West';

export type NBAPlayer = {
    id: string;
    name: string;
    team: string;
    conference: Conference;
    division: string;
    position: string;
    heightInches: number;
    age: number;
    jersey: number | null;
    imageUrl?: string;
};
