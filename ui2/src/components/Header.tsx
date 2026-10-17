import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, Cpu, Zap, Activity } from 'lucide-react';

interface HeaderProps {
  darkMode: boolean;
  gpuEnabled: boolean;
  onToggleDark: () => void;
  onToggleGpu: () => void;
}

const Header: React.FC<HeaderProps> = ({ darkMode, gpuEnabled, onToggleDark, onToggleGpu }) => {
  return (
    <motion.header
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={`relative z-20 flex items-center justify-between px-6 py-3 border-b ${
        darkMode
          ? `border-gray-800 ${gpuEnabled ? 'bg-gray-950/80 gpu-border-animate border' : 'bg-gray-950/90'}`
          : `border-gray-200 ${gpuEnabled ? 'bg-white/80 gpu-border-animate border' : 'bg-white/90'}`
      } glass-panel`}
    >
      {gpuEnabled && <div className="scan-line" />}
      
      <div className="flex items-center gap-3">
        <motion.div
          animate={gpuEnabled ? { rotate: [0, 360] } : { rotate: 0 }}
          transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            gpuEnabled
              ? 'bg-gradient-to-br from-cyan-500 via-purple-500 to-emerald-500 shadow-lg shadow-cyan-500/30'
              : darkMode
                ? 'bg-gradient-to-br from-gray-700 to-gray-800'
                : 'bg-gradient-to-br from-gray-200 to-gray-300'
          }`}
        >
          <Zap className="w-5 h-5 text-white" />
        </motion.div>
        <div>
          <h1 className={`text-xl font-bold tracking-tight ${
            gpuEnabled ? 'neon-text bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent' : 
            darkMode ? 'text-white' : 'text-gray-900'
          }`}>
            PixelForge
          </h1>
          <p className={`text-xs font-mono ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            AI Image Enhancement Studio v2.0
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Processing Status */}
        <motion.div
          animate={gpuEnabled ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 1.5, repeat: Infinity }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium ${
            gpuEnabled
              ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30'
              : darkMode
                ? 'bg-gray-800 border border-gray-700'
                : 'bg-gray-100 border border-gray-200'
          }`}
        >
          <Activity className={`w-4 h-4 ${gpuEnabled ? 'text-cyan-400' : darkMode ? 'text-gray-400' : 'text-gray-500'}`} />
          <span className={gpuEnabled ? 'text-cyan-300' : darkMode ? 'text-gray-300' : 'text-gray-600'}>
            {gpuEnabled ? 'GPU Accelerated' : 'CPU Processing'}
          </span>
        </motion.div>

        {/* GPU Toggle */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onToggleGpu}
          className={`relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-500 ${
            gpuEnabled
              ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white shadow-lg shadow-cyan-500/30 gpu-active'
              : darkMode
                ? 'bg-gray-800 text-gray-300 border border-gray-700 hover:border-gray-600'
                : 'bg-gray-100 text-gray-600 border border-gray-200 hover:border-gray-300'
          }`}
        >
          {gpuEnabled ? <Zap className="w-4 h-4" /> : <Cpu className="w-4 h-4" />}
          {gpuEnabled ? 'GPU ON' : 'GPU OFF'}
        </motion.button>

        {/* Dark/Light Toggle */}
        <motion.button
          whileHover={{ scale: 1.1, rotate: 15 }}
          whileTap={{ scale: 0.9 }}
          onClick={onToggleDark}
          className={`p-2.5 rounded-xl transition-all duration-300 ${
            darkMode
              ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-700'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
          }`}
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </motion.button>
      </div>
    </motion.header>
  );
};

export default Header;
