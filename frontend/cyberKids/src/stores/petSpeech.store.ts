import { computed, ref } from 'vue';
import dialoguesData from '@/data/pet_dialogues.json';
import { hasPetEquipped, currentPetId } from './petState.store';
import { TTSService } from '@/services/tts.service';
import { AudioService } from '@/services/audio.service';

export type PetSpeechBehavior = keyof typeof dialoguesData.behaviors | (string & {});

export interface PetSpeakOptions {
  behavior: PetSpeechBehavior;
  text?: string;
  vars?: Record<string, string | number | boolean | null | undefined>;
  ttlMs?: number;
  priority?: number;
  typingMsPerChar?: number;
  instant?: boolean;
}

const petVisible = ref(true);
const isOpen = ref(false);
const text = ref('');
const typedText = ref('');
const isTyping = ref(false);
const behavior = ref<PetSpeechBehavior | null>(null);
const currentPriority = ref(0);

// IDs de las mascotas femeninas (Grimorio Místico = mage:9, Flecha Precisa = ranger:11)
const FEMALE_PET_IDS = [9, 11];

// Nombres comunes de voces femeninas y masculinas
const FEMALE_VOICE_PATTERNS = [
  'female', 'woman', 'femenina', 'mujer',
  'helena', 'laura', 'monica', 'mónica', 'lucia', 'lucía', 'paulina',
  'sabina', 'paloma', 'elena', 'carmen', 'isabel', 'natalia'
];

const MALE_VOICE_PATTERNS = [
  'raul', 'raúl', 'jorge', 'diego', 'carlos', 'pablo', 'andrés', 'andres',
  'juan', 'miguel', 'pedro', 'francisco', 'javier', 'alberto'
];

// Obtener voz adecuada según el género de la mascota
async function getVoiceForPet(isFemale: boolean): Promise<string | undefined> {
  const voices = await TTSService.getVoices();
  
  console.log('[PetSpeech] 🔍 Voces disponibles:', voices.map(v => ({ name: v.name, lang: v.lang })));
  
  // Filtrar voces españolas
  const spanishVoices = voices.filter(v => v.lang.startsWith('es'));
  
  if (isFemale) {
    // Buscar voz específicamente femenina
    const femaleVoice = spanishVoices.find(v => {
      const nameLower = v.name.toLowerCase();
      // Primero excluir voces masculinas
      const isMale = MALE_VOICE_PATTERNS.some(pattern => nameLower.includes(pattern));
      if (isMale) return false;
      // Luego buscar patrones femeninos
      return FEMALE_VOICE_PATTERNS.some(pattern => nameLower.includes(pattern));
    });
    
    if (femaleVoice) {
      console.log('[PetSpeech] ✅ Voz femenina encontrada:', femaleVoice.name);
      return femaleVoice.voiceURI;
    }
    
    // Si no encuentra femenina explícita, usar la primera voz española que NO sea masculina
    const nonMaleVoice = spanishVoices.find(v => {
      const nameLower = v.name.toLowerCase();
      return !MALE_VOICE_PATTERNS.some(pattern => nameLower.includes(pattern));
    });
    
    if (nonMaleVoice) {
      console.log('[PetSpeech] ⚠️ Usando voz no-masculina:', nonMaleVoice.name);
      return nonMaleVoice.voiceURI;
    }
    
    console.log('[PetSpeech] ❌ No se encontró voz femenina, usando pitch alto');
  } else {
    // Buscar voz específicamente masculina
    const maleVoice = spanishVoices.find(v => {
      const nameLower = v.name.toLowerCase();
      return MALE_VOICE_PATTERNS.some(pattern => nameLower.includes(pattern));
    });
    
    if (maleVoice) {
      console.log('[PetSpeech] ✅ Voz masculina encontrada:', maleVoice.name);
      return maleVoice.voiceURI;
    }
    
    console.log('[PetSpeech] ⚠️ No se encontró voz masculina explícita');
  }
  
  // Fallback: primera voz española disponible
  if (spanishVoices.length > 0 && spanishVoices[0]) {
    console.log('[PetSpeech] 📢 Usando fallback:', spanishVoices[0].name);
    return spanishVoices[0].voiceURI;
  }
  
  return undefined;
}

// Configuración de voz reactiva que se actualiza cuando cambia la mascota
const petVoiceConfig = computed(() => {
  const petId = currentPetId.value;
  const isFemale = petId !== null && FEMALE_PET_IDS.includes(petId);
  return {
    pitch: isFemale ? 1.5 : 1.0,    // Pitch más alto si no hay voz femenina disponible
    rate: 1,                         // Velocidad normal
    isFemale,
  };
});

async function speakWithTTS(text: string) {
  if (!TTSService.isSupported()) return;
  
  // Detener cualquier TTS anterior para evitar errores de "interrupted"
  TTSService.stop();
  
  // Obtener la configuración reactiva actual
  const voiceConfig = petVoiceConfig.value;
  
  // Obtener la voz adecuada según el género
  const voiceURI = await getVoiceForPet(voiceConfig.isFemale);
  
  // Obtener el volumen ACTUAL del servicio (se actualiza dinámicamente)
  const currentVolume = AudioService.getPetTTSVolume();
  
  console.log('[PetSpeech] 🎤 Reproduciendo TTS:', { 
    petId: currentPetId.value, 
    isFemale: voiceConfig.isFemale,
    voiceURI,
    pitch: voiceConfig.pitch,
    rate: voiceConfig.rate,
    volume: currentVolume
  });
  
  try {
    await TTSService.speak({
      text,
      voiceURI,
      pitch: voiceConfig.pitch,
      rate: voiceConfig.rate,
      volume: currentVolume, // Usar volumen actual dinámico
      lang: 'es-ES',
    });
  } catch (error: any) {
    // Ignorar errores comunes del navegador (not-allowed, interrupted)
    if (error?.message !== 'not-allowed' && error?.message !== 'interrupted') {
      console.warn('[PetSpeech] Error al reproducir TTS:', error);
    }
  }
}

let hideTimer: number | null = null;
let typingTimer: number | null = null;

function clearHideTimer() {
  if (hideTimer !== null) {
    window.clearTimeout(hideTimer);
    hideTimer = null;
  }
}

function clearTypingTimer() {
  if (typingTimer !== null) {
    window.clearTimeout(typingTimer);
    typingTimer = null;
  }
}

function stopTyping() {
  clearTypingTimer();
  isTyping.value = false;
}

function formatTemplate(template: string, vars: Record<string, unknown>): string {
  return template.replace(/\{(\w+)\}/g, (_match, key: string) => {
    const value = vars[key];
    if (value === null || value === undefined) return '';
    return String(value);
  });
}

function pickDialogue(selectedBehavior: PetSpeechBehavior): string | null {
  const list = (dialoguesData.behaviors as Record<string, string[]>)[selectedBehavior];
  const fallback = dialoguesData.behaviors.idle;

  const candidates = Array.isArray(list) && list.length > 0 ? list : fallback;
  if (!candidates || candidates.length === 0) return null;

  const idx = Math.floor(Math.random() * candidates.length);
  return candidates[idx] ?? null;
}

function hide() {
  clearHideTimer();
  stopTyping();
  TTSService.stop(); // Detener TTS al ocultar
  isOpen.value = false;
  text.value = '';
  typedText.value = '';
  behavior.value = null;
  currentPriority.value = 0;
}

function setPetVisible(visible: boolean) {
  petVisible.value = visible;
  if (!visible) hide();
}

function speak(options: PetSpeakOptions) {
  // NO HABLAR SI NO HAY MASCOTA EQUIPADA
  if (!hasPetEquipped.value) return;
  if (!petVisible.value) return;

  const priority = options.priority ?? 0;
  if (isOpen.value && priority < currentPriority.value) return;

  const vars = {
    target: '',
    ...options.vars,
  } as Record<string, unknown>;

  const raw = options.text ?? pickDialogue(options.behavior) ?? '';
  const formatted = formatTemplate(raw, vars).trim();
  if (!formatted) return;

  clearHideTimer();
  stopTyping();

  behavior.value = options.behavior;
  currentPriority.value = priority;
  text.value = formatted;
  isOpen.value = true;

  // Reproducir TTS con la voz de la mascota
  speakWithTTS(formatted);

  const requestedHoldMs = options.ttlMs;
  const holdMsDefault = 3500;
  const holdMs = requestedHoldMs ?? holdMsDefault;

  // Instant mode (useful for hover hints if desired)
  if (options.instant) {
    typedText.value = formatted;
    isTyping.value = false;
    if (holdMs > 0) {
      hideTimer = window.setTimeout(() => hide(), holdMs);
    }
    return;
  }

  // Typewriter
  typedText.value = '';
  isTyping.value = true;

  const msPerChar = Math.max(10, options.typingMsPerChar ?? 28);
  const totalChars = formatted.length;
  let i = 0;

  const typeNext = () => {
    if (!isOpen.value) return;
    if (i >= totalChars) {
      typedText.value = formatted;
      isTyping.value = false;

      // TTL starts after typing finished (so text isn't cut off mid-sentence).
      if (holdMs > 0) {
        hideTimer = window.setTimeout(() => hide(), holdMs);
      }
      return;
    }

    i += 1;
    typedText.value = formatted.slice(0, i);

    const lastChar = formatted[i - 1] ?? '';
    const extraPause = lastChar === '.' || lastChar === '!' || lastChar === '?' ? 180 : lastChar === ',' || lastChar === ';' || lastChar === ':' ? 90 : 0;
    typingTimer = window.setTimeout(typeNext, msPerChar + extraPause);
  };

  typeNext();
}

function revealAll() {
  if (!isOpen.value) return;
  if (!text.value) return;
  stopTyping();
  typedText.value = text.value;
}

const petSpeechState = {
  petVisible,
  isOpen,
  text,
  typedText,
  isTyping,
  behavior,
  currentPriority,
};

export const PetSpeech = {
  state: petSpeechState,
  isVisible: computed(() => petVisible.value),
  isOpen: computed(() => isOpen.value),
  text: computed(() => text.value),
  typedText: computed(() => typedText.value),
  isTyping: computed(() => isTyping.value),
  behavior: computed(() => behavior.value),
  speak,
  hide,
  revealAll,
  setPetVisible,
};
