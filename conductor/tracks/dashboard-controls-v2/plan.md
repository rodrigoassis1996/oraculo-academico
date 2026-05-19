# Plano: Dashboard — Controles Interativos e View de Tabela

## Status: [~] Em Progresso

---

## Fase 1 — Fundação: Tipos e Hook
- [x] Task 1.1: Adicionar ao frontend/src/types/index.ts:
export type OrdemOpcao = 'recentes' | 'antigos' | 'nome-az' | 'nome-za' | 'etapa'
export type ViewMode = 'grid' | 'lista'

- [x] Task 1.2: Criar frontend/src/hooks/useClickOutside.ts
Hook que recebe uma ref e um callback, e chama o callback quando o usuário
clica fora do elemento referenciado. Usar useEffect com addEventListener
em document para detectar mousedown fora da ref.
Exportação nomeada: export function useClickOutside

Verificação da Fase 1:
- npm run build sem erros

---

## Fase 2 — Componentes de Dropdown
- [ ] Task 2.1: Criar frontend/src/components/ui/StatusFilterPanel.tsx

Referência: HTML "Dashboard — Cards — Filtro de status (painel aberto)"
Extrair apenas o dropdown panel (não o botão pai):

Props:
  statusSelecionado: StatusEtapa | null
  onAplicar: (status: StatusEtapa | null) => void
  onFechar: () => void

Estado interno: selecionadoLocal (cópia do statusSelecionado para controle do painel)

Estrutura (dropdown flutuante):
  position: absolute, top-[calc(100%+6px)], right-0, w-[240px], z-[100]
  bg-white, rounded-[10px], shadow, border border-gray-100

  Header: span "Filtrar por Status" text-[11px] font-bold text-gray-400 uppercase

  Lista de opções (div por opção):
    checkbox 4x4 (border-gray-300, checked = bg-amber-500 rounded)
    dot colorido (mesmo mapeamento de cores do StatusBadge)
    label text-sm

  Opções: Todas (sem dot), Rascunho, Etapa 1: Contexto, Etapa 2: Revisão,
          Etapa 3: Metodologia, Etapa 4: Escrita
  Opção selecionada: bg-amber-50, checkbox âmbar preenchido com check branco

  Footer: div com justify-between
    button "Limpar" (ghost, onClick → selecionadoLocal = null)
    button "Aplicar" px-4 py-2 bg-amber-500 text-white rounded-lg
      onClick → onAplicar(selecionadoLocal) + onFechar()

- [ ] Task 2.2: Criar frontend/src/components/ui/SortDropdown.tsx

Referência: HTML "Dashboard — Cards — Filtro de ordenação (dropdown aberto)"

Props:
  valorAtual: OrdemOpcao
  onSelecionar: (opcao: OrdemOpcao) => void
  onFechar: () => void

Estrutura (dropdown flutuante):
  position: absolute, top-[calc(100%+6px)], left-0, w-[220px], z-[100]
  bg-white, rounded-[10px], shadow, py-1

  Header: "ORDENAR POR" text-[11px] font-bold text-gray-500 uppercase px-4 pt-3 pb-2

  5 opções: cada uma tem radio button + label + ícone à direita
    recentes → "Mais recentes" + arrow_downward
    antigos  → "Mais antigos" + arrow_upward
    nome-az  → "Nome (A → Z)" + sort_by_alpha
    nome-za  → "Nome (Z → A)" + sort_by_alpha
    etapa    → "Etapa atual" + account_tree

  Radio selecionado: w-4 h-4 rounded-full border-2 border-primary-fixed-dim
    com ponto interno w-1.5 h-1.5 bg-primary-fixed-dim
  Radio não selecionado: w-4 h-4 rounded-full border-2 border-gray-300

  onClick em cada opção → onSelecionar(opcao) + onFechar()

- [ ] Task 2.3: Criar frontend/src/components/ui/UserMenuDropdown.tsx

Referência: HTML "Menu — Usuário Administrador" e "Menu — Usuário Comum"

Props:
  isAdmin: boolean
  nomeUsuario: string
  emailUsuario: string
  onFechar: () => void

Estrutura:
  position: absolute, right-0, top-[calc(100%+8px)], w-64
  bg-white, rounded-2xl, shadow-xl, border border-gray-100, z-50, overflow-hidden

  Header (p-4, border-b border-gray-100):
    avatar w-8 h-8 rounded-full bg-primary-container text-primary-fixed-dim (iniciais)
    nome (font-semibold text-sm) + email (text-xs text-gray-500)

  Seção de ações (p-2):
    item "Meu Perfil" → ícone 👤
    item "Preferências da Conta" → ícone ⚙️

  SE isAdmin === true:
    separator (border-t border-gray-100)
    label "ADMINISTRAÇÃO" (text-xs font-bold text-gray-400 uppercase px-3 pt-2 pb-1)
    item "Motor da IA (Blocos & Pontos)" → ícone 🧠
    item "Gestão de Usuários" → ícone 🛡️
    item "Logs do Sistema" → ícone 📊

  separator (border-t border-gray-100)
  item "Sair da conta" → ícone 🚪
    className: hover:bg-red-50 hover:text-red-600

  Cada item: flex items-center gap-2 px-3 py-2 text-sm text-gray-700
             hover:bg-gray-50 rounded-lg cursor-pointer transition-colors

Verificação da Fase 2:
- npm run build sem erros de TypeScript
- Nenhum import de antd

---

## Fase 3 — Componentes de Tabela e CSS
- [ ] Task 3.1: Adicionar ao frontend/src/index.css (após as classes existentes):

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton-shimmer {
  background: linear-gradient(90deg, #E5E7EB 25%, #F3F4F6 50%, #E5E7EB 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
}

- [ ] Task 3.2: Criar frontend/src/components/ui/ProjectTableRow.tsx

Referência: HTML "Dashboard — Tabela — Lista em tabela" (linhas de projeto)

Props:
  projeto: Projeto
  isAlternate: boolean (controla bg-white vs bg-[#f7f9fc])
  onClick?: () => void

Estrutura (div horizontal h-[52px]):
  className dinâmico: isAlternate ? 'bg-[#f7f9fc]' : 'bg-white'
  hover:bg-gray-50, transition-colors, cursor-pointer, rounded-lg, group

  Coluna STATUS (w-[200px]):
    StatusBadge já existente (importar de ProjectCard.tsx)

  Coluna PROJETO (flex-1):
    h3 font-body text-[#111827] text-[0.9rem] font-semibold truncate

  Coluna ÚLTIMA ATIVIDADE (w-[160px]):
    flex justify-end items-center gap-1.5
    ícone schedule text-[12px]
    data formatada text-[#9ca3af] text-[0.8rem]

Verificação da Fase 3:
- npm run build sem erros

---

## Fase 4 — Integração no DashboardPage
- [ ] Task 4.1: Atualizar DashboardPage.tsx com novos estados e lógica

Novos estados a adicionar:
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [ordenacao, setOrdenacao] = useState<OrdemOpcao>('recentes')
  const [statusDropdownAberto, setStatusDropdownAberto] = useState(false)
  const [sortDropdownAberto, setSortDropdownAberto] = useState(false)
  const [userMenuAberto, setUserMenuAberto] = useState(false)
  const [isAdmin] = useState(true)

Lógica de ordenação (aplicar após filtragem):
  const projetosOrdenados = [...projetosFiltrados].sort((a, b) => {
    switch(ordenacao) {
      case 'recentes': return new Date(b.dataCriacao).getTime() - new Date(a.dataCriacao).getTime()
      case 'antigos':  return new Date(a.dataCriacao).getTime() - new Date(b.dataCriacao).getTime()
      case 'nome-az':  return a.titulo.localeCompare(b.titulo, 'pt-BR')
      case 'nome-za':  return b.titulo.localeCompare(a.titulo, 'pt-BR')
      case 'etapa':    return a.etapaAtual - b.etapaAtual
      default:         return 0
    }
  })

- [ ] Task 4.2: Substituir botão Status por versão com dropdown real

Referência: HTML "Dashboard — Cards — Filtro de status (painel aberto)"

O botão Status agora é envolvido em div relative:
  <div className="relative" ref={statusRef}>
    <button onClick={() => setStatusDropdownAberto(!statusDropdownAberto)}>
      ...mesmo estilo atual (âmbar quando filtroAtivo, normal quando null)...
    </button>
    {statusDropdownAberto && (
      <StatusFilterPanel
        statusSelecionado={filtroAtivo}
        onAplicar={(status) => {
          setFiltroAtivo(status)
          setEstado(status ? 'filtrado' : 'populado')
        }}
        onFechar={() => setStatusDropdownAberto(false)}
      />
    )}
  </div>
Usar useClickOutside(statusRef, () => setStatusDropdownAberto(false))

- [ ] Task 4.3: Substituir botão Mais Recentes por versão com dropdown real

Referência: HTML "Dashboard — Cards — Filtro de ordenação (dropdown aberto)"

Botão mostra o label da opção atual (ex: "Mais recentes", "Nome (A → Z)")
Envolver em div relative com useClickOutside + SortDropdown

Labels para cada OrdemOpcao:
  recentes → "Mais recentes"
  antigos  → "Mais antigos"
  nome-az  → "Nome (A → Z)"
  nome-za  → "Nome (Z → A)"
  etapa    → "Etapa atual"

- [ ] Task 4.4: Substituir user chip por versão com menu dropdown

Referência: HTML "Menu — Usuário Administrador" e "Menu — Usuário Comum"

O div do user chip agora é envolvido em div relative:
  onClick no chip → setUserMenuAberto(!userMenuAberto)
  {userMenuAberto && (
    <UserMenuDropdown
      isAdmin={isAdmin}
      nomeUsuario="Ana"
      emailUsuario="ana.silva@universidade.edu"
      onFechar={() => setUserMenuAberto(false)}
    />
  )}
Usar useClickOutside(userMenuRef, () => setUserMenuAberto(false))

- [ ] Task 4.5: Implementar toggle grid/lista e view de tabela

Referência: HTML "Dashboard — Tabela — Lista em tabela"

O botão de toggle já existe (grid_view + format_list_bulleted).
Atualizar para:
  botão grid ativo quando viewMode === 'grid': bg-white shadow text-primary-fixed-dim
  botão lista ativo quando viewMode === 'lista': bg-white shadow text-amber-600
  onClick em cada botão → setViewMode('grid') ou setViewMode('lista')

Na renderização do conteúdo, quando viewMode === 'lista', substituir o grid por:

Estrutura da view tabela (baseada no HTML do Stitch):

<div className="flex flex-col w-full mb-12">
  {/* Cabeçalho de colunas */}
  <div className="flex items-center px-4 h-[36px] w-full">
    <div className="w-[200px] text-[0.72rem] text-[#9ca3af] font-medium tracking-widest uppercase">STATUS</div>
    <div className="flex-1 text-[0.72rem] text-[#9ca3af] font-medium tracking-widest uppercase">PROJETO</div>
    <div className="w-[160px] text-right text-[0.72rem] text-[#9ca3af] font-medium tracking-widest uppercase">ÚLTIMA ATIVIDADE</div>
  </div>

  {/* Botão Novo Projeto */}
  <button
    onClick={() => setModal('novo-projeto')}
    className="flex items-center px-4 mb-2 w-full h-[52px] rounded-[8px]
               border-[1.5px] border-dashed border-[rgba(245,158,11,0.40)]
               hover:bg-amber-50/30 transition-colors group">
    <div className="flex items-center justify-center w-full gap-2 text-amber-500">
      <span className="material-symbols-outlined text-[20px]">add</span>
      <span className="font-medium text-[0.9rem]">Novo Projeto</span>
    </div>
  </button>

  {/* Linhas de projeto */}
  <div className="flex flex-col">
    {projetosOrdenados.map((projeto, index) => (
      <ProjectTableRow
        key={projeto.id}
        projeto={projeto}
        isAlternate={index % 2 === 0}
      />
    ))}

    {/* Skeleton rows quando estado === 'skeleton' */}
    {estado === 'skeleton' && [1,2,3].map(i => (
      <div key={i} className="flex items-center px-4 w-full h-[52px] bg-white border-b border-gray-50 rounded-lg">
        <div className="w-[200px]"><div className="w-[60px] h-[12px] rounded-full skeleton-shimmer"></div></div>
        <div className="flex-1"><div className="w-[260px] h-[14px] rounded-full skeleton-shimmer"></div></div>
        <div className="w-[160px] flex justify-end"><div className="w-[80px] h-[12px] rounded-full skeleton-shimmer"></div></div>
      </div>
    ))}
  </div>
</div>

IMPORTANTE: os estados vazio e erro mantêm o mesmo comportamento em ambas as views.

Verificação da Fase 4:
- npm run build sem erros
- npm run lint sem erros e warnings
- Todos os dropdowns abrem e fecham corretamente
- Toggle alterna entre grid e tabela

---

## Fase 5 — Validação Final
- [ ] Task 5.1: npm run build → 0 erros
- [ ] Task 5.2: npm run lint → 0 erros e 0 warnings
- [ ] Task 5.3: Commit final

Verificação da Fase 5:
- Build e lint passam
- Todos os componentes novos tipados sem any
- Nenhum import de antd nos novos arquivos
