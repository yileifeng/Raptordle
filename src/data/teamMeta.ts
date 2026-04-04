export type TeamMeta = {
    conference: 'East' | 'West';
    division: string;
};

export const TEAM_META: Record<string, TeamMeta> = {
    Hawks: { conference: 'East', division: 'Southeast' },
    Celtics: { conference: 'East', division: 'Atlantic' },
    Nets: { conference: 'East', division: 'Atlantic' },
    Hornets: { conference: 'East', division: 'Southeast' },
    Bulls: { conference: 'East', division: 'Central' },
    Cavaliers: { conference: 'East', division: 'Central' },
    Mavericks: { conference: 'West', division: 'Southwest' },
    Nuggets: { conference: 'West', division: 'Northwest' },
    Pistons: { conference: 'East', division: 'Central' },
    Warriors: { conference: 'West', division: 'Pacific' },
    Rockets: { conference: 'West', division: 'Southwest' },
    Pacers: { conference: 'East', division: 'Central' },
    Clippers: { conference: 'West', division: 'Pacific' },
    Lakers: { conference: 'West', division: 'Pacific' },
    Grizzlies: { conference: 'West', division: 'Southwest' },
    Heat: { conference: 'East', division: 'Southeast' },
    Bucks: { conference: 'East', division: 'Central' },
    Timberwolves: { conference: 'West', division: 'Northwest' },
    Pelicans: { conference: 'West', division: 'Southwest' },
    Knicks: { conference: 'East', division: 'Atlantic' },
    Thunder: { conference: 'West', division: 'Northwest' },
    Magic: { conference: 'East', division: 'Southeast' },
    Sixers: { conference: 'East', division: 'Atlantic' },
    Suns: { conference: 'West', division: 'Pacific' },
    'Trail Blazers': { conference: 'West', division: 'Northwest' },
    Kings: { conference: 'West', division: 'Pacific' },
    Spurs: { conference: 'West', division: 'Southwest' },
    Raptors: { conference: 'East', division: 'Atlantic' },
    Jazz: { conference: 'West', division: 'Northwest' },
    Wizards: { conference: 'East', division: 'Southeast' }
};
