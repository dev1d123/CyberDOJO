import { AudioService } from '../services/audio.service';

export function useAudio() {
  const playClick = () => AudioService.playClick();
  const playSend = () => AudioService.playSend();
  const playReceive = () => AudioService.playReceive();
  const playDialog = () => AudioService.playDialog();
  const toggleMute = () => AudioService.toggleMute();
  const reloadTheme = () => AudioService.reloadTheme();

  return {
    playClick,
    playSend,
    playReceive,
    playDialog,
    toggleMute,
    reloadTheme,
  };
}
