import React from 'react';
import { Card, Typography, Divider, Empty } from 'antd';
import { FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const { Title, Paragraph } = Typography;

interface ABNTPreviewProps {
    title?: string;
    content?: string;
    sections?: Array<{ key: string; title: string; content?: string }>;
}

export const ABNTPreview: React.FC<ABNTPreviewProps> = ({
    title = "Trabalho Acadêmico",
    content,
    sections = []
}) => {
    if (!content && sections.length === 0) {
        return <Empty description="Nenhum conteúdo gerado ainda." />;
    }

    return (
        <Card className="shadow-lg border-gray-200">
            <div className="p-8 max-w-4xl mx-auto font-serif text-gray-900 leading-relaxed text-left">
                <div className="text-center mb-16">
                    <Title level={2} className="uppercase font-bold tracking-widest">{title}</Title>
                </div>

                {content && (
                    <Paragraph className="text-justify mb-8 whitespace-pre-wrap markdown-content">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </Paragraph>
                )}

                {sections.map((section, index) => (
                    <div key={section.key} className="mb-10">
                        <Title level={4} className="uppercase font-bold border-b border-gray-100 pb-2 mb-4">
                            {index + 1}. {section.title}
                        </Title>
                        <Paragraph className="text-justify whitespace-pre-wrap markdown-content">
                            <ReactMarkdown>{section.content || "Aguardando geração do conteúdo..."}</ReactMarkdown>
                        </Paragraph>
                    </div>
                ))}

                <Divider className="my-12" />
                <div className="text-center text-xs text-gray-400">
                    Formatado automaticamente segundo as normas ABNT.
                </div>
            </div>
        </Card>
    );
};
