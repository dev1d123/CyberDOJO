import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const modelsPath = join(__dirname, '../src/assets/models');
const outputPath = join(__dirname, '../src/data/animations.json');

const modelFiles = [
  'barbarian.glb',
  'knight.glb',
  'mage.glb',
  'ranger.glb',
  'rogue.glb'
];

function parseGLB(buffer) {
  // GLB binary format parsing
  const headerView = new DataView(buffer, 0, 12);
  const magic = headerView.getUint32(0, true);
  const version = headerView.getUint32(4, true);
  const length = headerView.getUint32(8, true);

  if (magic !== 0x46546C67) { // 'glTF' in ASCII
    throw new Error('Invalid GLB file');
  }

  // Read JSON chunk
  const chunkView = new DataView(buffer, 12, 8);
  const chunkLength = chunkView.getUint32(0, true);
  const chunkType = chunkView.getUint32(4, true);

  if (chunkType !== 0x4E4F534A) { // 'JSON' in ASCII
    throw new Error('First chunk is not JSON');
  }

  const jsonBytes = new Uint8Array(buffer, 20, chunkLength);
  const jsonString = new TextDecoder().decode(jsonBytes);
  const gltf = JSON.parse(jsonString);

  return gltf;
}

function extractAnimations() {
  const animationsData = {};

  for (const modelFile of modelFiles) {
    const modelPath = join(modelsPath, modelFile);
    const modelName = modelFile.replace('.glb', '');
    
    try {
      // Read the GLB file
      const data = readFileSync(modelPath);
      const arrayBuffer = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
      
      // Parse the GLB
      const gltf = parseGLB(arrayBuffer);

      // Extract animation names
      const animations = gltf.animations || [];
      const animationNames = animations.map(anim => anim.name || `Animation_${animations.indexOf(anim)}`);
      
      animationsData[modelName] = {
        model: modelFile,
        animationCount: animations.length,
        animations: animationNames
      };

      console.log(`✓ ${modelName}: ${animations.length} animations found`);
      animationNames.forEach(name => console.log(`  - ${name}`));
      
    } catch (error) {
      console.error(`✗ Error processing ${modelFile}:`, error.message);
      animationsData[modelName] = {
        model: modelFile,
        error: error.message
      };
    }
  }

  // Write to JSON file
  writeFileSync(outputPath, JSON.stringify(animationsData, null, 2), 'utf-8');
  console.log(`\n✓ Animation data saved to ${outputPath}`);
}

extractAnimations();
