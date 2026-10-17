import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Zap, HardDrive, Clock, Layers } from 'lucide-react';
import { ImageFile } from '../types';

interface StatusBarProps {
  darkMode: boolean;
  gpuEnabled: boolean;
  images: ImageFile[];
  selectedImage: ImageFile | null;
}

const StatusBar: React.FC<StatusBarProps> = ({ darkMode, gpuEnabled, images, selectedImage }) => {
  const textSecondary = darkMode ? 'text-gray-500' : 'text-gray-400';

  return (
    <motion.footer
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className={`flex items-center justify-between px-4 py-1.5 border-t text-xs font-mono z-20 ${
        darkMode
          ? `border-gray-800 ${gpuEnabled ? 'bg-gray-950/80' : 'bg-gray-950/90'}`
          : `border-gray-200 ${gpuEnabled ? 'bg-white/80' : 'bg-white/90'}`
      } glass-panel`}
    >
      <div className="flex items-center gap-4">
        <span className={`flex items-center gap-1 ${textSecondary}`}>
          <Layers className="w-3 h-3" />
          {images.length} image{images.length !== 1 ? 's' : ''} loaded
        </span>
        {selectedImage && (
          <span className={textSecondary}>
            {selectedImage.name}
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <span className={`flex items-center gap-1 ${textSecondary}`}>
          <HardDrive className="w-3 h-3" />
          {images.length > 0
            ? `${(images.reduce((a, i) => a + i.size, 0) / (1024 * 1024)).toFixed(2)} MB`
            : '0 MB'
          }
        </span>
        <span className={`flex items-center gap-1 ${
          gpuEnabled ? 'text-cyan-400' : textSecondary
        }`}>
          {gpuEnabled ? <Zap className="w-3 h-3" /> : <Cpu className="w-3 h-3" />}
          {gpuEnabled ? 'CUDA Accelerated' : 'CPU Mode'}
        </span>
        <span className={`flex items-center gap-1 ${textSecondary}`}>
          <Clock className="w-3 h-3" />
          Ready
        </span>
        {gpuEnabled && (
          <motion.span
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex items-center gap-1 text-emerald-400"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            GPU Online
          </motion.span>
        )}
      </div>
    </motion.footer>
  );
};

export default StatusBar;
