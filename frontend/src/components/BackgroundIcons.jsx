import { motion } from "framer-motion";
import { Building2, Home, Key, MapPin } from "lucide-react";

const icons = [
  { Icon: Building2, position: { top: "10%", left: "2%" } },
  { Icon: Home, position: { top: "30%", left: "12%" } },
  { Icon: Key, position: { bottom: "50%", right: "2%" } },
  { Icon: MapPin, position: { bottom: "30%", right: "12%" } },
];

export default function BackgroundIcons() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {icons.map(({ Icon, position }, index) => (
        <motion.div
          key={index}
          className="absolute text-cyan-500/30"
          style={{
            ...position,
            fontSize: "50px", // Consistent icon size
          }}
          animate={{
            y: [0, -20, 0], // Smooth vertical floating
          }}
          transition={{
            duration: 4, // Animation duration
            repeat: Infinity, // Loop infinitely
            repeatType: "reverse", // Reverse animation for smoothness
            ease: "easeInOut", // Smooth easing
          }}
        >
          <Icon size={64} />
        </motion.div>
      ))}
    </div>
  );
}
