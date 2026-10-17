import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Crop, Scaling, Shuffle, ChevronRight, Settings2,
  FlipHorizontal, FlipVertical, RotateCw,
  Sliders, Lock, Unlock
} from 'lucide-react';

interface RightPanelProps {
  darkMode: boolean;
  gpuEnabled: boolean;
  resizeWidth: number;
  resizeHeight: number;
  cropEnabled: boolean;
  augmentationEnabled: boolean;
  resizingEnabled: boolean;
  onResizeWidth: (w: number) => void;
  onResizeHeight: (h: number) => void;
  onToggleCrop: () => void;
  onToggleAugmentation: () => void;
  onToggleResizing: () => void;
}

const RightPanel: React.FC<RightPanelProps> = ({
  darkMode, gpuEnabled,
  resizeWidth, resizeHeight,
  cropEnabled, augmentationEnabled, resizingEnabled,
  onResizeWidth, onResizeHeight,
  onToggleCrop, onToggleAugmentation, onToggleResizing
}) => {
  const [aspectLock, setAspectLock] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>('resize');

  const textPrimary = darkMode ? 'text-white' : 'text-gray-900';
  const textSecondary = darkMode ? 'text-gray-400' : 'text-gray-500';
  const inputBg = darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900';
  const panelBg = darkMode
    ? gpuEnabled ? 'bg-gray-950/70 border-gray-800/50' : 'bg-gray-950/90 border-gray-800'
    : gpuEnabled ? 'bg-white/70 border-gray-200/50' : 'bg-white/90 border-gray-200';

  const handleWidthChange = (w: number) => {
    onResizeWidth(w);
    if (aspectLock && resizeWidth > 0) {
      const ratio = resizeHeight / resizeWidth;
      onResizeHeight(Math.round(w * ratio));
    }
  };

  const handleHeightChange = (h: number) => {
    onResizeHeight(h);
    if (aspectLock && resizeHeight > 0) {
      const ratio = resizeWidth / resizeHeight;
      onResizeWidth(Math.round(h * ratio));
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <motion.aside
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className={`w-72 min-w-72 border-l ${panelBg} glass-panel overflow-y-auto relative z-10`}
    >
      {gpuEnabled && <div className="scan-line" />}
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <Settings2 className={`w-4 h-4 ${gpuEnabled ? 'text-cyan-400' : textSecondary}`} />
          <h2 className={`text-sm font-bold ${textPrimary}`}>Processing Tools</h2>
        </div>

        {/* Resizing */}
        <ToolSection
          title="Resizing"
          icon={<Scaling className="w-4 h-4" />}
          enabled={resizingEnabled}
          onToggle={onToggleResizing}
          expanded={expandedSection === 'resize'}
          onExpand={() => toggleSection('resize')}
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          accentColor="cyan"
        >
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex-1">
                <label className={`text-xs ${textSecondary} mb-1 block`}>Width (px)</label>
                <input
                  type="number"
                  value={resizeWidth}
                  onChange={(e) => handleWidthChange(Number(e.target.value))}
                  className={`w-full text-xs px-3 py-2 rounded-lg border outline-none ${inputBg} ${
                    gpuEnabled ? 'focus:border-cyan-500' : 'focus:border-blue-500'
                  }`}
                />
              </div>
              <button
                onClick={() => setAspectLock(!aspectLock)}
                className={`mt-5 p-1.5 rounded-lg transition-colors ${
                  aspectLock
                    ? gpuEnabled ? 'text-cyan-400 bg-cyan-500/10' : 'text-blue-400 bg-blue-500/10'
                    : darkMode ? 'text-gray-500' : 'text-gray-400'
                }`}
              >
                {aspectLock ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
              </button>
              <div className="flex-1">
                <label className={`text-xs ${textSecondary} mb-1 block`}>Height (px)</label>
                <input
                  type="number"
                  value={resizeHeight}
                  onChange={(e) => handleHeightChange(Number(e.target.value))}
                  className={`w-full text-xs px-3 py-2 rounded-lg border outline-none ${inputBg} ${
                    gpuEnabled ? 'focus:border-cyan-500' : 'focus:border-blue-500'
                  }`}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1.5">
              {[
                { label: 'HD', w: 1280, h: 720 },
                { label: 'FHD', w: 1920, h: 1080 },
                { label: '4K', w: 3840, h: 2160 },
              ].map(preset => (
                <button
                  key={preset.label}
                  onClick={() => { onResizeWidth(preset.w); onResizeHeight(preset.h); }}
                  className={`py-1.5 rounded-lg text-xs font-medium transition-all ${
                    resizeWidth === preset.w && resizeHeight === preset.h
                      ? gpuEnabled
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : darkMode
                        ? 'bg-gray-800 text-gray-400 hover:text-gray-300 hover:bg-gray-700'
                        : 'bg-gray-100 text-gray-500 hover:text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            <div>
              <label className={`text-xs ${textSecondary} mb-1 block`}>Scale Factor</label>
              <input
                type="range"
                min={25}
                max={400}
                defaultValue={100}
                className={`w-full ${darkMode ? 'bg-gray-700' : 'bg-gray-300'}`}
              />
              <div className="flex justify-between">
                <span className={`text-xs ${textSecondary}`}>25%</span>
                <span className={`text-xs ${textSecondary}`}>400%</span>
              </div>
            </div>
          </div>
        </ToolSection>

        {/* Cropping */}
        <ToolSection
          title="Cropping"
          icon={<Crop className="w-4 h-4" />}
          enabled={cropEnabled}
          onToggle={onToggleCrop}
          expanded={expandedSection === 'crop'}
          onExpand={() => toggleSection('crop')}
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          accentColor="purple"
        >
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-1.5">
              {['1:1', '4:3', '16:9', '3:2', '9:16', 'Free'].map(ratio => (
                <button
                  key={ratio}
                  className={`py-1.5 rounded-lg text-xs font-medium transition-all ${
                    darkMode
                      ? 'bg-gray-800 text-gray-400 hover:text-gray-300 hover:bg-gray-700'
                      : 'bg-gray-100 text-gray-500 hover:text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {ratio}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <ToolMiniButton icon={<FlipHorizontal className="w-4 h-4" />} label="H-Flip" darkMode={darkMode} gpuEnabled={gpuEnabled} />
              <ToolMiniButton icon={<FlipVertical className="w-4 h-4" />} label="V-Flip" darkMode={darkMode} gpuEnabled={gpuEnabled} />
              <ToolMiniButton icon={<RotateCw className="w-4 h-4" />} label="Rotate" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            </div>
          </div>
        </ToolSection>

        {/* Data Augmentation */}
        <ToolSection
          title="Data Augmentation"
          icon={<Shuffle className="w-4 h-4" />}
          enabled={augmentationEnabled}
          onToggle={onToggleAugmentation}
          expanded={expandedSection === 'augmentation'}
          onExpand={() => toggleSection('augmentation')}
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          accentColor="emerald"
        >
          <div className="space-y-3">
            <AugmentToggle label="Random Rotation" sublabel="±15°" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            <AugmentToggle label="Horizontal Flip" sublabel="50% chance" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            <AugmentToggle label="Vertical Flip" sublabel="50% chance" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            <AugmentToggle label="Color Jitter" sublabel="Brightness, Contrast" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            <AugmentToggle label="Random Crop" sublabel="80-100% area" darkMode={darkMode} gpuEnabled={gpuEnabled} />
            <AugmentToggle label="Gaussian Noise" sublabel="σ=0.01" darkMode={darkMode} gpuEnabled={gpuEnabled} />

            <div>
              <label className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1 block`}>Augmentation Multiplier</label>
              <input
                type="range"
                min={1}
                max={10}
                defaultValue={3}
                className={`w-full ${darkMode ? 'bg-gray-700' : 'bg-gray-300'}`}
              />
              <div className="flex justify-between">
                <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>1x</span>
                <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>10x</span>
              </div>
            </div>
          </div>
        </ToolSection>

        {/* Advanced Settings */}
        <ToolSection
          title="Advanced"
          icon={<Sliders className="w-4 h-4" />}
          enabled={true}
          expanded={expandedSection === 'advanced'}
          onExpand={() => toggleSection('advanced')}
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          accentColor="amber"
        >
          <div className="space-y-3">
            <SliderControl label="Brightness" min={-100} max={100} defaultValue={0} darkMode={darkMode} />
            <SliderControl label="Contrast" min={-100} max={100} defaultValue={0} darkMode={darkMode} />
            <SliderControl label="Saturation" min={-100} max={100} defaultValue={0} darkMode={darkMode} />
            <SliderControl label="Sharpness" min={0} max={100} defaultValue={0} darkMode={darkMode} />
          </div>
        </ToolSection>
      </div>
    </motion.aside>
  );
};

/* Sub-components */

interface ToolSectionProps {
  title: string;
  icon: React.ReactNode;
  enabled?: boolean;
  onToggle?: () => void;
  expanded: boolean;
  onExpand: () => void;
  darkMode: boolean;
  gpuEnabled: boolean;
  accentColor: string;
  children: React.ReactNode;
}

const ToolSection: React.FC<ToolSectionProps> = ({
  title, icon, enabled = true, onToggle, expanded, onExpand,
  darkMode, gpuEnabled, accentColor, children
}) => {
  const accentColors: Record<string, { active: string; border: string; bg: string }> = {
    cyan: { active: 'text-cyan-400', border: 'border-cyan-500/30', bg: 'bg-cyan-500/10' },
    purple: { active: 'text-purple-400', border: 'border-purple-500/30', bg: 'bg-purple-500/10' },
    emerald: { active: 'text-emerald-400', border: 'border-emerald-500/30', bg: 'bg-emerald-500/10' },
    amber: { active: 'text-amber-400', border: 'border-amber-500/30', bg: 'bg-amber-500/10' },
  };

  const accent = accentColors[accentColor] || accentColors.cyan;

  return (
    <motion.div
      layout
      className={`rounded-2xl overflow-hidden border transition-all duration-300 ${
        enabled && gpuEnabled
          ? `${darkMode ? 'bg-gray-900/80' : 'bg-gray-50'} ${accent.border}`
          : `${darkMode ? 'bg-gray-900/80 border-gray-800' : 'bg-gray-50 border-gray-200'}`
      }`}
    >
      <button
        onClick={onExpand}
        className="w-full flex items-center gap-2 p-3 text-left"
      >
        <span className={`${enabled && gpuEnabled ? accent.active : darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
          {icon}
        </span>
        <span className={`text-sm font-semibold flex-1 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          {title}
        </span>
        {onToggle && (
          <button
            onClick={(e) => { e.stopPropagation(); onToggle(); }}
            className={`relative w-9 h-5 rounded-full transition-all duration-300 ${
              enabled
                ? gpuEnabled
                  ? `bg-gradient-to-r from-cyan-500 to-${accentColor === 'purple' ? 'purple' : accentColor === 'emerald' ? 'emerald' : 'cyan'}-500`
                  : 'bg-blue-500'
                : darkMode ? 'bg-gray-700' : 'bg-gray-300'
            }`}
          >
            <motion.div
              className="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm"
              animate={{ left: enabled ? '18px' : '2px' }}
              transition={{ duration: 0.2 }}
            />
          </button>
        )}
        <ChevronRight className={`w-4 h-4 transition-transform duration-200 ${
          expanded ? 'rotate-90' : ''
        } ${darkMode ? 'text-gray-500' : 'text-gray-400'}`} />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const AugmentToggle: React.FC<{
  label: string;
  sublabel: string;
  darkMode: boolean;
  gpuEnabled: boolean;
}> = ({ label, sublabel, darkMode, gpuEnabled }) => {
  const [on, setOn] = useState(false);
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>{label}</p>
        <p className={`text-xs ${darkMode ? 'text-gray-600' : 'text-gray-400'}`}>{sublabel}</p>
      </div>
      <button
        onClick={() => setOn(!on)}
        className={`relative w-8 h-4.5 rounded-full transition-all duration-300 ${
          on
            ? gpuEnabled ? 'bg-emerald-500' : 'bg-blue-500'
            : darkMode ? 'bg-gray-700' : 'bg-gray-300'
        }`}
        style={{ minWidth: '32px', height: '18px' }}
      >
        <motion.div
          className="absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white shadow-sm"
          animate={{ left: on ? '15px' : '2px' }}
          transition={{ duration: 0.2 }}
          style={{ width: '14px', height: '14px' }}
        />
      </button>
    </div>
  );
};

const ToolMiniButton: React.FC<{
  icon: React.ReactNode;
  label: string;
  darkMode: boolean;
  gpuEnabled: boolean;
}> = ({ icon, label, darkMode }) => (
  <button className={`flex-1 flex flex-col items-center gap-1 py-2 rounded-lg transition-colors ${
    darkMode ? 'bg-gray-800 text-gray-400 hover:text-gray-300 hover:bg-gray-700' : 'bg-gray-100 text-gray-500 hover:text-gray-600 hover:bg-gray-200'
  }`}>
    {icon}
    <span className="text-xs">{label}</span>
  </button>
);

const SliderControl: React.FC<{
  label: string;
  min: number;
  max: number;
  defaultValue: number;
  darkMode: boolean;
}> = ({ label, min, max, defaultValue, darkMode }) => {
  const [value, setValue] = useState(defaultValue);
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>{label}</span>
        <span className={`text-xs font-mono ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        className={`w-full ${darkMode ? 'bg-gray-700' : 'bg-gray-300'}`}
      />
    </div>
  );
};

export default RightPanel;
