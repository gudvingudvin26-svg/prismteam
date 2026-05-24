import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/ui';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
      <Card className="p-8 text-center max-w-md bg-white/90 backdrop-blur-sm">
        <div className="text-6xl mb-4">404</div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Страница не найдена</h1>
        <p className="text-gray-600 mb-6">
          Запрашиваемая страница не существует или была перемещена.
        </p>
        <Button onClick={() => navigate('/')}>
          Вернуться на главную
        </Button>
      </Card>
    </div>
  );
};

export default NotFound;