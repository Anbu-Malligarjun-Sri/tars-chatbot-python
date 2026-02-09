import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TarsSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  icon?: React.ReactNode;
  color?: 'amber' | 'blue' | 'green';
  minLabel?: string;
  maxLabel?: string;
}

const colorMap = {
  amber: {
    track: 'bg-tars-amber',
    glow: 'shadow-[0_0_10px_hsl(37,100%,50%,0.5)]',
    text: 'text-tars-amber',
  },
  blue: {
    track: 'bg-tars-blue',
    glow: 'shadow-[0_0_10px_hsl(200,80%,55%,0.5)]',
    text: 'text-tars-blue',
  },
  green: {
    track: 'bg-tars-green',
    glow: 'shadow-[0_0_10px_hsl(145,70%,45%,0.5)]',
    text: 'text-tars-green',
  },
};

export function TarsSlider({ label, value, onChange, icon, color = 'amber', minLabel, maxLabel }: TarsSliderProps) {
  const colors = colorMap[color];
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    onChange(newValue);
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Label and Value */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && <span className={cn("opacity-70", colors.text)}>{icon}</span>}
          <span className="font-terminal text-xs uppercase tracking-widest text-muted-foreground">
            {label}
          </span>
        </div>
        <motion.span 
          key={value}
          initial={{ scale: 1.2, opacity: 0.5 }}
          animate={{ scale: 1, opacity: 1 }}
          className={cn("font-terminal text-sm font-semibold tabular-nums", colors.text)}
        >
          {value}%
        </motion.span>
      </div>
      
      {/* Slider Track */}
      <div className="relative h-8 w-full">
        {/* Background Track */}
        <div className="absolute inset-0 rounded bg-tars-dark border border-border overflow-hidden">
          {/* Grid Lines */}
          <div className="absolute inset-0 flex">
            {[...Array(10)].map((_, i) => (
              <div 
                key={i} 
                className="flex-1 border-r border-border/30 last:border-r-0"
              />
            ))}
          </div>
          
          {/* Fill */}
          <motion.div 
            className={cn("absolute left-0 top-0 h-full", colors.track)}
            initial={false}
            animate={{ 
              width: `${value}%`,
              opacity: 0.8 
            }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            style={{
              boxShadow: value > 10 ? `inset 0 0 20px rgba(255,157,0,0.3)` : 'none'
            }}
          />
        </div>
        
        {/* Thumb */}
        <motion.div 
          className={cn(
            "absolute top-0 h-full w-1 -translate-x-1/2",
            colors.track,
            colors.glow
          )}
          initial={false}
          animate={{ left: `${value}%` }}
          transition={{ type: "spring", stiffness: 400, damping: 35 }}
        />
        
        {/* Actual Input */}
        <input
          type="range"
          min={0}
          max={100}
          value={value}
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>
      
      {/* Scale Markers / Custom Labels */}
      <div className="flex justify-between px-0.5">
        {minLabel && maxLabel ? (
          <>
            <span className="font-terminal text-[9px] text-muted-foreground/50 uppercase">{minLabel}</span>
            <span className="font-terminal text-[9px] text-muted-foreground/50 uppercase">{maxLabel}</span>
          </>
        ) : (
          ['0', '25', '50', '75', '100'].map((mark) => (
            <span 
              key={mark} 
              className="font-terminal text-[10px] text-muted-foreground/50"
            >
              {mark}
            </span>
          ))
        )}
      </div>
    </div>
  );
}
