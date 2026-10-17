import { useState, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import LeftPanel from './components/LeftPanel';
import CenterPanel from './components/CenterPanel';
import RightPanel from './components/RightPanel';
import StatusBar from './components/StatusBar';
import GpuParticles from './components/GpuParticles';
import { ImageFile } from './types';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [gpuEnabled, setGpuEnabled] = useState(false);
  const [images, setImages] = useState<ImageFile[]>([]);
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState('A');
  const [savePath, setSavePath] = useState('/home/user/enhanced');
  const [folderName, setFolderName] = useState('enhanced_output');
  const [resizeWidth, setResizeWidth] = useState(1920);
  const [resizeHeight, setResizeHeight] = useState(1080);
  const [cropEnabled, setCropEnabled] = useState(false);
  const [augmentationEnabled, setAugmentationEnabled] = useState(false);
  const [resizingEnabled, setResizingEnabled] = useState(true);
  const [enhancing, setEnhancing] = useState(false);
  const [enhanceProgress, setEnhanceProgress] = useState(0);
  const [compareMode, setCompareMode] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);

  const selectedImage = images.find(img => img.id === selectedImageId) || null;

  const handleImagesAdd = useCallback((files: FileList) => {
    const newImages: ImageFile[] = Array.from(files)
      .filter(file => file.type.startsWith('image/'))
      .map(file => ({
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        file,
        url: URL.createObjectURL(file),
        name: file.name,
        size: file.size,
        enhanced: false,
      }));

    setImages(prev => [...prev, ...newImages]);
    if (!selectedImageId && newImages.length > 0) {
      setSelectedImageId(newImages[0].id);
    }
  }, [selectedImageId]);

  const handleRemoveImage = useCallback((id: string) => {
    setImages(prev => {
      const filtered = prev.filter(img => img.id !== id);
      if (selectedImageId === id) {
        setSelectedImageId(filtered.length > 0 ? filtered[0].id : null);
      }
      return filtered;
    });
  }, [selectedImageId]);

  const handleClearImages = useCallback(() => {
    images.forEach(img => URL.revokeObjectURL(img.url));
    setImages([]);
    setSelectedImageId(null);
  }, [images]);

  const handleEnhance = useCallback(() => {
    if (images.length === 0 || enhancing) return;

    setEnhancing(true);
    setEnhanceProgress(0);

    // Simulate enhancement process
    const totalSteps = 50;
    let step = 0;

    const interval = setInterval(() => {
      step++;
      const progress = Math.min(100, Math.round((step / totalSteps) * 100));
      setEnhanceProgress(progress);

      if (step >= totalSteps) {
        clearInterval(interval);
        setEnhancing(false);
        setEnhanceProgress(100);

        // Mark all images as enhanced (simulate with a canvas filter)
        setImages(prev => prev.map(img => ({
          ...img,
          enhanced: true,
          enhancedUrl: img.url, // In a real app, this would be the enhanced image URL
        })));

        // Auto-enable compare mode
        setCompareMode(true);

        setTimeout(() => setEnhanceProgress(0), 2000);
      }
    }, 60);
  }, [images, enhancing]);

  const handleSave = useCallback(() => {
    // In a real desktop app, this would save files to the specified path
    // For the web demo, we'll trigger downloads
    const enhancedImages = images.filter(img => img.enhanced);
    if (enhancedImages.length === 0) {
      alert('No enhanced images to save. Please enhance images first.');
      return;
    }

    enhancedImages.forEach(img => {
      const link = document.createElement('a');
      link.href = img.enhancedUrl || img.url;
      link.download = `enhanced_${img.name}`;
      link.click();
    });

    alert(`${enhancedImages.length} image(s) would be saved to: ${savePath}/${folderName}`);
  }, [images, savePath, folderName]);

  return (
    <div className={`h-screen w-screen flex flex-col overflow-hidden transition-colors duration-500 ${
      darkMode ? 'bg-gray-950 text-white' : 'bg-gray-50 text-gray-900'
    }`}>
      {/* GPU Particles Background */}
      <GpuParticles active={gpuEnabled} />

      {/* GPU Active Global Glow */}
      <AnimatePresence>
        {gpuEnabled && (
          <div className="fixed inset-0 pointer-events-none z-0">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/3 rounded-full blur-3xl" />
          </div>
        )}
      </AnimatePresence>

      <Header
        darkMode={darkMode}
        gpuEnabled={gpuEnabled}
        onToggleDark={() => setDarkMode(!darkMode)}
        onToggleGpu={() => setGpuEnabled(!gpuEnabled)}
      />

      <div className="flex-1 flex overflow-hidden">
        <LeftPanel
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          images={images}
          selectedImageId={selectedImageId}
          selectedModel={selectedModel}
          savePath={savePath}
          folderName={folderName}
          enhancing={enhancing}
          enhanceProgress={enhanceProgress}
          onImagesAdd={handleImagesAdd}
          onSelectImage={setSelectedImageId}
          onRemoveImage={handleRemoveImage}
          onClearImages={handleClearImages}
          onSelectModel={setSelectedModel}
          onSetSavePath={setSavePath}
          onSetFolderName={setFolderName}
          onEnhance={handleEnhance}
          onSave={handleSave}
        />

        <CenterPanel
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          selectedImage={selectedImage}
          compareMode={compareMode}
          zoomLevel={zoomLevel}
          onToggleCompare={() => setCompareMode(!compareMode)}
          onZoomChange={setZoomLevel}
        />

        <RightPanel
          darkMode={darkMode}
          gpuEnabled={gpuEnabled}
          resizeWidth={resizeWidth}
          resizeHeight={resizeHeight}
          cropEnabled={cropEnabled}
          augmentationEnabled={augmentationEnabled}
          resizingEnabled={resizingEnabled}
          onResizeWidth={setResizeWidth}
          onResizeHeight={setResizeHeight}
          onToggleCrop={() => setCropEnabled(!cropEnabled)}
          onToggleAugmentation={() => setAugmentationEnabled(!augmentationEnabled)}
          onToggleResizing={() => setResizingEnabled(!resizingEnabled)}
        />
      </div>

      <StatusBar
        darkMode={darkMode}
        gpuEnabled={gpuEnabled}
        images={images}
        selectedImage={selectedImage}
      />
    </div>
  );
}

export default App;
