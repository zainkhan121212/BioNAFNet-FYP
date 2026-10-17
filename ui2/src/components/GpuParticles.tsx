import React, { useMemo } from 'react';

interface GpuParticlesProps {
  active: boolean;
}

const GpuParticles: React.FC<GpuParticlesProps> = ({ active }) => {
  const particles = useMemo(() => {
    return Array.from({ length: 30 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 8,
      duration: 6 + Math.random() * 8,
      size: 1 + Math.random() * 3,
      color: ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b'][Math.floor(Math.random() * 4)],
    }));
  }, []);

  if (!active) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="particle"
          style={{
            left: `${p.left}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            background: p.color,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
            boxShadow: `0 0 ${p.size * 3}px ${p.color}`,
          }}
        />
      ))}
    </div>
  );
};

export default GpuParticles;
