import { motion } from "framer-motion";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import user from "@/assets/user.png";
import bot from "@/assets/bot.png";

export default function ChatMessage({ message, isUser, isLoading }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 100 : -100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex gap-3 ${
        isUser ? "flex-row-reverse" : "flex-row"
      } items-start mb-4`}
    >
      <Avatar className="w-8 h-8 md:w-10 md:h-10 bg-cyan-400">
        <AvatarImage src={isUser ? user : bot} />
        <AvatarFallback className="bg-cyan-500">
          {isUser ? "U" : "B"}
        </AvatarFallback>
      </Avatar>

      {isLoading ? (
         <div className="space-y-2">
         <Skeleton className="h-4 w-56 rounded-full bg-white" />
         <Skeleton className="h-4 w-80 rounded-full bg-white" />
       </div>
      ) : (
        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2 }}
          className={`max-w-[80%] rounded-2xl p-4 ${
            isUser
              ? "bg-cyan-600 text-white"
              : "bg-slate-700/50 backdrop-blur-xl text-white"
          }`}
        >
          {message}
        </motion.div>
      )}
    </motion.div>
  );
}
