export type Season = 'Inverno' | 'Primavera' | 'Verão' | 'Outono';

export interface OfficialPlayer {
  id: string;
  name: string;
  colorName: string;
  colorHex: string;
  colorText: string;
  borderColor: string;
  isOfficial: boolean;
}

export interface ScenarioDefinition {
  id: string;
  name: string;
  category: 'Base' | 'Navegantes' | 'Personalizado';
  scenarioNumber?: number;
  defaultVP: number;
  description: string;
}

export interface MatchPlayerResult {
  playerId: string;
  playerName: string;
  isOfficial: boolean;
  playerColorHex: string;
  vp: number;
  // Computed statistical metrics
  normalizedVP: number;       // vp / targetVP
  balancedVPPercent: number;  // (vp / totalTableVP) * (numPlayers / 4) * 100
  isWinner: boolean;
}

export interface Match {
  id: string;
  date: string; // YYYY-MM-DD
  season: Season;
  scenarioId: string;
  scenarioName: string;
  targetVP: number;
  notes?: string;
  is5to6Players: boolean;
  playerResults: MatchPlayerResult[];
  winnerId: string;
  winnerName: string;
  createdAt: string;
}

export interface PlayerStanding {
  playerId: string;
  playerName: string;
  isOfficial: boolean;
  playerColorHex: string;
  matchesPlayed: number;
  wins: number;
  totalVP: number;
  avgVP: number;
  winRate: number; // in %
  avgBalancedVPPercent: number; // in %
  highestVP: number;
  rank: number;
}

export interface AnnualStanding {
  playerId: string;
  playerName: string;
  colorHex: string;
  pointsBySeason: Record<Season, number>;
  totalAnnualPoints: number;
  seasonRanks: Record<Season, number | null>;
  rank: number;
}
