import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md'
}) => {
  const paddings = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-8'
  }

  return (
    <div className={`bg-white rounded-lg shadow-md ${paddings[padding]} ${className}`}>
      {children}
    </div>
  )
}

export default Card