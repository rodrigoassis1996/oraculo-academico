import React, { useState } from 'react';
import { Card, Steps, Input, Button, Space, Typography, Form } from 'antd';
import { GraduationCap, BookOpen, Target, Lightbulb } from 'lucide-react';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

interface BriefingWizardProps {
    onComplete: () => void;
}

export const BriefingWizard: React.FC<BriefingWizardProps> = ({ onComplete }) => {
    const [current, setCurrent] = useState(0);

    const steps = [
        {
            title: 'Tema',
            icon: <BookOpen size={18} />,
            content: (
                <Form layout="vertical">
                    <Form.Item label="Qual o tema central do seu trabalho?" required>
                        <TextArea placeholder="Ex: Impactos da IA na Educação Superior..." rows={3} />
                    </Form.Item>
                </Form>
            ),
        },
        {
            title: 'Objetivos',
            icon: <Target size={18} />,
            content: (
                <Form layout="vertical">
                    <Form.Item label="O que você pretende demonstrar ou analisar?" required>
                        <TextArea placeholder="Ex: Analisar como ferramentas de LLM podem auxiliar professores..." rows={3} />
                    </Form.Item>
                </Form>
            ),
        },
        {
            title: 'Metodologia',
            icon: <GraduationCap size={18} />,
            content: (
                <Form layout="vertical">
                    <Form.Item label="Qual a abordagem metodológica pretendida?">
                        <TextArea placeholder="Ex: Pesquisa qualitativa, estudo de caso, revisão bibliográfica..." rows={3} />
                    </Form.Item>
                </Form>
            ),
        },
        {
            title: 'Finalização',
            icon: <Lightbulb size={18} />,
            content: (
                <div className="text-center py-6">
                    <Title level={4}>Briefing Completo!</Title>
                    <Paragraph>
                        Com essas informações, estou pronto para sugerir uma estrutura inicial seguindo as normas ABNT.
                    </Paragraph>
                </div>
            ),
        },
    ];

    return (
        <Card className="max-w-3xl mx-auto shadow-md border-none" bodyStyle={{ padding: '40px' }}>
            <Steps
                current={current}
                size="small"
                items={steps.map(s => ({ title: s.title, icon: s.icon }))}
                className="mb-10"
            />

            <div className="min-h-[200px] mb-8">
                {steps[current].content}
            </div>

            <div className="flex justify-between border-t pt-6">
                <Button
                    onClick={() => setCurrent(current - 1)}
                    disabled={current === 0}
                >
                    Anterior
                </Button>
                <Button
                    type="primary"
                    onClick={() => {
                        if (current < steps.length - 1) {
                            setCurrent(current + 1);
                        } else {
                            onComplete();
                        }
                    }}
                >
                    {current === steps.length - 1 ? 'Iniciar Consultoria' : 'Próximo'}
                </Button>
            </div>
        </Card>
    );
};
