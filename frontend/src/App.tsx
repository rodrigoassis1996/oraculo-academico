import { useEffect, useState } from 'react';
import { App as AntdApp, Card } from 'antd';
import { Sparkles, Plus } from 'lucide-react';
import { useAppStore } from './store/useAppStore';
import { useSession } from './api/queries';
import { AppShell } from './components/layout/AppShell';
import { AgentChatInterface } from './components/features/Chat';
import { BriefingWizard } from './components/features/BriefingWizard';

function AppContent() {
  const { sessionId, setSessionId, setAgenteAtivo, setRagStats, documentos, setActiveDocId } = useAppStore();
  const [showWizard, setShowWizard] = useState(false);

  // Inicializa sessão se não houver
  const { data: sessionData, isLoading } = useSession(sessionId || undefined);

  useEffect(() => {
    if (sessionData && !sessionId) {
      setSessionId(sessionData.session_id);
    }
    if (sessionData) {
      setAgenteAtivo(sessionData.agente_ativo);
      if (sessionData.active_doc_id) {
        setActiveDocId(sessionData.active_doc_id);
      }
      if (sessionData.rag_stats) {
        setRagStats(sessionData.rag_stats);
      }
    }
  }, [sessionData, sessionId, setSessionId, setAgenteAtivo, setRagStats]);

  if (isLoading) {
    return (
      <AppShell>
        <Card loading title="Iniciando plataforma acadêmica..." />
      </AppShell>
    );
  }

  if (documentos.length === 0) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[70vh] py-20 px-4">
          <div className="w-24 h-24 bg-white rounded-[2rem] shadow-2xl shadow-primary-500/10 flex items-center justify-center mb-8 relative border border-slate-100">
            <Sparkles size={44} className="text-primary-500" />
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center shadow-lg border-4 border-slate-50">
              <Plus size={16} className="text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900 mb-3 tracking-tight">Pronto para começar?</h2>
          <p className="text-slate-500 text-center max-w-sm mb-10 leading-relaxed font-medium">
            Carregue seus materiais de referência na barra lateral para que eu possa ajudá-lo a estruturar seu trabalho acadêmico.
          </p>
          <div className="bg-white/50 backdrop-blur-sm self-stretch max-w-md mx-auto text-slate-400 text-xs font-semibold px-6 py-4 rounded-2xl border border-slate-200/60 italic shadow-sm text-center">
            "O conhecimento começa com a organização das fontes."
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      {showWizard ? (
        <BriefingWizard onComplete={() => setShowWizard(false)} />
      ) : (
        <div className="h-full flex flex-col">
          <AgentChatInterface />
        </div>
      )}
    </AppShell>
  );
}

function App() {
  return (
    <AntdApp>
      <AppContent />
    </AntdApp>
  );
}

export default App;
