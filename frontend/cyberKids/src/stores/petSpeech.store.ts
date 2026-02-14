import { computed, ref } from 'vue';
import dialoguesData from '@/data/pet_dialogues.json';
import { hasPetEquipped } from './petState.store';

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
