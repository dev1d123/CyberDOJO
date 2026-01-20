import type { DirectiveBinding, ObjectDirective } from 'vue';
import { PetSpeech, type PetSpeakOptions } from '@/stores/petSpeech.store';

type HintConfig =
  | string
  | ({
      hover?: Omit<PetSpeakOptions, 'behavior'> & { behavior?: PetSpeakOptions['behavior'] };
      click?: Omit<PetSpeakOptions, 'behavior'> & { behavior?: PetSpeakOptions['behavior'] };
    } & (Omit<PetSpeakOptions, 'behavior'> & { behavior?: PetSpeakOptions['behavior'] }));

const HANDLERS = Symbol('pet-hint-handlers');

function isHoverBehavior(behavior: unknown): boolean {
  return behavior === 'hover' || behavior === 'hover_button' || behavior === 'hover_module' || behavior === 'logout_hover';
}

function getDefaultTarget(el: HTMLElement): string {
  const data = el.getAttribute('data-pet-label');
  if (data) return data;

  const aria = el.getAttribute('aria-label');
  if (aria) return aria;

  const title = el.getAttribute('title');
  if (title) return title;

  const text = (el.textContent ?? '').trim();
  if (text) return text.length > 40 ? `${text.slice(0, 40)}…` : text;

  return 'esto';
}

function normalize(value: unknown, el: HTMLElement): { hover?: PetSpeakOptions; click?: PetSpeakOptions } {
  const target = getDefaultTarget(el);

  if (typeof value === 'string') {
    return {
      hover: { behavior: 'hover', text: value, vars: { target }, ttlMs: 0, priority: 1 },
      click: { behavior: 'click', vars: { target }, ttlMs: 1800, priority: 1 },
    };
  }

  if (!value || typeof value !== 'object') {
    return {
      hover: { behavior: 'hover', vars: { target }, ttlMs: 0, priority: 1 },
      click: { behavior: 'click', vars: { target }, ttlMs: 1600, priority: 1 },
    };
  }

  const v = value as any;

  const baseBehavior = (v.behavior ?? 'hover') as PetSpeakOptions['behavior'];
  const base: PetSpeakOptions = {
    behavior: baseBehavior,
    text: v.text,
    vars: { target, ...(v.vars ?? {}) },
    ttlMs: v.ttlMs,
    priority: v.priority,
  };

  const hoverCfg = v.hover
    ? {
        behavior: (v.hover.behavior ?? base.behavior) as PetSpeakOptions['behavior'],
        text: v.hover.text ?? base.text,
        vars: { ...(base.vars ?? {}), ...(v.hover.vars ?? {}) },
        ttlMs: v.hover.ttlMs ?? base.ttlMs,
        priority: v.hover.priority ?? base.priority,
      }
    : undefined;

  const clickCfg = v.click
    ? {
        behavior: (v.click.behavior ?? 'click') as PetSpeakOptions['behavior'],
        text: v.click.text,
        vars: { target, ...(v.click.vars ?? {}) },
        ttlMs: v.click.ttlMs,
        priority: v.click.priority,
      }
    : undefined;

  // If no explicit hover/click is provided, reuse base for hover and default click.
  return {
    hover:
      hoverCfg ??
      {
        ...base,
        // Default for hover hints: stay until leaving element
        ttlMs: base.ttlMs ?? 0,
        priority: base.priority ?? 1,
      },
    click: clickCfg ?? { behavior: 'click', vars: { target }, ttlMs: 1600, priority: 1 },
  };
}

export const petHintDirective: ObjectDirective<HTMLElement, HintConfig> = {
  mounted(el, binding: DirectiveBinding<HintConfig>) {
    const cfg = normalize(binding.value, el);

    const onEnter = () => {
      if (cfg.hover) PetSpeech.speak(cfg.hover);
    };

    const onLeave = () => {
      const current = PetSpeech.behavior.value;
      if (isHoverBehavior(current)) {
        PetSpeech.hide();
      }
    };

    const onClick = () => {
      if (cfg.click) PetSpeech.speak(cfg.click);
    };

    (el as any)[HANDLERS] = { onEnter, onLeave, onClick };

    // Pointer events work better across devices; keep mouseenter as fallback.
    el.addEventListener('pointerenter', onEnter);
    el.addEventListener('mouseenter', onEnter);
    el.addEventListener('focusin', onEnter);

    el.addEventListener('pointerleave', onLeave);
    el.addEventListener('mouseleave', onLeave);
    el.addEventListener('blur', onLeave);

    el.addEventListener('pointerdown', onClick);
    el.addEventListener('click', onClick);
  },

  updated(el, binding) {
    // If the binding changes, re-normalize by re-mounting handlers.
    const handlers = (el as any)[HANDLERS] as { onEnter: () => void; onLeave: () => void; onClick: () => void } | undefined;
    if (!handlers) return;

    el.removeEventListener('pointerenter', handlers.onEnter);
    el.removeEventListener('mouseenter', handlers.onEnter);
    el.removeEventListener('focusin', handlers.onEnter);
    el.removeEventListener('pointerleave', handlers.onLeave);
    el.removeEventListener('mouseleave', handlers.onLeave);
    el.removeEventListener('blur', handlers.onLeave);
    el.removeEventListener('pointerdown', handlers.onClick);
    el.removeEventListener('click', handlers.onClick);

    const cfg = normalize(binding.value, el);

    const onEnter = () => {
      if (cfg.hover) PetSpeech.speak(cfg.hover);
    };

    const onLeave = () => {
      const current = PetSpeech.behavior.value;
      if (isHoverBehavior(current)) {
        PetSpeech.hide();
      }
    };

    const onClick = () => {
      if (cfg.click) PetSpeech.speak(cfg.click);
    };

    (el as any)[HANDLERS] = { onEnter, onLeave, onClick };

    el.addEventListener('pointerenter', onEnter);
    el.addEventListener('mouseenter', onEnter);
    el.addEventListener('focusin', onEnter);

    el.addEventListener('pointerleave', onLeave);
    el.addEventListener('mouseleave', onLeave);
    el.addEventListener('blur', onLeave);

    el.addEventListener('pointerdown', onClick);
    el.addEventListener('click', onClick);
  },

  unmounted(el) {
    const handlers = (el as any)[HANDLERS] as { onEnter: () => void; onLeave: () => void; onClick: () => void } | undefined;
    if (!handlers) return;

    el.removeEventListener('pointerenter', handlers.onEnter);
    el.removeEventListener('mouseenter', handlers.onEnter);
    el.removeEventListener('focusin', handlers.onEnter);
    el.removeEventListener('pointerleave', handlers.onLeave);
    el.removeEventListener('mouseleave', handlers.onLeave);
    el.removeEventListener('blur', handlers.onLeave);
    el.removeEventListener('pointerdown', handlers.onClick);
    el.removeEventListener('click', handlers.onClick);
    delete (el as any)[HANDLERS];
  },
};
