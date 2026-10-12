import express from 'express';
import fs from 'fs';
import path from 'path';

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
const DATA_DIR = path.resolve(process.cwd(), 'data');
const DATA_FILE = path.resolve(DATA_DIR, 'catan_matches.json');
const DEFAULT_DATA_FILE = path.resolve(DATA_DIR, 'default_matches.json');

app.use(express.json({ limit: '10mb' }));

function getDefaultMatches(): any[] {
  try {
    if (fs.existsSync(DEFAULT_DATA_FILE)) {
      return JSON.parse(fs.readFileSync(DEFAULT_DATA_FILE, 'utf-8'));
    }
  } catch (err) {
    console.error('Error reading default matches:', err);
  }
  return [];
}

// Ensure data directory and initial file exist
function getMatches(): any[] {
  try {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    if (!fs.existsSync(DATA_FILE)) {
      const defaults = getDefaultMatches();
      fs.writeFileSync(DATA_FILE, JSON.stringify(defaults, null, 2), 'utf-8');
      return defaults;
    }
    const raw = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    console.error('Error reading matches data:', err);
    return getDefaultMatches();
  }
}

function saveMatches(matches: any[]): boolean {
  try {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    fs.writeFileSync(DATA_FILE, JSON.stringify(matches, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error('Error writing matches data:', err);
    return false;
  }
}

// API Endpoints
app.get('/api/matches', (_req, res) => {
  const matches = getMatches();
  res.json(matches);
});

app.post('/api/matches', (req, res) => {
  const match = req.body;
  if (!match || !match.season || !match.scenarioId || !Array.isArray(match.playerResults)) {
    return res.status(400).json({ error: 'Dados da partida incompletos ou inválidos.' });
  }

  const matches = getMatches();
  const existingIdx = matches.findIndex((m: any) => m.id === match.id);
  if (existingIdx >= 0) {
    matches[existingIdx] = match;
  } else {
    matches.unshift(match);
  }

  saveMatches(matches);
  res.status(201).json(match);
});

app.put('/api/matches/:id', (req, res) => {
  const matchId = req.params.id;
  const updatedMatch = req.body;
  const matches = getMatches();
  const idx = matches.findIndex((m: any) => m.id === matchId);

  if (idx === -1) {
    return res.status(404).json({ error: 'Partida não encontrada.' });
  }

  matches[idx] = updatedMatch;
  saveMatches(matches);
  res.json(updatedMatch);
});

app.delete('/api/matches/:id', (req, res) => {
  const matchId = req.params.id;
  let matches = getMatches();
  const initialLen = matches.length;
  matches = matches.filter((m: any) => m.id !== matchId);

  if (matches.length === initialLen) {
    return res.status(404).json({ error: 'Partida não encontrada.' });
  }

  saveMatches(matches);
  res.json({ success: true, id: matchId });
});

app.post('/api/matches/reset', (_req, res) => {
  const defaults = getDefaultMatches();
  saveMatches(defaults);
  res.json({ success: true, matches: defaults });
});

// CSV Export Endpoint
app.get('/api/export/csv', (_req, res) => {
  const matches = getMatches();
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
    'Observações'
  ];

  const rows: string[] = [headers.join(',')];

  for (const m of matches) {
    for (const p of m.playerResults) {
      const row = [
        `"${m.id}"`,
        `"${m.date}"`,
        `"${m.season}"`,
        `"${(m.scenarioName || '').replace(/"/g, '""')}"`,
        m.targetVP,
        m.is5to6Players ? 'Sim' : 'Não',
        `"${(m.winnerName || '').replace(/"/g, '""')}"`,
        `"${(p.playerName || '').replace(/"/g, '""')}"`,
        p.isOfficial ? 'Sim' : 'Não',
        p.vp,
        p.normalizedVP,
        p.balancedVPPercent,
        p.isWinner ? 'Sim' : 'Não',
        `"${(m.notes || '').replace(/"/g, '""')}"`
      ];
      rows.push(row.join(','));
    }
  }

  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename="torneio_catan_4_estacoes.csv"');
  res.send('\uFEFF' + rows.join('\r\n'));
});

async function startServer() {
  const distPath = path.resolve(process.cwd(), 'dist');
  const distExists = fs.existsSync(distPath) && fs.existsSync(path.resolve(distPath, 'index.html'));
  const isProduction = process.env.NODE_ENV === 'production' || distExists;

  if (isProduction && distExists) {
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.resolve(distPath, 'index.html'));
    });
  } else {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Torneio Catan server running on port ${PORT} (mode: ${isProduction ? 'production' : 'development'})`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});
