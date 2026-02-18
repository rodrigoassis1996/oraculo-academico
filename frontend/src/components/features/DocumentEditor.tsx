import React, { useState } from 'react';
import { Card, Steps, Button, Typography, Space, Tag, Empty } from 'antd';
import { ExternalLink, CheckCircle2, Circle, Clock } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { ABNTPreview } from '../common/ABNTPreview';

const { Title, Text } = Typography;

export const DocumentEditor: React.FC = () => {
    const { documentos, activeDocId } = useAppStore();
    const [currentSection, setCurrentSection] = useState(0);

    // Mock de seções para o layout (será integrado com a API)
    const secoes = [
        { key: 'INTRODUCAO', title: 'Introdução', status: 'done', content: 'Conteúdo da introdução...' },
        { key: 'METODOLOGIA', title: 'Metodologia', status: 'progress', content: 'A metodologia está sendo refinada...' },
        { key: 'RESULTADOS', title: 'Resultados', status: 'todo' },
        { key: 'CONCLUSAO', title: 'Conclusão', status: 'todo' },
    ];

    if (!activeDocId && documentos.length === 0) {
        return (
            <Card className="h-full flex items-center justify-center border-dashed border-2">
                <Empty description="Nenhum documento ativo para edição." />
            </Card>
        );
    }

    return (
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
            {/* Listagem de Seções */}
            <Card className="col-span-4 shadow-sm" bodyStyle={{ padding: '20px' }}>
                <Title level={5} className="mb-6 flex items-center justify-between">
                    Estrutura do Trabalho
                    {activeDocId && (
                        <Tag color="green" icon={<ExternalLink size={12} className="mr-1 inline" />}>
                            Google Docs
                        </Tag>
                    )}
                </Title>

                <Steps
                    direction="vertical"
                    current={currentSection}
                    onChange={setCurrentSection}
                    items={secoes.map((s, idx) => ({
                        title: s.title,
                        description: s.status === 'done' ? 'Sincronizado' : s.status === 'progress' ? 'Em edição' : 'Aguardando',
                        icon: s.status === 'done' ? <CheckCircle2 size={16} className="text-green-500" /> :
                            s.status === 'progress' ? <Clock size={16} className="text-primary-500" /> :
                                <Circle size={16} className="text-gray-300" />,
                        disabled: s.status === 'todo' && idx > currentSection + 1
                    }))}
                />

                <div className="mt-8 border-t pt-4">
                    <Button type="link" block className="text-xs text-gray-400">
                        Exportar como PDF (Normas ABNT)
                    </Button>
                </div>
            </Card>

            {/* Visualização da Seção Ativa */}
            <div className="col-span-8 overflow-y-auto">
                <Card className="shadow-md h-full" bodyStyle={{ padding: 0 }}>
                    <div className="p-4 border-b flex items-center justify-between bg-white sticky top-0 z-10">
                        <Space direction="vertical" size={0}>
                            <Text type="secondary" className="text-[10px] uppercase font-bold tracking-widest text-primary-600">
                                Visualização de Seção
                            </Text>
                            <Title level={4} style={{ margin: 0 }}>{secoes[currentSection].title}</Title>
                        </Space>

                        <Space>
                            <Button size="small">Editar Manualmente</Button>
                            <Button type="primary" size="small">Revisar com IA</Button>
                        </Space>
                    </div>

                    <div className="p-8">
                        <ABNTPreview
                            title={secoes[currentSection].title}
                            content={secoes[currentSection].content}
                        />
                    </div>
                </Card>
            </div>
        </div>
    );
};
