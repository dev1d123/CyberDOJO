export type SpeakOptions = {
  text: string;
  voiceURI?: string;
  lang?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
};

class TTSServiceClass {
  private voicesCache: SpeechSynthesisVoice[] = [];
  private voicesReadyPromise: Promise<void> | null = null;

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined';
  }

  async ensureVoicesReady(): Promise<void> {
    if (!this.isSupported()) return;

    if (this.voicesCache.length > 0) return;
    if (this.voicesReadyPromise) return this.voicesReadyPromise;

    this.voicesReadyPromise = new Promise<void>((resolve) => {
      const tryLoad = () => {
        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length > 0) {
          this.voicesCache = voices;
          resolve();
          return true;
        }
        return false;
      };

      if (tryLoad()) return;

      const handleVoicesChanged = () => {
        if (tryLoad()) {
          window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged);
        }
      };

      window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged);

      // Fallback: algunos browsers no disparan voiceschanged consistentemente
      setTimeout(() => {
        tryLoad();
        resolve();
      }, 750);
    }).finally(() => {
      this.voicesReadyPromise = null;
    });

    return this.voicesReadyPromise;
  }

  async getVoices(): Promise<SpeechSynthesisVoice[]> {
    if (!this.isSupported()) return [];
    await this.ensureVoicesReady();
    if (this.voicesCache.length === 0) {
      this.voicesCache = window.speechSynthesis.getVoices();
    }
    return this.voicesCache;
  }

  stop(): void {
    if (!this.isSupported()) return;
    window.speechSynthesis.cancel();
  }

  async speak(options: SpeakOptions): Promise<void> {
    if (!this.isSupported()) {
      throw new Error('Tu navegador no soporta Text-to-Speech (speechSynthesis).');
    }

    const text = (options.text ?? '').trim();
    if (!text) return;

    await this.ensureVoicesReady();

    // Cancelar cualquier locución previa
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    if (options.lang) utterance.lang = options.lang;
    if (typeof options.rate === 'number') utterance.rate = options.rate;
    if (typeof options.pitch === 'number') utterance.pitch = options.pitch;
    if (typeof options.volume === 'number') utterance.volume = options.volume;

    if (options.voiceURI) {
      const voices = await this.getVoices();
      const voice = voices.find(v => v.voiceURI === options.voiceURI);
      if (voice) utterance.voice = voice;
    }

    await new Promise<void>((resolve, reject) => {
      utterance.onend = () => resolve();
      utterance.onerror = (e) => reject(new Error((e as any)?.error || 'Error reproduciendo TTS'));
      window.speechSynthesis.speak(utterance);
    });
  }
}

export const TTSService = new TTSServiceClass();
