export default function Card({ children, className = '', padding = 'p-6' }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200 ${padding} ${className}`}>
      {children}
    </div>
  );
}
