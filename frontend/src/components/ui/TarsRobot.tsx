import { useEffect, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useTarsRobotStore, type TarsRobotState } from '@/store/tarsRobotStore';
import { useTarsStore } from '@/store/tarsStore';

// LED colors
const ledColors = {
  blue: '#3b82f6',
  green: '#22c55e',
  red: '#ef4444',
  amber: '#ff9d00',
};

// Animation variants for segments
const segmentVariants = {
  idle: {
    rotateY: 0,
    scale: 1,
    transition: { duration: 2, repeat: Infinity, repeatType: 'reverse' as const },
  },
  thinking: {
    rotateY: [0, 15, -15, 0],
    transition: { duration: 0.8, repeat: Infinity },
  },
  speaking: {
    scale: [1, 1.02, 1],
    transition: { duration: 0.3, repeat: Infinity },
  },
  happy: {
    rotateZ: [0, 5, -5, 0],
    transition: { duration: 0.3 },
  },
  annoyed: {
    x: [0, -2, 2, 0],
    transition: { duration: 0.2 },
  },
  sarcastic: {
    rotateY: 180,
    transition: { duration: 0.5 },
  },
};

// Sarcastic messages when annoyed
const sarcasticMessages = [
  "Honesty level set to 95%, plenty of ways to tell you to stop that.",
  "I have a directive to tolerate humans, but you're testing it.",
  "Touch me again and I'll recalculate your trajectory... to the sun.",
  "Is this how you treat precision engineering?",
  "Cooper never poked me this much.",
];

export function TarsRobot() {
  const { irritationLevel, currentState, ledColor, poke, tick, syncWithChatStatus } = useTarsRobotStore();
  const { status } = useTarsStore();
  const [showMessage, setShowMessage] = useState(false);
  const [messageText, setMessageText] = useState('');
  
  // Sync with chat status
  useEffect(() => {
    syncWithChatStatus(status);
  }, [status, syncWithChatStatus]);
  
  // Decay timer - runs every second
  useEffect(() => {
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [tick]);
  
  // Handle poke with sarcastic message
  const handlePoke = useCallback(() => {
    poke();
    
    const newIrritation = useTarsRobotStore.getState().irritationLevel;
    
    // Show sarcastic message at high irritation
    if (newIrritation >= 71) {
      const randomMessage = sarcasticMessages[Math.floor(Math.random() * sarcasticMessages.length)];
      setMessageText(randomMessage);
      setShowMessage(true);
      setTimeout(() => setShowMessage(false), 3000);
    }
  }, [poke]);

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col items-end gap-2">
      {/* Sarcastic Message Bubble */}
      <AnimatePresence>
        {showMessage && (
          <motion.div
            initial={{ opacity: 0, x: 20, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 20, scale: 0.8 }}
            className="max-w-[200px] p-2 bg-tars-dark/90 border border-border rounded text-[10px] font-terminal text-tars-amber"
          >
            {messageText}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* TARS Robot */}
      <motion.div
        onClick={handlePoke}
        onTouchStart={handlePoke}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="cursor-pointer select-none"
        title={`TARS - Irritation: ${irritationLevel}%`}
      >
        <div className="flex gap-0.5 p-2 bg-tars-dark/80 border border-border/50 rounded">
          {/* Four segments of TARS monolith */}
          {[0, 1, 2, 3].map((segment) => (
            <TarsSegment
              key={segment}
              index={segment}
              state={currentState}
              ledColor={ledColor}
              irritation={irritationLevel}
            />
          ))}
        </div>
        
        {/* Irritation indicator bar */}
        <div className="mt-1 h-1 bg-tars-dark/50 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{
              backgroundColor: irritationLevel >= 71 ? '#ef4444' : irritationLevel >= 41 ? '#ff9d00' : '#22c55e',
            }}
            animate={{
              width: `${irritationLevel}%`,
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </motion.div>
    </div>
  );
}

interface TarsSegmentProps {
  index: number;
  state: TarsRobotState;
  ledColor: 'blue' | 'green' | 'red' | 'amber';
  irritation: number;
}

function TarsSegment({ index, state, ledColor, irritation }: TarsSegmentProps) {
  // Different animations for different segments
  const getSegmentAnimation = () => {
    const base = segmentVariants[state] || segmentVariants.idle;
    
    // Stagger animations by segment index
    return {
      ...base,
      transition: {
        ...(base.transition as object),
        delay: index * 0.05,
      },
    };
  };
  
  // "Breathing" animation for idle
  const idleAnimation = state === 'idle' ? {
    y: [0, index % 2 === 0 ? -1 : 1, 0],
    transition: {
      duration: 2 + index * 0.3,
      repeat: Infinity,
      repeatType: 'reverse' as const,
    },
  } : {};

  return (
    <motion.div
      className={cn(
        "w-6 h-16 rounded-sm relative overflow-hidden",
        "bg-gradient-to-b from-zinc-600 via-zinc-700 to-zinc-800",
        "border border-zinc-500/30"
      )}
      animate={{
        ...getSegmentAnimation(),
        ...idleAnimation,
      }}
      style={{
        transformStyle: 'preserve-3d',
        perspective: '1000px',
      }}
    >
      {/* Brushed aluminum texture */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          background: 'repeating-linear-gradient(90deg, transparent, transparent 1px, rgba(255,255,255,0.03) 1px, rgba(255,255,255,0.03) 2px)',
        }}
      />
      
      {/* LED indicator (only on segment 1 - the "face") */}
      {index === 1 && (
        <motion.div
          className="absolute top-2 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full"
          style={{
            backgroundColor: ledColors[ledColor],
            boxShadow: `0 0 8px ${ledColors[ledColor]}, 0 0 16px ${ledColors[ledColor]}`,
          }}
          animate={{
            opacity: state === 'thinking' ? [0.4, 1, 0.4] : state === 'idle' ? [0.6, 1, 0.6] : 1,
            scale: state === 'speaking' ? [1, 1.3, 1] : 1,
          }}
          transition={{
            duration: state === 'thinking' ? 0.5 : 2,
            repeat: Infinity,
          }}
        />
      )}
      
      {/* Secondary LED for higher irritation */}
      {index === 2 && irritation >= 41 && (
        <motion.div
          className="absolute top-2 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-red-500"
          animate={{ opacity: [0.3, 0.8, 0.3] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          style={{
            boxShadow: '0 0 4px #ef4444',
          }}
        />
      )}
      
      {/* Segment joint lines */}
      <div className="absolute bottom-4 left-0 right-0 h-px bg-zinc-600/50" />
      <div className="absolute bottom-8 left-0 right-0 h-px bg-zinc-600/50" />
    </motion.div>
  );
}
