import { useState, useEffect } from 'react';
import { Header, NavigationTab } from './components/Header';
import { MobileBottomNav } from './components/MobileBottomNav';
import { LeaderboardTab } from './components/LeaderboardTab';
import { AnnualRankingTab } from './components/AnnualRankingTab';
import { ChartsTab } from './components/ChartsTab';
import { MatchHistoryTab } from './components/MatchHistoryTab';
import { VisitorsTab } from './components/VisitorsTab';
import { DataAndStreamlitTab } from './components/DataAndStreamlitTab';
import { MatchFormModal } from './components/MatchFormModal';
import { ShareModal } from './components/ShareModal';
import { Match } from './types';
import { deleteMatch, fetchMatches, resetMatchesToInitial, saveMatch } from './api';
import { CheckCircle2, Flame, Share2 } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavigationTab>('leaderboard');
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isMatchModalOpen, setIsMatchModalOpen] = useState<boolean>(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState<boolean>(false);
  const [editingMatch, setEditingMatch] = useState<Match | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    async function init() {
      try {
        const loaded = await fetchMatches();
        setMatches(loaded);
      } catch (err) {
        console.error('Failed to load matches:', err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleOpenNewMatch = () => {
    setEditingMatch(null);
    setIsMatchModalOpen(true);
  };

  const handleEditMatch = (match: Match) => {
    setEditingMatch(match);
    setIsMatchModalOpen(true);
  };

  const handleSaveMatch = async (matchToSave: Match) => {
    try {
      const saved = await saveMatch(matchToSave);
      setMatches(prev => {
        const idx = prev.findIndex(m => m.id === saved.id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = saved;
          return updated;
        }
        return [saved, ...prev];
      });
      showToast(
        editingMatch
          ? 'Partida atualizada com sucesso!'
          : `Partida salva! Vencedor: ${saved.winnerName}`
      );
    } catch (err) {
      console.error('Error saving match:', err);
      showToast('Erro ao salvar partida.');
    }
  };

  const handleDeleteMatch = async (matchId: string) => {
    try {
      await deleteMatch(matchId);
      setMatches(prev => prev.filter(m => m.id !== matchId));
      showToast('Partida removida do torneio.');
    } catch (err) {
      console.error('Error deleting match:', err);
      showToast('Erro ao excluir partida.');
    }
  };

  const handleResetMatches = async () => {
    try {
      const resetList = await resetMatchesToInitial();
      setMatches(resetList);
      showToast('Dados restaurados para o padrão inicial do torneio.');
    } catch (err) {
      console.error('Error resetting matches:', err);
    }
  };

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col font-sans selection:bg-amber-500 selection:text-stone-950">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-4 z-50 flex items-center gap-2 bg-stone-900 border border-amber-500/80 text-amber-300 px-4 py-2.5 rounded-xl shadow-xl animate-fade-in text-xs font-semibold">
          <CheckCircle2 size={16} className="text-amber-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Bar */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onOpenMatchModal={handleOpenNewMatch}
        onOpenShareModal={() => setIsShareModalOpen(true)}
      />

      {/* Hero Sub-header / Status strip */}
      <section className="bg-stone-900/60 border-b border-stone-800/80 px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-stone-400">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="flex items-center gap-1.5 text-stone-300 font-medium">
              <Flame size={14} className="text-amber-400" />
              Torneio das 4 Estações de Catan
            </span>
            <span>·</span>
            <span>Edição: <strong className="text-amber-300">Primavera</strong></span>
            <span>·</span>
            <span className="hidden sm:inline">4 Oficiais: Jhonata, Rodrigo, Giovana, Zhang</span>
          </div>

          <div className="flex items-center gap-3 text-[11px] text-stone-400">
            <button
              onClick={() => setIsShareModalOpen(true)}
              className="text-amber-400 hover:underline flex items-center gap-1 font-medium"
            >
              <Share2 size={12} />
              <span>Convidar amigos</span>
            </button>
            <span>·</span>
            <span className="font-mono">{matches.length} partidas registradas</span>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 sm:py-8 pb-24 md:pb-12">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-sm text-stone-400">
            Carregando dados do torneio...
          </div>
        ) : (
          <>
            {activeTab === 'leaderboard' && (
              <LeaderboardTab
                matches={matches}
                onOpenMatchModal={handleOpenNewMatch}
              />
            )}

            {activeTab === 'annual' && (
              <AnnualRankingTab matches={matches} />
            )}

            {activeTab === 'charts' && (
              <ChartsTab matches={matches} />
            )}

            {activeTab === 'history' && (
              <MatchHistoryTab
                matches={matches}
                onEditMatch={handleEditMatch}
                onDeleteMatch={handleDeleteMatch}
                onOpenNewMatch={handleOpenNewMatch}
              />
            )}

            {activeTab === 'visitors' && (
              <VisitorsTab matches={matches} />
            )}

            {activeTab === 'data' && (
              <DataAndStreamlitTab
                matches={matches}
                onResetMatches={handleResetMatches}
              />
            )}
          </>
        )}
      </main>

      {/* Match Registration & Edit Modal */}
      <MatchFormModal
        isOpen={isMatchModalOpen}
        onClose={() => setIsMatchModalOpen(false)}
        onSave={handleSaveMatch}
        matchToEdit={editingMatch}
      />

      {/* Share / QR Code Modal */}
      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
      />

      {/* Mobile Fixed Bottom Navigation for Smartphones */}
      <MobileBottomNav
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onOpenMatchModal={handleOpenNewMatch}
        onOpenShareModal={() => setIsShareModalOpen(true)}
      />
    </div>
  );
}
