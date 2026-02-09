import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { type TarsStatus } from '@/store/tarsStore';

interface CueLightProps {
  status: TarsStatus;
  className?: string;
}

const statusConfig = {
  idle: {
    color: 'bg-tars-gray',
    glow: false,
    pulse: false,
    label: 'STANDBY',
  },
  listening: {
    color: 'bg-tars-blue',
    glow: true,
    pulse: true,
    label: 'LISTENING',
  },
  thinking: {
    color: 'bg-tars-amber',
    glow: true,
    pulse: true,
    label: 'PROCESSING',
  },
  speaking: {
    color: 'bg-tars-green',
    glow: true,
    pulse: false,
    label: 'TRANSMITTING',
  },
};

export function CueLight({ status, className }: CueLightProps) {
  const config = statusConfig[status];
  
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {/* Light indicator */}
      <div className="relative">
        {/* Outer ring */}
        <div className="w-4 h-4 rounded-full border border-border bg-tars-dark flex items-center justify-center">
          {/* Inner light */}
          <motion.div
            className={cn(
              "w-2 h-2 rounded-full",
              config.color
            )}
            animate={config.pulse ? {
              scale: [1, 1.2, 1],
              opacity: [0.7, 1, 0.7],
            } : {
              scale: 1,
              opacity: config.glow ? 1 : 0.4,
            }}
            transition={config.pulse ? {
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            } : {
              duration: 0.3,
            }}
            style={config.glow ? {
              boxShadow: `0 0 8px currentColor, 0 0 16px currentColor`,
            } : {}}
          />
        </div>
        
        {/* Glow effect */}
        {config.glow && (
          <motion.div
            className={cn(
              "absolute inset-0 rounded-full",
              config.color
            )}
            animate={{
              scale: [1, 1.5],
              opacity: [0.4, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeOut",
            }}
          />
        )}
      </div>
      
      {/* Status label */}
      <span className="font-terminal text-[10px] uppercase tracking-[0.2em] text-muted-foreground">
        {config.label}
      </span>
    </div>
  );
}
