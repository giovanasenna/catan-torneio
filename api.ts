import { INITIAL_MATCHES } from './constants';
import { Match } from './types';

const LOCAL_STORAGE_KEY = 'catan_tournament_matches_v1';

export async function fetchMatches(): Promise<Match[]> {
  try {
    const res = await fetch('/api/matches');
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
        return data;
      }
    }
  } catch (err) {
    console.warn('Backend fetch failed, using local storage fallback:', err);
  }

  // Fallback to localStorage or initial matches
  const cached = localStorage.getItem(LOCAL_STORAGE_KEY);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch {
      // ignore parse error
    }
  }

  return INITIAL_MATCHES;
}

export async function saveMatch(match: Match): Promise<Match> {
  // Update local cache first
  const current = await fetchMatches();
  const existingIdx = current.findIndex(m => m.id === match.id);
  const updated = [...current];
  if (existingIdx >= 0) {
    updated[existingIdx] = match;
  } else {
    updated.unshift(match);
  }
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(updated));

  try {
    const res = await fetch('/api/matches', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(match),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend save failed, saved in local storage:', err);
  }

  return match;
}

export async function deleteMatch(matchId: string): Promise<boolean> {
  const current = await fetchMatches();
  const updated = current.filter(m => m.id !== matchId);
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(updated));

  try {
    const res = await fetch(`/api/matches/${matchId}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch (err) {
    console.warn('Backend delete failed, removed from local storage:', err);
    return true;
  }
}

export async function resetMatchesToInitial(): Promise<Match[]> {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(INITIAL_MATCHES));
  try {
    await fetch('/api/matches/reset', { method: 'POST' });
  } catch (err) {
    console.warn('Backend reset failed:', err);
  }
  return INITIAL_MATCHES;
}

export function exportMatchesToCSV(matches: Match[]): string {
  const headers = [
    'Partida_ID',
    'Data',
    'Estação',
    'Cenário',
    'Meta_PV',
    'Expansão_5_6',
    'Vencedor',
    'Jogador',
    'Oficial',
    'PV',
    'PV_Normalizado',
    'VP_Percent_Balanceado',
    'Venceu',
    'Observações',
  ];

  const rows: string[] = [headers.join(',')];

  for (const m of matches) {
    for (const p of m.playerResults) {
      const row = [
        `"${m.id}"`,
        `"${m.date}"`,
        `"${m.season}"`,
        `"${m.scenarioName.replace(/"/g, '""')}"`,
        m.targetVP,
        m.is5to6Players ? 'Sim' : 'Não',
        `"${m.winnerName.replace(/"/g, '""')}"`,
        `"${p.playerName.replace(/"/g, '""')}"`,
        p.isOfficial ? 'Sim' : 'Não',
        p.vp,
        p.normalizedVP,
        p.balancedVPPercent,
        p.isWinner ? 'Sim' : 'Não',
        `"${(m.notes || '').replace(/"/g, '""')}"`,
      ];
      rows.push(row.join(','));
    }
  }

  return '\uFEFF' + rows.join('\r\n');
}
