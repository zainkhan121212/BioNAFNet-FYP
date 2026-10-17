export interface ImageFile {
  id: string;
  file: File;
  url: string;
  name: string;
  size: number;
  enhanced?: boolean;
  enhancedUrl?: string;
}

export interface EnhancementModel {
  id: string;
  label: string;
  name: string;
  description: string;
  icon: string;
}

export interface AppState {
  darkMode: boolean;
  gpuEnabled: boolean;
  images: ImageFile[];
  selectedImageId: string | null;
  selectedModel: string;
  savePath: string;
  folderName: string;
  resizeWidth: number;
  resizeHeight: number;
  cropEnabled: boolean;
  augmentationEnabled: boolean;
  resizingEnabled: boolean;
  enhancing: boolean;
  enhanceProgress: number;
  compareMode: boolean;
  zoomLevel: number;
}

export const ENHANCEMENT_MODELS: EnhancementModel[] = [
  { id: 'A', label: 'A', name: 'Zero-DCE', description: 'Zero-Reference Deep Curve Estimation', icon: '⚡' },
  { id: 'B', label: 'B', name: 'RetinexNet', description: 'Retinex-based Deep Enhancement', icon: '🔆' },
  { id: 'C', label: 'C', name: 'MIRNet', description: 'Multi-Scale Residual Block Network', icon: '🧠' },
  { id: 'D', label: 'D', name: 'EnlightenGAN', description: 'Unsupervised GAN Enhancement', icon: '✨' },
  { id: 'E', label: 'E', name: 'RUAS', description: 'Retinex-inspired Unrolling Architecture', icon: '🔄' },
  { id: 'F', label: 'F', name: 'SNR-Aware', description: 'Signal-to-Noise Ratio Aware Model', icon: '📊' },
  { id: 'G', label: 'G', name: 'SCI', description: 'Self-Calibrated Illumination Learning', icon: '💎' },
];
