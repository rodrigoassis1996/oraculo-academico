/** 
 * Rótulos de status exibidos nos cards do dashboard 
 */
export type StatusEtapa =
    | 'Rascunho'
    | 'Etapa 1: Contexto'
    | 'Etapa 2: Revisão'
    | 'Etapa 3: Metodologia'
    | 'Etapa 4: Escrita'
    | 'Revisão';

/** 
 * Perfil do usuário autenticado via OAuth Google 
 */
export interface Usuario {
    id: number;
    nome: string;
    email: string;
    fotoPerfil: string | null;
    role: 'pesquisador' | 'admin';
}

/** 
 * Projeto de pesquisa pertencente a um usuário 
 */
export interface Projeto {
    id: number;
    titulo: string;
    etapaAtual: 1 | 2 | 3 | 4 | 5;
    status: StatusEtapa;
    dataCriacao: string;
    dataUltimaModificacao: string | null;
}
