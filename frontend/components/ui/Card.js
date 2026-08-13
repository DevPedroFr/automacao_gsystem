export default function Card({ children, className = '', padding = 'p-6' }) {
  return (
    <div className={`bg-card backdrop-blur-md rounded-2xl shadow-lg border border-cardBorder hover:border-cyan-500/30 transition-all duration-300 ${padding} ${className}`}>
      {children}
    </div>
  );
}
