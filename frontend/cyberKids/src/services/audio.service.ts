import soundsData from '../data/sounds.json';
import { CosmeticService } from './cosmetic.service';

type SoundType = 'click' | 'send' | 'receive' | 'dialog' | 'background';

interface SoundTheme {
  item_id: number;
  name: string;
  sounds: {
    click: string;
    send: string;
    receive: string;
    dialog: string;
    background: string;
  };
}

class AudioServiceClass {
  private currentTheme: SoundTheme | null = null;
  private audioCache: Map<string, HTMLAudioElement> = new Map();
  private backgroundMusic: HTMLAudioElement | null = null;
  private quizSfxCache: Map<string, HTMLAudioElement> = new Map();
  private isMuted: boolean = false;
  private backgroundMusicVolume: number = 0.3;
  private sfxVolume: number = 0.5;
  private petTTSVolume: number = 1.5; // Inicial: 1.5x para mayor audibilidad
  private shouldPlayBackground: boolean = true;
  private readonly quizSfxBoost: number = 2.0;

  private themeLoaded: Promise<void>;

  constructor() {
    this.themeLoaded = this.loadUserTheme();
  }

  private isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  async loadUserTheme(): Promise<void> {
    // Siempre intentar cargar el tema del usuario si está autenticado
    if (this.isAuthenticated()) {
      try {
        const purchases = await CosmeticService.getMyPurchases();
        const equippedAudio = purchases.cosmetics.find(c => c.is_equipped);
        
        if (equippedAudio) {
          const theme = soundsData.soundThemes.find(t => t.item_id === equippedAudio.item);
          if (theme) {
            this.currentTheme = theme;
            console.log('🎵 [AudioService] Tema de audio cargado:', theme.name);
            this.preloadSounds();
            return;
          }
        }
      } catch (error) {
        console.error('❌ [AudioService] Error cargando tema de usuario:', error);
      }
    }
    
    // Siempre cargar tema por defecto (esté o no autenticado)
    this.currentTheme =
      soundsData.soundThemes.find(t => t.item_id === soundsData.defaultTheme) ??
      soundsData.soundThemes[0] ??
      null;
    if (this.currentTheme) {
      console.log('🎵 [AudioService] Usando tema por defecto:', this.currentTheme.name);
    }
    this.preloadSounds();
  }

  private preloadSounds(): void {
    if (!this.currentTheme) return;

    Object.entries(this.currentTheme.sounds).forEach(([type, path]) => {
      if (type !== 'background') {
        const audio = new Audio(path);
        audio.preload = 'auto';
        audio.volume = this.sfxVolume;
        this.audioCache.set(type, audio);
      }
    });

    console.log('🎵 [AudioService] Sonidos precargados');
  }

  private getSound(type: SoundType): HTMLAudioElement | null {
    if (!this.currentTheme || this.isMuted) return null;

    if (type === 'background') {
      if (!this.backgroundMusic) {
        this.backgroundMusic = new Audio(this.currentTheme.sounds.background);
        this.backgroundMusic.loop = true;
        this.backgroundMusic.volume = this.backgroundMusicVolume;
      }
      return this.backgroundMusic;
    }

    let audio = this.audioCache.get(type);
    if (!audio) {
      audio = new Audio(this.currentTheme.sounds[type]);
      audio.volume = this.sfxVolume;
      this.audioCache.set(type, audio);
    }
    return audio;
  }

  playClick(): void {
    if (!this.isAuthenticated()) return;
    const audio = this.getSound('click');
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(err => console.warn('Error playing click sound:', err));
    }
  }

  playSend(): void {
    if (!this.isAuthenticated()) return;
    const audio = this.getSound('send');
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(err => console.warn('Error playing send sound:', err));
    }
  }

  playReceive(): void {
    if (!this.isAuthenticated()) return;
    const audio = this.getSound('receive');
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(err => console.warn('Error playing receive sound:', err));
    }
  }

  playDialog(): void {
    if (!this.isAuthenticated()) return;
    const audio = this.getSound('dialog');
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(err => console.warn('Error playing dialog sound:', err));
    }
  }

  async playBackgroundMusic(): Promise<void> {
    if (!this.isAuthenticated()) {
      return;
    }

    this.shouldPlayBackground = true;
    await this.startBackgroundMusic();
  }

  private async startBackgroundMusic(): Promise<void> {
    await this.themeLoaded;
    const audio = this.getSound('background');
    if (audio) {
      if (audio.paused) {
        try {
          await audio.play();
          console.log('🎵 [AudioService] Background music started');
        } catch (err) {
          // Silenciar error - se intentará en el próximo click
        }
      }
    }
  }

  pauseBackgroundMusic(): void {
    if (this.backgroundMusic && !this.backgroundMusic.paused) {
      this.backgroundMusic.pause();
    }
  }

  stopBackgroundMusic(): void {
    this.shouldPlayBackground = false;
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
      this.backgroundMusic.currentTime = 0;
    }
  }

  setMuted(muted: boolean): void {
    this.isMuted = muted;
    if (muted) {
      this.pauseBackgroundMusic();
    } else if (this.shouldPlayBackground) {
      this.startBackgroundMusic();
    }
  }

  toggleMute(): void {
    this.setMuted(!this.isMuted);
  }

  setBackgroundVolume(volume: number): void {
    // Cap intencional para evitar música demasiado alta
    this.backgroundMusicVolume = Math.max(0, Math.min(0.5, volume));
    if (this.backgroundMusic) {
      this.backgroundMusic.volume = this.backgroundMusicVolume;
    }
  }

  setSFXVolume(volume: number): void {
    // Cap intencional para evitar SFX demasiado altos
    this.sfxVolume = Math.max(0, Math.min(0.7, volume));
    this.audioCache.forEach(audio => {
      audio.volume = this.sfxVolume;
    });
    this.quizSfxCache.forEach(audio => {
      audio.volume = Math.min(1, this.sfxVolume * this.quizSfxBoost);
    });
  }

  getMuted(): boolean {
    return this.isMuted;
  }

  getBackgroundVolume(): number {
    return this.backgroundMusicVolume;
  }

  getSFXVolume(): number {
    return this.sfxVolume;
  }

  setPetTTSVolume(volume: number): void {
    this.petTTSVolume = Math.max(0, Math.min(5, volume));
  }

  getPetTTSVolume(): number {
    return this.petTTSVolume;
  }

  private async fadeOut(audio: HTMLAudioElement, duration: number = 1000): Promise<void> {
    const startVolume = audio.volume;
    const steps = 20;
    const stepDuration = duration / steps;
    const volumeDecrement = startVolume / steps;

    for (let i = 0; i < steps; i++) {
      audio.volume = Math.max(0, startVolume - (volumeDecrement * (i + 1)));
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    audio.volume = 0;
  }

  private async fadeIn(audio: HTMLAudioElement, targetVolume: number, duration: number = 1000): Promise<void> {
    audio.volume = 0;
    const steps = 20;
    const stepDuration = duration / steps;
    const volumeIncrement = targetVolume / steps;

    for (let i = 0; i < steps; i++) {
      audio.volume = Math.min(targetVolume, volumeIncrement * (i + 1));
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    audio.volume = targetVolume;
  }

  async reloadTheme(): Promise<void> {
    const wasPlaying = this.shouldPlayBackground && this.backgroundMusic && !this.backgroundMusic.paused;
    
    // Fade out de la música actual si está sonando
    if (wasPlaying && this.backgroundMusic) {
      console.log('🎵 [AudioService] Fade out del tema actual...');
      await this.fadeOut(this.backgroundMusic, 800);
    }
    
    // Detener sin cambiar shouldPlayBackground
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
      this.backgroundMusic.currentTime = 0;
    }
    
    // Limpiar audio cache
    this.audioCache.clear();
    this.currentTheme = null;
    this.backgroundMusic = null;
    
    // Cargar nuevo tema
    await this.loadUserTheme();
    
    // Siempre reproducir la nueva música si estaba sonando antes O si shouldPlayBackground está activo
    if ((wasPlaying || this.shouldPlayBackground) && this.isAuthenticated()) {
      console.log('🎵 [AudioService] Fade in del nuevo tema...');
      this.shouldPlayBackground = true; // Asegurar que está activo
      const newAudio = this.getSound('background');
      if (newAudio) {
        try {
          await newAudio.play();
          await this.fadeIn(newAudio, this.backgroundMusicVolume, 800);
          console.log('✅ [AudioService] Nuevo tema reproduciendo');
        } catch (err) {
          console.warn('⚠️ Error al reproducir nueva música:', err);
        }
      }
    }
  }

  // ===== QUIZ SFX METHODS ====
  private getQuizSfx(path: string): HTMLAudioElement {
    let audio = this.quizSfxCache.get(path);
    if (!audio) {
      audio = new Audio(path);
      audio.preload = 'auto';
      this.quizSfxCache.set(path, audio);
    }
    audio.volume = Math.min(1, this.sfxVolume * this.quizSfxBoost);
    return audio;
  }

  playQuizCorrect(): void {
    if (this.isMuted) return;
    const audio = this.getQuizSfx('/sounds/quiz/correct_answer.mp3');
    audio.currentTime = 0;
    audio.play().catch(() => {
      console.warn('Error playing correct sound');
    });
  }

  playQuizWrong(): void {
    if (this.isMuted) return;
    const audio = this.getQuizSfx('/sounds/quiz/Voicy_Quiz%20Player%20Loser.mp3');
    audio.currentTime = 0;
    audio.play().catch(() => {
      console.warn('Error playing wrong sound');
    });
  }

  playQuizWin(): void {
    if (this.isMuted) return;
    const audio = this.getQuizSfx('/sounds/quiz/Voicy_win.mp3');
    audio.currentTime = 0;
    audio.play().catch(() => {
      console.warn('Error playing win sound');
    });
  }

  playQuizDefeat(): void {
    if (this.isMuted) return;
    const audio = this.getQuizSfx('/sounds/quiz/sfx-defeat6.mp3');
    audio.currentTime = 0;
    audio.play().catch(() => {
      console.warn('Error playing defeat sound');
    });
  }

  cleanup(): void {
    console.log('🎵 [AudioService] Limpiando audio por cierre de sesión');
    this.shouldPlayBackground = false;
    this.stopBackgroundMusic();
    this.audioCache.clear();
    this.quizSfxCache.clear();
    this.currentTheme = null;
    this.backgroundMusic = null;
  }
}

export const AudioService = new AudioServiceClass();
