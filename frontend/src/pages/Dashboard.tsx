import React from 'react';
import QuizList from '../components/quiz/QuizList';

const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <QuizList />
    </div>
  );
};

export default Dashboard;