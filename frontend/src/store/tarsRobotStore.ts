import { create } from 'zustand';

export type TarsRobotState = 'idle' | 'thinking' | 'speaking' | 'happy' | 'annoyed' | 'sarcastic';

interface TarsRobotStore {
  // Mood state
  irritationLevel: number; // 0-100
  currentState: TarsRobotState;
  lastGesture: string | null;
  
  // LED color based on state
  ledColor: 'blue' | 'green' | 'red' | 'amber';
  
  // Actions
  poke: () => void;
  setGesture: (gesture: string) => void;
  clearGesture: () => void;
  syncWithChatStatus: (status: 'idle' | 'thinking' | 'speaking' | 'listening') => void;
  tick: () => void; // called every second to decay irritation
}

export const useTarsRobotStore = create<TarsRobotStore>((set, get) => ({
  irritationLevel: 0,
  currentState: 'idle',
  lastGesture: null,
  ledColor: 'blue',

  poke: () => {
    set((state) => {
      const newIrritation = Math.min(100, state.irritationLevel + 15);
      
      let newState: TarsRobotState = state.currentState;
      let newLedColor: 'blue' | 'green' | 'red' | 'amber' = state.ledColor;
      
      // Determine new state based on irritation
      if (newIrritation >= 71) {
        newState = 'sarcastic';
        newLedColor = 'red';
      } else if (newIrritation >= 41) {
        newState = 'annoyed';
        newLedColor = 'amber';
      } else {
        // Quick reaction then back to previous state
        newState = 'happy'; // Friendly reaction
        newLedColor = 'green';
      }
      
      return {
        irritationLevel: newIrritation,
        currentState: newState,
        ledColor: newLedColor,
      };
    });
  },

  setGesture: (gesture: string) => {
    const lowerGesture = gesture.toLowerCase();
    
    set((state) => {
      let newState: TarsRobotState = state.currentState;
      
      // Parse common gestures
      if (lowerGesture.includes('sigh') || lowerGesture.includes('scoff')) {
        newState = 'annoyed';
      } else if (lowerGesture.includes('cue light') || lowerGesture.includes('illuminate')) {
        newState = 'speaking';
      } else if (lowerGesture.includes('laugh') || lowerGesture.includes('chuckle')) {
        newState = 'happy';
      } else if (lowerGesture.includes('think') || lowerGesture.includes('process')) {
        newState = 'thinking';
      }
      
      return {
        lastGesture: gesture,
        currentState: newState,
      };
    });
    
    // Clear gesture after 3 seconds
    setTimeout(() => get().clearGesture(), 3000);
  },

  clearGesture: () => {
    set({ lastGesture: null });
  },

  syncWithChatStatus: (status) => {
    set((state) => {
      // Don't override if annoyed/sarcastic from poking
      if (state.irritationLevel >= 41) return state;
      
      let newState: TarsRobotState = 'idle';
      let newLedColor: 'blue' | 'green' | 'red' | 'amber' = 'blue';
      
      switch (status) {
        case 'thinking':
          newState = 'thinking';
          newLedColor = 'amber';
          break;
        case 'speaking':
          newState = 'speaking';
          newLedColor = 'green';
          break;
        case 'listening':
          newState = 'idle';
          newLedColor = 'amber';
          break;
        default:
          newState = 'idle';
          newLedColor = 'blue';
      }
      
      return { currentState: newState, ledColor: newLedColor };
    });
  },

  tick: () => {
    set((state) => {
      if (state.irritationLevel <= 0) return state;
      
      const newIrritation = Math.max(0, state.irritationLevel - 2); // Decay by 2 per second
      
      // Reset state if calmed down
      let newState = state.currentState;
      let newLedColor = state.ledColor;
      
      if (newIrritation < 41 && state.irritationLevel >= 41) {
        newState = 'idle';
        newLedColor = 'blue';
      } else if (newIrritation < 71 && state.irritationLevel >= 71) {
        newState = 'annoyed';
        newLedColor = 'amber';
      }
      
      return {
        irritationLevel: newIrritation,
        currentState: newState,
        ledColor: newLedColor,
      };
    });
  },
}));
