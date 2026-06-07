import { motion } from 'framer-motion';

interface ShinyTextProps {
  text: string;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
}

export default function ShinyText({ text, className = '', as: Tag = 'span' }: ShinyTextProps) {
  return (
    <Tag
      className={`inline-block bg-clip-text text-transparent bg-[length:200%_auto] animate-shine ${className}`}
      style={{
        backgroundImage:
          'linear-gradient(90deg, #60a5fa 0%, #67e8f9 25%, #ffffff 50%, #67e8f9 75%, #60a5fa 100%)',
      }}
    >
      {text}
    </Tag>
  );
}

export function AnimatedCounter({ value, duration = 2 }: { value: number; duration?: number }) {
  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.span
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {value.toLocaleString()}
      </motion.span>
    </motion.span>
  );
}
