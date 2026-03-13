import React from 'react';
import clsx from 'clsx';

const LoadingSpinner = ({ size = 'md', fullScreen = false }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const spinner = (
    <div className={clsx('flex items-center justify-center', fullScreen && 'min-h-screen')}>
      <div className={clsx(
        'border-4 border-primary border-t-transparent rounded-full animate-spin',
        sizeClasses[size]
      )}></div>
    </div>
  );

  if (fullScreen) {
    return spinner;
  }

  return spinner;
};

export default LoadingSpinner;