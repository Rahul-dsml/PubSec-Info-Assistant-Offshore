import { motion, AnimatePresence } from "framer-motion";
import ChatMessage from "./ChatMessage";
import { useEffect, useRef } from "react";

export default function ChatContainer({ messages }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="chatContainer h-full overflow-y-auto p-4 "
      ref={scrollRef}
    >
      <AnimatePresence>
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg.text} isUser={msg.isUser} isLoading={msg.isLoading} />
        ))}
      </AnimatePresence>
    </motion.div>
  );
} 
