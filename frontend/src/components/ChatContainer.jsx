import { motion, AnimatePresence } from "framer-motion";
import ChatMessage from "./ChatMessage";
import { useEffect, useRef } from "react";
import RecommenderComponent from "./RecommenderComponent";
import CardsContainer from "./CardsContainer";
import useAppStore from "@/state/zustand";

export default function ChatContainer({ messages,handleSend }) {
  const scrollRef = useRef(null);
  const {latLongDetails,showRecommendationCards} = useAppStore()
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
        {/* {latLongDetails?.length>1 && showRecommendationCards && <CardsContainer handleSend={handleSend} />} */}
      </AnimatePresence>
    </motion.div>
  );
} 
