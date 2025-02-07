import { motion } from "framer-motion";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import user from "@/assets/user.png";
import bot from "@/assets/bot.png";
import ReactMarkdown from "react-markdown";
import useAppStore from "@/state/zustand";
import CardsContainer from "./CardsContainer";
// import remarkGfm from "remark-gfm"; // For GitHub-style markdown like tables, checkboxes, etc.

export default function ChatMessage({ message, isUser, isLoading }) {
  // const {latLongDetails} = useAppStore()
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
        <>
        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2 }}
          className={`max-w-[80%] text-start rounded-2xl p-4 ${
            isUser
              ? "bg-cyan-600 text-white"
              : "bg-slate-700/50 backdrop-blur-xl text-white"
          }`}
        >
          <ReactMarkdown
            children={message}
            // remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold">{children}</h1>,
              h2: ({ children }) => <h2 className="text-xl font-semibold">{children}</h2>,
              h3: ({ children }) => <h3 className="text-lg font-medium">{children}</h3>,
              p: ({ children }) => <p className="mb-2">{children}</p>,
              strong: ({ children }) => <strong className="font-bold">{children}</strong>,
              ul: ({ children }) => <ul className="list-disc pl-5">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pl-5">{children}</ol>,
              li: ({ children }) => <li className="mb-1">{children}</li>,
            }}
          />
        {/* {latLongDetails?.length>1 && <CardsContainer/>} */}
          

        </motion.div>
        </>
      )}
    </motion.div>
  );
}
