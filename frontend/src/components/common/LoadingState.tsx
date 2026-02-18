import React from 'react';
import { Spin, Space, Typography } from 'antd';

const { Text } = Typography;

interface LoadingStateProps {
    message?: string;
    tip?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
    message = "Processando informações acadêmicas...",
    tip
}) => {
    return (
        <div className="flex flex-col items-center justify-center py-20 w-full">
            <Space direction="vertical" align="center" size="large">
                <Spin size="large" />
                <div className="text-center">
                    <Text className="text-lg font-medium text-gray-600 block">{message}</Text>
                    {tip && <Text type="secondary" className="text-sm mt-2">{tip}</Text>}
                </div>
            </Space>
        </div>
    );
};
