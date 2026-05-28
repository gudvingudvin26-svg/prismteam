import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
  key?: string | number;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  onClick,
  key
}) => {
  const paddings = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-8'
  };

  return (
    <div
      key={key}
      className={`bg-white rounded-lg shadow-md ${paddings[padding]} ${className} ${onClick ? 'cursor-pointer hover:shadow-lg transition' : ''}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;