<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { UserService } from '@/services/user.service';
import PetSpeechBubble from './PetSpeechBubble.vue';
import { PetSpeech } from '@/stores/petSpeech.store';
import { setPetEquipped } from '@/stores/petState.store';

const route = useRoute();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const petContainer = ref<HTMLDivElement | null>(null);
void petContainer;
const isVisible = ref(true);
const loading = ref(false);
const petOpacity = ref(1);
const currentPetId = ref<number | null>(null);

let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let renderer: THREE.WebGLRenderer | null = null;
let mixer: THREE.AnimationMixer | null = null;
let clock: THREE.Clock | null = null;
let animationFrame: number | null = null;
let allAnimations: THREE.AnimationClip[] = [];
let model3D: THREE.Group | null = null;
let currentAction: THREE.AnimationAction | null = null;

const PET_RENDER_SIZE = 340;
const PET_HALF = PET_RENDER_SIZE / 2;
const PET_HOVER_DIM_OPACITY = 0.45;

// Posición base y área de movimiento
const basePosition = { x: window.innerWidth - (PET_RENDER_SIZE + 50), y: window.innerHeight - (PET_RENDER_SIZE + 50) };
const petPosition = ref({ x: basePosition.x, y: basePosition.y });
const targetPosition = ref({ x: basePosition.x, y: basePosition.y });
const isWalking = ref(false);
const movementRadius = 80; // Radio de movimiento desde la posición base
const isPerformingGesture = ref(false);
const isTalking = ref(false);
const isHoveringPet = ref(false);

let hoverRaf: number | null = null;
let lastPointer: { x: number; y: number } | null = null;

function computeHover(pointer: { x: number; y: number }) {
  const petEl = petContainer.value;
  if (!petEl || !isVisible.value) {
    isHoveringPet.value = false;
    return;
  }

  const petRect = petEl.getBoundingClientRect();
  const inPet =
    pointer.x >= petRect.left &&
    pointer.x <= petRect.right &&
    pointer.y >= petRect.top &&
    pointer.y <= petRect.bottom;

  // Also include the speech bubble area so both dim together while hovering near it.
  const bubbleEl = document.querySelector('.pet-speech') as HTMLElement | null;
  let inBubble = false;
  if (bubbleEl) {
    const bubbleRect = bubbleEl.getBoundingClientRect();
    inBubble =
      pointer.x >= bubbleRect.left &&
      pointer.x <= bubbleRect.right &&
      pointer.y >= bubbleRect.top &&
      pointer.y <= bubbleRect.bottom;
  }

  isHoveringPet.value = inPet || inBubble;
}

function handlePointerMove(event: PointerEvent) {
  lastPointer = { x: event.clientX, y: event.clientY };
  if (hoverRaf !== null) return;
  hoverRaf = requestAnimationFrame(() => {
    hoverRaf = null;
    if (lastPointer) computeHover(lastPointer);
  });
}

function handlePointerLeaveWindow() {
  isHoveringPet.value = false;
}

// Mapeo de pet_id a modelo
const petModelMap: Record<number, string> = {
  7: 'barbarian',
  8: 'knight',
  9: 'mage',
  10: 'ranger',
  11: 'rogue'
};

// Mapeo de animaciones por contexto
const contextAnimations = {
  idle: ['Player_Idle_A', 'Player_Idle_B'],
  walking: ['Player_Walking_A', 'Player_Walking_B', 'Player_Walking_C', 'Player_Running_A'],
  random: [
    'Player_Jump_Full_Short', 'Player_Jump_Full_Long', 'Player_Cheering', 
    'Player_Waving', 'Player_Interact', 'Player_PickUp', 'Player_Use_Item',
    'Player_Throw', 'Player_Jump_Start', 'Player_Sit_Ups'
  ],
  sadness: ['Player_Lie_Down', 'Player_Sit_Floor_Down', 'Player_Death_A'],
  pushup: ['Player_Push_Ups', 'Player_Sit_Ups', 'Player_Lie_Down', 'Player_Sit_Floor_Idle'],
  battle: [
    'Player_Hit_A', 'Player_Hit_B', 'Player_Throw', 'Player_Use_Item',
    'Player_Running_B', 'Player_Jump_Full_Long', 'Player_Cheering'
  ],
  chatting: ['Player_Idle_B', 'Player_Interact', 'Player_PickUp', 'Player_Waving'],
  victory: ['Player_Cheering', 'Player_Waving', 'Player_Jump_Full_Long', 'Player_Jump_Full_Short'],
  taunt: ['Player_Idle_B', 'Player_Cheering', 'Player_Waving'],
  defeat: ['Player_Death_A', 'Player_Death_B', 'Player_Lie_Down', 'Player_Sit_Floor_Down']
};

let idleInterval: number | null = null;
let randomGestureInterval: number | null = null;
let petCheckInterval: number | null = null;
let idleTalkInterval: number | null = null;
let logoutCheckInterval: number | null = null;
let chatCheckInterval: number | null = null;

onMounted(async () => {
  await loadUserPet();
  startRandomGestures();
  startRandomWalking();
  setupClickListener();
  startPetChecker();
  setupEventListeners();
  PetSpeech.setPetVisible(isVisible.value);
  startIdleTalk();

  window.addEventListener('pointermove', handlePointerMove, { passive: true });
  window.addEventListener('blur', handlePointerLeaveWindow);
  document.addEventListener('mouseleave', handlePointerLeaveWindow);
});

onUnmounted(() => {
  cleanup();
  removeClickListener();
  window.removeEventListener('pointermove', handlePointerMove);
  window.removeEventListener('blur', handlePointerLeaveWindow);
  document.removeEventListener('mouseleave', handlePointerLeaveWindow);
  if (hoverRaf !== null) {
    cancelAnimationFrame(hoverRaf);
    hoverRaf = null;
  }

  if (idleInterval) clearInterval(idleInterval);
  if (randomGestureInterval) clearInterval(randomGestureInterval);
  if (petCheckInterval) clearInterval(petCheckInterval);
  if (idleTalkInterval) clearInterval(idleTalkInterval);
  if (logoutCheckInterval) clearInterval(logoutCheckInterval);
  if (chatCheckInterval) clearInterval(chatCheckInterval);

  if (logoutButton) logoutButton.removeEventListener('mouseenter', handleLogoutHover);
  if (chatInputs) {
    chatInputs.forEach(input => {
      input.removeEventListener('focus', handleChatFocus);
      input.removeEventListener('blur', handleChatBlur);
    });
  }
});

const loadUserPet = async () => {
  try {
    const user = await UserService.getCurrentUser();
    if (user.pet_id) {
      // Actualizar el store global
      setPetEquipped(user.pet_id);
      
      // Si cambió la mascota equipada, hacer transición
      if (currentPetId.value !== null && currentPetId.value !== user.pet_id) {
        await transitionToPet(user.pet_id);
      } else {
        currentPetId.value = user.pet_id;
        const modelName = petModelMap[user.pet_id];
        if (modelName) {
          await loadModel(modelName);
        }
      }
    } else {
      // No hay mascota equipada
      setPetEquipped(null);
    }
  } catch (error) {
    console.error('Error cargando mascota:', error);
    setPetEquipped(null);
  }
};

const transitionToPet = async (newPetId: number) => {
  // Fade out
  petOpacity.value = 0;
  
  // Esperar que termine el fade out
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Cambiar mascota
  currentPetId.value = newPetId;
  const modelName = petModelMap[newPetId];
  if (modelName) {
    await loadModel(modelName);
  }
  
  // Fade in
  petOpacity.value = 1;
};

const startPetChecker = () => {
  // Verificar cada 3 segundos si cambió la mascota equipada
  petCheckInterval = window.setInterval(async () => {
    try {
      const user = await UserService.getCurrentUser();
      if (user.pet_id) {
        // Si no hay mascota cargada, cargarla
        if (currentPetId.value === null) {
          await loadUserPet();
        }
        // Si cambió la mascota, hacer transición
        else if (currentPetId.value !== user.pet_id) {
          await transitionToPet(user.pet_id);
        }
      }
    } catch (error: any) {
      // Ignorar errores silenciosamente, pero detener si es error de auth
      if (error?.status === 401 || error?.status === 403) {
        if (petCheckInterval) {
          clearInterval(petCheckInterval);
          petCheckInterval = null;
          console.warn('🛑 [PetViewer] 401 Auth error detected. Stopping pet check interval.');
        }
      }
    }
  }, 3000);
};

const loadModel = async (modelName: string) => {
  if (!canvasRef.value) return;
  
  loading.value = true;
  cleanup();

  // Configurar escena
  scene = new THREE.Scene();
  
  camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);

  renderer = new THREE.WebGLRenderer({ 
    canvas: canvasRef.value,
    antialias: true,
    alpha: true
  });
  renderer.setSize(PET_RENDER_SIZE, PET_RENDER_SIZE);
  renderer.setPixelRatio(window.devicePixelRatio);

  // Luces
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
  directionalLight.position.set(5, 10, 5);
  scene.add(directionalLight);

  // Cargar modelo
  const loader = new GLTFLoader();
  try {
    const modelPath = new URL(`../assets/models/${modelName}.glb`, import.meta.url).href;
    const gltf = await loader.loadAsync(modelPath);
    
    model3D = gltf.scene;
    model3D.position.set(0, 0, 0);
    scene.add(model3D);

    // Frame model so legs/head aren't clipped (robust across pets)
    if (camera && model3D) {
      const box = new THREE.Box3().setFromObject(model3D);
      const center = box.getCenter(new THREE.Vector3());

      // Center XZ; put feet at y=0
      model3D.position.x += -center.x;
      model3D.position.z += -center.z;
      model3D.position.y += -box.min.y;

      const framedBox = new THREE.Box3().setFromObject(model3D);
      const framedSize = framedBox.getSize(new THREE.Vector3());
      const maxDim = Math.max(framedSize.x, framedSize.y, framedSize.z);
      const fovRad = (camera.fov * Math.PI) / 180;
      let cameraZ = Math.abs((maxDim / 2) / Math.tan(fovRad / 2));
      cameraZ *= 1.35;

      camera.position.set(0, framedSize.y * 0.55, cameraZ);
      camera.near = Math.max(0.01, cameraZ / 100);
      camera.far = cameraZ * 100;
      camera.updateProjectionMatrix();
      camera.lookAt(0, framedSize.y * 0.45, 0);
    }

    if (gltf.animations && gltf.animations.length > 0) {
      clock = new THREE.Clock();
      mixer = new THREE.AnimationMixer(model3D);
      allAnimations = gltf.animations;
      currentAction = null;
      playRandomAnimation(contextAnimations.idle);
    }

    loading.value = false;
    animate();
  } catch (error) {
    console.error('Error cargando modelo:', error);
    loading.value = false;
  }
};

const playAnimation = (animationName: string, loop: boolean = true) => {
  if (!mixer || !allAnimations.length) return;

  const clip = allAnimations.find(clip => clip.name === animationName);
  
  if (clip) {
    const action = mixer.clipAction(clip);
    if (currentAction === action) return;

    action.reset();
    action.enabled = true;
    action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, loop ? Infinity : 1);
    action.clampWhenFinished = true;
    action.play();

    const fadeSeconds = 0.22;
    if (currentAction) {
      currentAction.crossFadeTo(action, fadeSeconds, false);
    } else {
      action.fadeIn(fadeSeconds);
    }

    currentAction = action;
  }
};

const playRandomAnimation = (animList: string[]) => {
  const randomAnim = animList[Math.floor(Math.random() * animList.length)];
  if (randomAnim) {
    playAnimation(randomAnim);
  }
};

const animate = () => {
  if (!scene || !camera || !renderer) return;

  animationFrame = requestAnimationFrame(animate);

  if (mixer && clock) {
    mixer.update(clock.getDelta());
  }

  // Movimiento hacia el target
  if (isWalking.value) {
    const dx = targetPosition.value.x - petPosition.value.x;
    const dy = targetPosition.value.y - petPosition.value.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance > 2) {
      const speed = 0.8;
      petPosition.value.x += (dx / distance) * speed;
      petPosition.value.y += (dy / distance) * speed;
      
      // Rotar modelo hacia la dirección del movimiento
      if (model3D) {
        const angle = Math.atan2(dx, dy);
        model3D.rotation.y = angle;
      }
    } else {
      isWalking.value = false;
      if (!isPerformingGesture.value) {
        playRandomAnimation(contextAnimations.idle);
      }
      // Esperar un poco y luego elegir nuevo destino
      setTimeout(() => {
        if (!isWalking.value) {
          chooseRandomTarget();
        }
      }, Math.random() * 2000 + 1500);
    }
  }

  renderer.render(scene, camera);
};

const cleanup = () => {
  if (animationFrame !== null) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }

  if (mixer) {
    mixer.stopAllAction();
    mixer = null;
  }

  if (renderer) {
    renderer.dispose();
    renderer = null;
  }

  if (scene) {
    scene.traverse((object: any) => {
      if (object instanceof THREE.Mesh) {
        object.geometry.dispose();
        if (Array.isArray(object.material)) {
          object.material.forEach((material: any) => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
    scene = null;
  }

  clock = null;
  allAnimations = [];
  model3D = null;
};

const chooseRandomTarget = () => {
  if (!isVisible.value) return;
  if (isTalking.value || PetSpeech.isOpen.value) return;
  
  // Elegir punto aleatorio dentro del radio de movimiento
  const angle = Math.random() * Math.PI * 2;
  const distance = Math.random() * movementRadius;
  
  let newX = basePosition.x + Math.cos(angle) * distance;
  let newY = basePosition.y + Math.sin(angle) * distance;
  
  // Asegurar que no se salga de los límites de la pantalla
  const margin = 50;
  newX = Math.max(margin, Math.min(window.innerWidth - PET_RENDER_SIZE - margin, newX));
  newY = Math.max(margin, Math.min(window.innerHeight - PET_RENDER_SIZE - margin, newY));
  
  targetPosition.value = { x: newX, y: newY };
  
  isWalking.value = true;
  playRandomAnimation(contextAnimations.walking);
};

const startRandomWalking = () => {
  // Iniciar primer movimiento
  setTimeout(() => {
    chooseRandomTarget();
  }, 2000);
};

const handleScreenClick = (event: MouseEvent) => {
  if (!isVisible.value) return;
  
  // Evitar clicks en el botón toggle
  const target = event.target as HTMLElement;
  if (target.closest('.toggle-btn')) return;

  PetSpeech.speak({ behavior: 'click_screen', ttlMs: 1600, priority: 0 });
  
  // Calcular ángulo hacia el click
  const clickX = event.clientX;
  const clickY = event.clientY;
  
  const dx = clickX - (petPosition.value.x + PET_HALF);
  const dy = clickY - (petPosition.value.y + PET_HALF);
  
  // Rotar modelo hacia el click
  if (model3D) {
    const angle = Math.atan2(dx, dy);
    
    // Animación suave de rotación
    const startRotation = model3D.rotation.y;
    const endRotation = angle;
    const duration = 500; // ms
    const startTime = Date.now();
    
    const rotateToClick = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Interpolar ángulo
      let diff = endRotation - startRotation;
      // Normalizar diferencia de ángulo
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      
      if (model3D) {
        model3D.rotation.y = startRotation + diff * progress;
      }
      
      if (progress < 1) {
        requestAnimationFrame(rotateToClick);
      } else {
        // Al terminar de girar, hacer un gesto
        if (!isPerformingGesture.value) {
          isPerformingGesture.value = true;
          playRandomAnimation(['Player_Waving', 'Player_Cheering', 'Player_Interact', 'Player_Jump_Full_Short']);
          setTimeout(() => {
            isPerformingGesture.value = false;
            if (isWalking.value) {
              playRandomAnimation(contextAnimations.walking);
            } else {
              playRandomAnimation(contextAnimations.idle);
            }
          }, 2500);
        }
      }
    };
    
    rotateToClick();
  }
};

const setupClickListener = () => {
  document.addEventListener('click', handleScreenClick);
};

const removeClickListener = () => {
  document.removeEventListener('click', handleScreenClick);
};

const startRandomGestures = () => {
  randomGestureInterval = window.setInterval(() => {
    // Solo si está visible, no está hablando, y con probabilidad
    if (!isVisible.value) return;
    if (isPerformingGesture.value) return;
    if (PetSpeech.isOpen.value) return;
    
    // Mayor frecuencia de gestos
    if (Math.random() > 0.5) {
      isPerformingGesture.value = true;
      const wasWalking = isWalking.value;
      
      playRandomAnimation(contextAnimations.random);
      
      // Garantizar retorno a estado base después de animación
      setTimeout(() => {
        isPerformingGesture.value = false;
        
        // Siempre volver a un estado válido
        if (wasWalking || isWalking.value) {
          playRandomAnimation(contextAnimations.walking);
        } else {
          playRandomAnimation(contextAnimations.idle);
        }
        
        // Reanudar ciclo de movimiento si no está caminando
        if (!isWalking.value && !PetSpeech.isOpen.value) {
          setTimeout(() => {
            if (!isWalking.value && !isPerformingGesture.value) {
              chooseRandomTarget();
            }
          }, 1500);
        }
      }, 2500);
    } else if (!isWalking.value && !isPerformingGesture.value) {
      // Si no hace gesto, considerar iniciar movimiento
      if (Math.random() > 0.7) {
        chooseRandomTarget();
      } else {
        // O mantener animación idle activa
        playRandomAnimation(contextAnimations.idle);
      }
    }
  }, 4000); // Cada 4 segundos para más vida
};

// Event listeners específicos por contexto (sin click en pantalla)
let logoutButton: HTMLElement | null = null;
let chatInputs: NodeListOf<HTMLInputElement> | null = null;

const setupEventListeners = () => {
  // Detectar hover en logout
  logoutCheckInterval = window.setInterval(() => {
    if (logoutButton) return;
    logoutButton = document.querySelector('[data-logout-btn]') as HTMLElement;
    if (logoutButton) {
      logoutButton.addEventListener('mouseenter', handleLogoutHover);
      if (logoutCheckInterval) {
        clearInterval(logoutCheckInterval);
        logoutCheckInterval = null;
      }
    }
  }, 1000);

  // Detectar inputs de chat
  chatCheckInterval = window.setInterval(() => {
    if (chatInputs && chatInputs.length > 0) return;
    chatInputs = document.querySelectorAll('input[type="text"], textarea');
    if (chatInputs.length > 0) {
      chatInputs.forEach(input => {
        input.addEventListener('focus', handleChatFocus);
        input.addEventListener('blur', handleChatBlur);
      });
      if (chatCheckInterval) {
        clearInterval(chatCheckInterval);
        chatCheckInterval = null;
      }
    }
  }, 1000);
};

const handleLogoutHover = () => {
  if (isVisible.value && !isPerformingGesture.value) {
    PetSpeech.speak({ behavior: 'logout_hover', ttlMs: 3000, priority: 1 });
    isPerformingGesture.value = true;
    playRandomAnimation(contextAnimations.sadness);
    setTimeout(() => {
      isPerformingGesture.value = false;
      if (isWalking.value) {
        playRandomAnimation(contextAnimations.walking);
      } else {
        playRandomAnimation(contextAnimations.idle);
      }
    }, 3500);
  }
};

const handleChatFocus = () => {
  if (isVisible.value && !isPerformingGesture.value) {
    PetSpeech.speak({ behavior: 'hover', vars: { target: 'el chat' }, ttlMs: 2200, priority: 0 });
    isPerformingGesture.value = true;
    playRandomAnimation(contextAnimations.chatting);
  }
};

const handleChatBlur = () => {
  if (isVisible.value) {
    isPerformingGesture.value = false;
    if (isWalking.value) {
      playRandomAnimation(contextAnimations.walking);
    } else {
      playRandomAnimation(contextAnimations.idle);
    }
  }
};

// Animaciones contextuales por ruta
const currentPage = computed(() => route.name);

// Ejecutar animaciones según la página actual
const executePageAnimation = () => {
  if (!isVisible.value || isPerformingGesture.value) return;
  
  isPerformingGesture.value = true;
  
  switch (currentPage.value) {
    case 'history':
      playRandomAnimation(contextAnimations.pushup);
      setTimeout(() => {
        isPerformingGesture.value = false;
        if (isWalking.value) {
          playRandomAnimation(contextAnimations.walking);
        } else {
          playRandomAnimation(contextAnimations.idle);
        }
      }, 4500);
      break;
    case 'challenges':
      playRandomAnimation(contextAnimations.battle);
      setTimeout(() => {
        isPerformingGesture.value = false;
        if (isWalking.value) {
          playRandomAnimation(contextAnimations.walking);
        } else {
          playRandomAnimation(contextAnimations.idle);
        }
      }, 3500);
      break;
  }
};

// Ejecutar animación cuando cambia de página
const pageAnimationInterval = setInterval(() => {
  if (Math.random() > 0.85) {
    executePageAnimation();
  }
}, 15000);

onUnmounted(() => {
  clearInterval(pageAnimationInterval);
});

const toggleVisibility = () => {
  isVisible.value = !isVisible.value;
  PetSpeech.setPetVisible(isVisible.value);
  if (isVisible.value) {
    PetSpeech.speak({ behavior: 'pet_shown', ttlMs: 1600, priority: 1 });
  }
};

const startIdleTalk = () => {
  idleTalkInterval = window.setInterval(() => {
    if (!isVisible.value) return;
    if (PetSpeech.isOpen.value) return;
    if (isPerformingGesture.value) return;

    // Hablar con mayor frecuencia para dar más vida
    if (Math.random() > 0.65) {
      PetSpeech.speak({ behavior: 'idle', ttlMs: 3200, priority: 0 });
    }
  }, 18000); // Cada 18 segundos en lugar de 25
};

// Sync pet animation with speech bubble ("talking" state)
watch(
  () => PetSpeech.isOpen.value,
  (open) => {
    if (!isVisible.value) return;

    if (open) {
      isTalking.value = true;
      // Stop walking while speaking to avoid odd motion + bubble tracking.
      isWalking.value = false;
      if (!isPerformingGesture.value) {
        playRandomAnimation(contextAnimations.chatting);
      }
    } else {
      isTalking.value = false;
      // Siempre retornar a animación idle al terminar de hablar
      if (!isPerformingGesture.value) {
        playRandomAnimation(contextAnimations.idle);
      }
      // Resume walking after a short delay.
      setTimeout(() => {
        if (!isVisible.value) return;
        if (PetSpeech.isOpen.value) return;
        if (!isWalking.value && !isPerformingGesture.value) {
          chooseRandomTarget();
        }
      }, 1200);
    }
  },
  { immediate: true }
);

// Mantener animación idle activa
let idleMaintenanceInterval: number | null = null;
idleMaintenanceInterval = window.setInterval(() => {
  if (!isVisible.value) return;
  if (isPerformingGesture.value) return;
  if (isWalking.value) return;
  if (PetSpeech.isOpen.value) return;
  
  // Reforzar animación idle cada cierto tiempo
  playRandomAnimation(contextAnimations.idle);
}, 8000);

onUnmounted(() => {
  if (idleMaintenanceInterval) clearInterval(idleMaintenanceInterval);
});

const petStyle = computed(() => ({
  left: `${petPosition.value.x}px`,
  top: `${petPosition.value.y}px`,
  display: isVisible.value ? 'block' : 'none',
  opacity: petOpacity.value * (isHoveringPet.value ? PET_HOVER_DIM_OPACITY : 1)
}));
</script>

<template>
  <div class="pet-system">
    <button class="toggle-btn" data-tour-step="pet-toggle" @click="toggleVisibility">
      {{ isVisible ? '👁️ Ocultar' : '👁️ Mostrar' }} Mascota
    </button>

    <PetSpeechBubble :anchor-el="petContainer" :is-pet-visible="isVisible" :dimmed="isHoveringPet" />

    <div 
      ref="petContainer"
      class="pet-container" 
      :style="petStyle"
    >
      <div v-if="loading" class="pet-loading">⏳</div>
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
.pet-system {
  position: fixed;
  z-index: 9998;
}

.toggle-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.85);
  color: #ff6b6b;
  border: 2px solid #ff6b6b;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
  transition: all 0.2s ease;
  z-index: 9999;
}

.toggle-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  transform: scale(1.05);
}

.pet-container {
  position: fixed;
  width: 340px;
  height: 340px;
  pointer-events: none;
  transition: left 0.05s linear, top 0.05s linear, opacity 0.5s ease;
  z-index: 9998;
}

canvas {
  width: 340px !important;
  height: 340px !important;
  display: block;
}

.pet-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.4rem;
}
</style>
