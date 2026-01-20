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
}

const petVisible = ref(true);
const isOpen = ref(false);
const text = ref('');
const behavior = ref<PetSpeechBehavior | null>(null);
const currentPriority = ref(0);

let hideTimer: number | null = null;

function clearHideTimer() {
  if (hideTimer !== null) {
    window.clearTimeout(hideTimer);
    hideTimer = null;
  }
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
  isOpen.value = false;
  text.value = '';
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

  behavior.value = options.behavior;
  currentPriority.value = priority;
  text.value = formatted;
  isOpen.value = true;

  const ttlMs = options.ttlMs ?? 3500;
  if (ttlMs > 0) {
    hideTimer = window.setTimeout(() => {
      hide();
    }, ttlMs);
  }
}

const petSpeechState = {
  petVisible,
  isOpen,
  text,
  behavior,
  currentPriority,
};

export const PetSpeech = {
  state: petSpeechState,
  isVisible: computed(() => petVisible.value),
  isOpen: computed(() => isOpen.value),
  text: computed(() => text.value),
  behavior: computed(() => behavior.value),
  speak,
  hide,
  setPetVisible,
};
