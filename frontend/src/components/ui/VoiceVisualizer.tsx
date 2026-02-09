import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface VoiceVisualizerProps {
  isActive: boolean;
  className?: string;
}

export function VoiceVisualizer({ isActive, className }: VoiceVisualizerProps) {
  const bars = 12;
  
  return (
    <div className={cn("flex items-end justify-center gap-0.5 h-8", className)}>
      {[...Array(bars)].map((_, i) => {
        const delay = i * 0.05;
        const baseHeight = Math.sin((i / bars) * Math.PI) * 100;
        
        return (
          <motion.div
            key={i}
            className="w-1 bg-tars-amber rounded-full origin-bottom"
            animate={isActive ? {
              scaleY: [0.3, 0.8 + Math.random() * 0.2, 0.4, 1, 0.5],
            } : {
              scaleY: 0.2,
            }}
            transition={isActive ? {
              duration: 0.5,
              repeat: Infinity,
              delay,
              ease: "easeInOut",
            } : {
              duration: 0.3,
            }}
            style={{
              height: `${20 + baseHeight * 0.3}px`,
              opacity: isActive ? 1 : 0.3,
            }}
          />
        );
      })}
    </div>
  );
}
