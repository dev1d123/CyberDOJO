<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import animationsData from '@/data/animations.json';
import { UserService } from '@/services/user.service';

const route = useRoute();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const petContainer = ref<HTMLDivElement | null>(null);
const isVisible = ref(true);
const loading = ref(false);
const petOpacity = ref(1);
const currentPetId = ref<number | null>(null);

let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let renderer: THREE.WebGLRenderer | null = null;
let mixer: THREE.AnimationMixer | null = null;
let clock: THREE.Clock | null = null;
let currentGLTF: any = null;
let animationFrame: number | null = null;
let currentModel: string = '';
let allAnimations: THREE.AnimationClip[] = [];
let model3D: THREE.Group | null = null;

// Posición base y área de movimiento
const basePosition = { x: window.innerWidth - 300, y: window.innerHeight - 300 };
const petPosition = ref({ x: basePosition.x, y: basePosition.y });
const targetPosition = ref({ x: basePosition.x, y: basePosition.y });
const isWalking = ref(false);
const movementRadius = 80; // Radio de movimiento desde la posición base
const isPerformingGesture = ref(false);

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

onMounted(async () => {
  await loadUserPet();
  startRandomGestures();
  startRandomWalking();
  setupClickListener();
  startPetChecker();
});

onUnmounted(() => {
  cleanup();
  removeClickListener();
  if (idleInterval) clearInterval(idleInterval);
  if (randomGestureInterval) clearInterval(randomGestureInterval);
  if (petCheckInterval) clearInterval(petCheckInterval);
});

const loadUserPet = async () => {
  try {
    const user = await UserService.getCurrentUser();
    if (user.pet_id) {
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
    }
  } catch (error) {
    console.error('Error cargando mascota:', error);
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
      if (user.pet_id && currentPetId.value !== null && currentPetId.value !== user.pet_id) {
        await transitionToPet(user.pet_id);
      }
    } catch (error) {
      // Ignorar errores silenciosamente
    }
  }, 3000);
};

const loadModel = async (modelName: string) => {
  if (!canvasRef.value) return;
  
  loading.value = true;
  currentModel = modelName;
  cleanup();

  // Configurar escena
  scene = new THREE.Scene();
  
  camera = new THREE.PerspectiveCamera(50, 250 / 250, 0.1, 1000);
  camera.position.set(0, 1.5, 3);

  renderer = new THREE.WebGLRenderer({ 
    canvas: canvasRef.value,
    antialias: true,
    alpha: true
  });
  renderer.setSize(250, 250);
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
    currentGLTF = gltf;
    
    model3D = gltf.scene;
    model3D.position.set(0, 0, 0);
    scene.add(model3D);

    if (gltf.animations && gltf.animations.length > 0) {
      clock = new THREE.Clock();
      mixer = new THREE.AnimationMixer(model3D);
      allAnimations = gltf.animations;
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

  mixer.stopAllAction();
  const clip = allAnimations.find(clip => clip.name === animationName);
  
  if (clip) {
    const action = mixer.clipAction(clip);
    action.reset();
    action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, loop ? Infinity : 1);
    action.clampWhenFinished = true;
    action.play();
  }
};

const playRandomAnimation = (animList: string[]) => {
  const randomAnim = animList[Math.floor(Math.random() * animList.length)];
  playAnimation(randomAnim);
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
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry.dispose();
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
    scene = null;
  }

  clock = null;
  currentGLTF = null;
  allAnimations = [];
  model3D = null;
};

const chooseRandomTarget = () => {
  if (!isVisible.value) return;
  
  // Elegir punto aleatorio dentro del radio de movimiento
  const angle = Math.random() * Math.PI * 2;
  const distance = Math.random() * movementRadius;
  
  let newX = basePosition.x + Math.cos(angle) * distance;
  let newY = basePosition.y + Math.sin(angle) * distance;
  
  // Asegurar que no se salga de los límites de la pantalla
  const margin = 50;
  newX = Math.max(margin, Math.min(window.innerWidth - 250 - margin, newX));
  newY = Math.max(margin, Math.min(window.innerHeight - 250 - margin, newY));
  
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
  
  // Calcular ángulo hacia el click
  const clickX = event.clientX;
  const clickY = event.clientY;
  
  const dx = clickX - (petPosition.value.x + 125); // 125 = mitad del canvas (250/2)
  const dy = clickY - (petPosition.value.y + 125);
  
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
    if (isVisible.value && Math.random() > 0.6 && !isPerformingGesture.value) {
      isPerformingGesture.value = true;
      const currentlyWalking = isWalking.value;
      
      playRandomAnimation(contextAnimations.random);
      
      // Tiempo muerto de 1 segundo después de la animación
      setTimeout(() => {
        isPerformingGesture.value = false;
        // Volver a caminar o idle según el estado
        if (currentlyWalking || isWalking.value) {
          playRandomAnimation(contextAnimations.walking);
        } else {
          playRandomAnimation(contextAnimations.idle);
        }
      }, 2500); // Duración de animación + 1 segundo de tiempo muerto
    }
  }, 5000); // Cada 5 segundos intenta hacer una animación
};

// Event listeners específicos por contexto (sin click en pantalla)
let logoutButton: HTMLElement | null = null;
let chatInputs: NodeListOf<HTMLInputElement> | null = null;

const setupEventListeners = () => {
  // Detectar hover en logout
  const checkLogout = setInterval(() => {
    logoutButton = document.querySelector('[data-logout-btn]') as HTMLElement;
    if (logoutButton) {
      logoutButton.addEventListener('mouseenter', handleLogoutHover);
      clearInterval(checkLogout);
    }
  }, 1000);
  
  // Detectar inputs de chat
  const checkChatInputs = setInterval(() => {
    chatInputs = document.querySelectorAll('input[type="text"], textarea');
    if (chatInputs.length > 0) {
      chatInputs.forEach(input => {
        input.addEventListener('focus', handleChatFocus);
        input.addEventListener('blur', handleChatBlur);
      });
      clearInterval(checkChatInputs);
    }
  }, 1000);
  
  setupEventListeners();
};

const removeEventListeners = () => {
  if (logoutButton) {
    logoutButton.removeEventListener('mouseenter', handleLogoutHover);
  }
  if (chatInputs) {
    chatInputs.forEach(input => {
      input.removeEventListener('focus', handleChatFocus);
      input.removeEventListener('blur', handleChatBlur);
    });
  }
};

const handleLogoutHover = () => {
  if (isVisible.value && !isPerformingGesture.value) {
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
};

const petStyle = computed(() => ({
  left: `${petPosition.value.x}px`,
  top: `${petPosition.value.y}px`,
  display: isVisible.value ? 'block' : 'none',
  opacity: petOpacity.value
}));
</script>

<template>
  <div class="pet-system">
    <button class="toggle-btn" @click="toggleVisibility">
      {{ isVisible ? '👁️ Ocultar' : '👁️ Mostrar' }} Mascota
    </button>

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
  font-size: 13px;
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
  width: 250px;
  height: 250px;
  pointer-events: none;
  transition: left 0.05s linear, top 0.05s linear, opacity 0.5s ease;
  z-index: 9998;
}

canvas {
  width: 250px !important;
  height: 250px !important;
  display: block;
}

.pet-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
}
</style>
