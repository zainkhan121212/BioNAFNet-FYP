import React, { useCallback, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload, FolderOpen, Save, Sparkles, Trash2, Image as ImageIcon,
  ChevronDown, CheckCircle2, X, FolderPlus, HardDrive
} from 'lucide-react';
import { ImageFile, ENHANCEMENT_MODELS } from '../types';

interface LeftPanelProps {
  darkMode: boolean;
  gpuEnabled: boolean;
  images: ImageFile[];
  selectedImageId: string | null;
  selectedModel: string;
  savePath: string;
  folderName: string;
  enhancing: boolean;
  enhanceProgress: number;
  onImagesAdd: (files: FileList) => void;
  onSelectImage: (id: string) => void;
  onRemoveImage: (id: string) => void;
  onClearImages: () => void;
  onSelectModel: (id: string) => void;
  onSetSavePath: (path: string) => void;
  onSetFolderName: (name: string) => void;
  onEnhance: () => void;
  onSave: () => void;
}

const LeftPanel: React.FC<LeftPanelProps> = ({
  darkMode, gpuEnabled, images, selectedImageId, selectedModel,
  savePath, folderName, enhancing, enhanceProgress,
  onImagesAdd, onSelectImage, onRemoveImage, onClearImages,
  onSelectModel, onSetSavePath, onSetFolderName, onEnhance, onSave
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      onImagesAdd(e.dataTransfer.files);
    }
  }, [onImagesAdd]);

  const currentModel = ENHANCEMENT_MODELS.find(m => m.id === selectedModel);

  const panelBg = darkMode
    ? gpuEnabled ? 'bg-gray-950/70 border-gray-800/50' : 'bg-gray-950/90 border-gray-800'
    : gpuEnabled ? 'bg-white/70 border-gray-200/50' : 'bg-white/90 border-gray-200';

  const cardBg = darkMode ? 'bg-gray-900/80' : 'bg-gray-50';
  const textPrimary = darkMode ? 'text-white' : 'text-gray-900';
  const textSecondary = darkMode ? 'text-gray-400' : 'text-gray-500';
  const inputBg = darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900';

  return (
    <motion.aside
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className={`w-80 min-w-80 border-r ${panelBg} glass-panel overflow-y-auto relative z-10`}
    >
      {gpuEnabled && <div className="scan-line" />}
      <div className="p-4 space-y-4">
        {/* Upload Section */}
        <motion.div layout className={`rounded-2xl p-4 ${cardBg} border ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="flex items-center gap-2 mb-3">
            <Upload className={`w-4 h-4 ${gpuEnabled ? 'text-cyan-400' : textSecondary}`} />
            <h3 className={`text-sm font-semibold ${textPrimary}`}>Image Upload</h3>
            {images.length > 0 && (
              <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${
                gpuEnabled ? 'bg-cyan-500/20 text-cyan-300' : darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'
              }`}>
                {images.length}
              </span>
            )}
          </div>

          <motion.div
            whileHover={{ scale: 1.02 }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-300 ${
              dragOver
                ? 'border-cyan-400 bg-cyan-500/10'
                : gpuEnabled
                  ? `${darkMode ? 'border-cyan-800/50 hover:border-cyan-500/50' : 'border-cyan-300/50 hover:border-cyan-400'} hover:bg-cyan-500/5`
                  : `${darkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-300 hover:border-gray-400'}`
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={(e) => e.target.files && onImagesAdd(e.target.files)}
              className="hidden"
            />
            <motion.div
              animate={gpuEnabled ? { y: [0, -4, 0] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <ImageIcon className={`w-8 h-8 mx-auto mb-2 ${
                gpuEnabled ? 'text-cyan-400' : textSecondary
              }`} />
            </motion.div>
            <p className={`text-sm font-medium ${textPrimary}`}>Drop images here</p>
            <p className={`text-xs mt-1 ${textSecondary}`}>or click to browse</p>
            <p className={`text-xs mt-1 ${textSecondary}`}>PNG, JPG, WEBP • Unlimited</p>
          </motion.div>

          {/* Image Thumbnails */}
          <AnimatePresence>
            {images.length > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-3 space-y-1.5 max-h-48 overflow-y-auto"
              >
                {images.map((img, i) => (
                  <motion.div
                    key={img.id}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -20, opacity: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => onSelectImage(img.id)}
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all duration-200 group ${
                      selectedImageId === img.id
                        ? gpuEnabled
                          ? 'bg-cyan-500/20 border border-cyan-500/30'
                          : darkMode ? 'bg-blue-500/20 border border-blue-500/30' : 'bg-blue-50 border border-blue-200'
                        : darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100'
                    }`}
                  >
                    <img
                      src={img.url}
                      alt={img.name}
                      className="w-9 h-9 rounded-md object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <p className={`text-xs font-medium truncate ${textPrimary}`}>{img.name}</p>
                      <p className={`text-xs ${textSecondary}`}>{(img.size / 1024).toFixed(1)} KB</p>
                    </div>
                    {img.enhanced && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); onRemoveImage(img.id); }}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className={`w-4 h-4 ${darkMode ? 'text-gray-500 hover:text-red-400' : 'text-gray-400 hover:text-red-500'}`} />
                    </button>
                  </motion.div>
                ))}

                <button
                  onClick={onClearImages}
                  className={`w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    darkMode ? 'text-red-400 hover:bg-red-500/10' : 'text-red-500 hover:bg-red-50'
                  }`}
                >
                  <Trash2 className="w-3 h-3" />
                  Clear All
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Model Selection */}
        <motion.div layout className={`rounded-2xl p-4 ${cardBg} border ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className={`w-4 h-4 ${gpuEnabled ? 'text-purple-400' : textSecondary}`} />
            <h3 className={`text-sm font-semibold ${textPrimary}`}>Enhancement Model</h3>
          </div>

          {/* Dropdown */}
          <div className="relative">
            <button
              onClick={() => setModelDropdownOpen(!modelDropdownOpen)}
              className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all duration-200 ${
                gpuEnabled
                  ? 'border-purple-500/30 hover:border-purple-400/50 bg-purple-500/5'
                  : darkMode ? 'border-gray-700 hover:border-gray-600 bg-gray-800' : 'border-gray-300 hover:border-gray-400 bg-white'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold ${
                  gpuEnabled ? 'bg-purple-500/20 text-purple-300' : darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'
                }`}>
                  {currentModel?.icon}
                </span>
                <div className="text-left">
                  <p className={`text-sm font-medium ${textPrimary}`}>
                    Model {currentModel?.label}: {currentModel?.name}
                  </p>
                </div>
              </div>
              <ChevronDown className={`w-4 h-4 transition-transform ${modelDropdownOpen ? 'rotate-180' : ''} ${textSecondary}`} />
            </button>

            <AnimatePresence>
              {modelDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  className={`absolute top-full left-0 right-0 mt-1 rounded-xl border overflow-hidden z-50 ${
                    darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'
                  } shadow-xl`}
                >
                  {ENHANCEMENT_MODELS.map((model) => (
                    <button
                      key={model.id}
                      onClick={() => { onSelectModel(model.id); setModelDropdownOpen(false); }}
                      className={`w-full flex items-center gap-3 p-3 text-left transition-all duration-150 ${
                        selectedModel === model.id
                          ? gpuEnabled
                            ? 'bg-purple-500/20'
                            : darkMode ? 'bg-blue-500/20' : 'bg-blue-50'
                          : darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50'
                      }`}
                    >
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${
                        darkMode ? 'bg-gray-800' : 'bg-gray-100'
                      }`}>
                        {model.icon}
                      </span>
                      <div>
                        <p className={`text-sm font-medium ${textPrimary}`}>
                          [{model.label}] {model.name}
                        </p>
                        <p className={`text-xs ${textSecondary}`}>{model.description}</p>
                      </div>
                      {selectedModel === model.id && (
                        <CheckCircle2 className="w-4 h-4 text-cyan-400 ml-auto shrink-0" />
                      )}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Enhance Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onEnhance}
            disabled={images.length === 0 || enhancing}
            className={`w-full mt-3 py-3 rounded-xl font-semibold text-sm transition-all duration-300 relative overflow-hidden ${
              images.length === 0
                ? darkMode ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : gpuEnabled
                  ? 'bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40'
                  : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40'
            }`}
          >
            {enhancing && (
              <motion.div
                className="absolute inset-0 bg-white/20"
                initial={{ x: '-100%' }}
                animate={{ x: '100%' }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
            <div className="flex items-center justify-center gap-2 relative z-10">
              <Sparkles className="w-4 h-4" />
              {enhancing ? `Enhancing... ${enhanceProgress}%` : '✦ ENHANCE'}
            </div>
          </motion.button>

          {enhancing && (
            <div className="mt-2">
              <div className={`h-1.5 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-gray-200'}`}>
                <motion.div
                  className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${enhanceProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          )}
        </motion.div>

        {/* Save Section */}
        <motion.div layout className={`rounded-2xl p-4 ${cardBg} border ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="flex items-center gap-2 mb-3">
            <FolderOpen className={`w-4 h-4 ${gpuEnabled ? 'text-emerald-400' : textSecondary}`} />
            <h3 className={`text-sm font-semibold ${textPrimary}`}>Output Settings</h3>
          </div>

          <div className="space-y-3">
            <div>
              <label className={`text-xs font-medium ${textSecondary} mb-1 block`}>Save Path</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={savePath}
                  onChange={(e) => onSetSavePath(e.target.value)}
                  placeholder="/home/user/enhanced"
                  className={`flex-1 text-xs px-3 py-2 rounded-lg border outline-none transition-colors ${inputBg} ${
                    gpuEnabled ? 'focus:border-cyan-500' : 'focus:border-blue-500'
                  }`}
                />
                <button className={`p-2 rounded-lg border transition-colors ${
                  darkMode ? 'border-gray-700 hover:bg-gray-800 text-gray-400' : 'border-gray-300 hover:bg-gray-100 text-gray-500'
                }`}>
                  <HardDrive className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div>
              <label className={`text-xs font-medium ${textSecondary} mb-1 block`}>New Folder Name</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={folderName}
                  onChange={(e) => onSetFolderName(e.target.value)}
                  placeholder="enhanced_output"
                  className={`flex-1 text-xs px-3 py-2 rounded-lg border outline-none transition-colors ${inputBg} ${
                    gpuEnabled ? 'focus:border-cyan-500' : 'focus:border-blue-500'
                  }`}
                />
                <button className={`p-2 rounded-lg border transition-colors ${
                  darkMode ? 'border-gray-700 hover:bg-gray-800 text-gray-400' : 'border-gray-300 hover:bg-gray-100 text-gray-500'
                }`}>
                  <FolderPlus className="w-4 h-4" />
                </button>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onSave}
              disabled={images.length === 0}
              className={`w-full py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
                images.length === 0
                  ? darkMode ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : gpuEnabled
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30'
                    : darkMode
                      ? 'bg-gray-800 text-gray-300 border border-gray-700 hover:bg-gray-700'
                      : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
              }`}
            >
              <Save className="w-4 h-4" />
              Save Results
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.aside>
  );
};

export default LeftPanel;
