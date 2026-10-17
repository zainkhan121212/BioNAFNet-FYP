import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ZoomIn, ZoomOut, RotateCcw, Maximize2, Columns,
  Eye, ImageIcon, Move
} from 'lucide-react';
import { ImageFile } from '../types';

interface CenterPanelProps {
  darkMode: boolean;
  gpuEnabled: boolean;
  selectedImage: ImageFile | null;
  compareMode: boolean;
  zoomLevel: number;
  onToggleCompare: () => void;
  onZoomChange: (zoom: number) => void;
}

const CenterPanel: React.FC<CenterPanelProps> = ({
  darkMode, gpuEnabled, selectedImage, compareMode, zoomLevel,
  onToggleCompare, onZoomChange
}) => {
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [rotation, setRotation] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const panStart = useRef({ x: 0, y: 0 });

  const handleSliderMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    setSliderPos(Math.max(0, Math.min(100, x)));
  }, [isDragging]);

  const handlePanStart = useCallback((e: React.MouseEvent) => {
    if (!compareMode && zoomLevel > 100) {
      setIsPanning(true);
      panStart.current = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
    }
  }, [compareMode, zoomLevel, panOffset]);

  const handlePanMove = useCallback((e: React.MouseEvent) => {
    if (isPanning) {
      setPanOffset({
        x: e.clientX - panStart.current.x,
        y: e.clientY - panStart.current.y,
      });
    }
  }, [isPanning]);

  const handlePanEnd = useCallback(() => {
    setIsPanning(false);
  }, []);

  const textPrimary = darkMode ? 'text-white' : 'text-gray-900';
  const textSecondary = darkMode ? 'text-gray-400' : 'text-gray-500';

  return (
    <motion.main
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="flex-1 flex flex-col overflow-hidden relative z-10"
    >
      {/* Toolbar */}
      <div className={`flex items-center justify-between px-4 py-2 border-b ${
        darkMode ? 'border-gray-800 bg-gray-950/50' : 'border-gray-200 bg-white/50'
      } glass-panel`}>
        <div className="flex items-center gap-1.5">
          <ToolButton icon={<ZoomOut className="w-4 h-4" />} onClick={() => onZoomChange(Math.max(25, zoomLevel - 25))} darkMode={darkMode} gpuEnabled={gpuEnabled} />
          <div className={`px-3 py-1 rounded-lg text-xs font-mono font-medium ${
            darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-600'
          }`}>
            {zoomLevel}%
          </div>
          <ToolButton icon={<ZoomIn className="w-4 h-4" />} onClick={() => onZoomChange(Math.min(400, zoomLevel + 25))} darkMode={darkMode} gpuEnabled={gpuEnabled} />
          <div className={`w-px h-5 mx-1 ${darkMode ? 'bg-gray-700' : 'bg-gray-300'}`} />
          <ToolButton icon={<RotateCcw className="w-4 h-4" />} onClick={() => { setRotation(r => r - 90); }} darkMode={darkMode} gpuEnabled={gpuEnabled} />
          <ToolButton icon={<Maximize2 className="w-4 h-4" />} onClick={() => { onZoomChange(100); setRotation(0); setPanOffset({ x: 0, y: 0 }); }} darkMode={darkMode} gpuEnabled={gpuEnabled} />
          <ToolButton icon={<Move className="w-4 h-4" />} onClick={() => {}} darkMode={darkMode} gpuEnabled={gpuEnabled} active={isPanning} />
        </div>

        <div className="flex items-center gap-1.5">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleCompare}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              compareMode
                ? gpuEnabled
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : darkMode
                  ? 'bg-gray-800 text-gray-400 hover:text-gray-300'
                  : 'bg-gray-100 text-gray-500 hover:text-gray-600'
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            Compare
          </motion.button>
        </div>
      </div>

      {/* Viewport */}
      <div
        ref={containerRef}
        className={`flex-1 flex items-center justify-center overflow-hidden relative ${
          darkMode
            ? gpuEnabled ? 'bg-gray-950 gpu-grid-bg' : 'bg-gray-950'
            : gpuEnabled ? 'bg-gray-100 gpu-grid-bg' : 'bg-gray-100'
        }`}
        onMouseDown={handlePanStart}
        onMouseMove={(e) => { handlePanMove(e); handleSliderMove(e); }}
        onMouseUp={() => { handlePanEnd(); setIsDragging(false); }}
        onMouseLeave={() => { handlePanEnd(); setIsDragging(false); }}
      >
        {/* Checkerboard pattern background */}
        {selectedImage ? (
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedImage.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
              className="relative"
              style={{
                transform: `scale(${zoomLevel / 100}) rotate(${rotation}deg) translate(${panOffset.x}px, ${panOffset.y}px)`,
                transition: isPanning ? 'none' : 'transform 0.3s ease',
              }}
            >
              {compareMode && selectedImage.enhanced ? (
                <div className="relative select-none" style={{ width: '600px', maxWidth: '70vw' }}>
                  {/* Enhanced (full) */}
                  <img
                    src={selectedImage.enhancedUrl || selectedImage.url}
                    alt="Enhanced"
                    className="w-full h-auto rounded-xl shadow-2xl"
                    draggable={false}
                  />
                  {/* Original (clipped) */}
                  <div
                    className="absolute inset-0 overflow-hidden rounded-xl"
                    style={{ width: `${sliderPos}%` }}
                  >
                    <img
                      src={selectedImage.url}
                      alt="Original"
                      className="h-full object-cover rounded-l-xl"
                      style={{ width: `${100 / (sliderPos / 100)}%`, maxWidth: 'none' }}
                      draggable={false}
                    />
                  </div>
                  {/* Slider handle */}
                  <div
                    className="absolute top-0 bottom-0 cursor-col-resize z-20"
                    style={{ left: `${sliderPos}%`, transform: 'translateX(-50%)' }}
                    onMouseDown={() => setIsDragging(true)}
                  >
                    <div className={`w-0.5 h-full ${gpuEnabled ? 'bg-cyan-400' : 'bg-white'} shadow-lg`} />
                    <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full border-2 flex items-center justify-center ${
                      gpuEnabled ? 'border-cyan-400 bg-gray-900/80' : 'border-white bg-gray-900/80'
                    }`}>
                      <Columns className={`w-4 h-4 ${gpuEnabled ? 'text-cyan-400' : 'text-white'}`} />
                    </div>
                  </div>
                  {/* Labels */}
                  <div className="absolute top-3 left-3 px-2 py-1 rounded-md bg-black/60 text-white text-xs font-medium">
                    Original
                  </div>
                  <div className="absolute top-3 right-3 px-2 py-1 rounded-md bg-black/60 text-white text-xs font-medium flex items-center gap-1">
                    <Sparkle gpuEnabled={gpuEnabled} />
                    Enhanced
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={selectedImage.enhanced ? (selectedImage.enhancedUrl || selectedImage.url) : selectedImage.url}
                    alt={selectedImage.name}
                    className={`max-w-[70vw] max-h-[60vh] rounded-xl shadow-2xl ${
                      gpuEnabled ? 'shadow-cyan-500/10' : ''
                    }`}
                    draggable={false}
                  />
                  {selectedImage.enhanced && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`absolute bottom-3 right-3 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 ${
                        gpuEnabled
                          ? 'bg-gradient-to-r from-cyan-500/80 to-purple-500/80 text-white backdrop-blur-md'
                          : 'bg-emerald-500/80 text-white backdrop-blur-md'
                      }`}
                    >
                      <Eye className="w-3 h-3" />
                      Enhanced
                    </motion.div>
                  )}
                  <div className={`absolute bottom-3 left-3 px-3 py-1.5 rounded-lg text-xs font-medium backdrop-blur-md ${
                    'bg-black/50 text-white'
                  }`}>
                    {selectedImage.name}
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <motion.div
              animate={gpuEnabled ? { y: [0, -8, 0], rotate: [0, 5, -5, 0] } : {}}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <ImageIcon className={`w-20 h-20 mx-auto mb-4 ${
                gpuEnabled ? 'text-cyan-500/30' : darkMode ? 'text-gray-700' : 'text-gray-300'
              }`} />
            </motion.div>
            <p className={`text-lg font-semibold ${textPrimary}`}>No Image Selected</p>
            <p className={`text-sm mt-1 ${textSecondary}`}>Upload and select an image to begin</p>
          </motion.div>
        )}

        {/* Zoom slider on the side */}
        <div className={`absolute right-4 top-1/2 -translate-y-1/2 flex flex-col items-center gap-2 p-2 rounded-xl ${
          darkMode ? 'bg-gray-900/80' : 'bg-white/80'
        } glass-panel`}>
          <ZoomIn className={`w-3.5 h-3.5 ${textSecondary}`} />
          <input
            type="range"
            min={25}
            max={400}
            value={zoomLevel}
            onChange={(e) => onZoomChange(Number(e.target.value))}
            className={`w-24 -rotate-90 ${darkMode ? 'bg-gray-700' : 'bg-gray-300'}`}
            style={{ marginTop: '40px', marginBottom: '40px' }}
          />
          <ZoomOut className={`w-3.5 h-3.5 ${textSecondary}`} />
        </div>
      </div>
    </motion.main>
  );
};

const ToolButton: React.FC<{
  icon: React.ReactNode;
  onClick: () => void;
  darkMode: boolean;
  gpuEnabled: boolean;
  active?: boolean;
}> = ({ icon, onClick, darkMode, gpuEnabled, active }) => (
  <motion.button
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.9 }}
    onClick={onClick}
    className={`p-1.5 rounded-lg transition-all duration-200 ${
      active
        ? gpuEnabled
          ? 'bg-cyan-500/20 text-cyan-400'
          : 'bg-blue-500/20 text-blue-400'
        : darkMode
          ? 'text-gray-400 hover:text-white hover:bg-gray-800'
          : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200'
    }`}
  >
    {icon}
  </motion.button>
);

const Sparkle: React.FC<{ gpuEnabled: boolean }> = ({ gpuEnabled }) => (
  <span className={gpuEnabled ? 'text-cyan-300' : 'text-emerald-300'}>✦</span>
);

export default CenterPanel;
