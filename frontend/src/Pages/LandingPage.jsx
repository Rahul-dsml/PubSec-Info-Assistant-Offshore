import { chatService } from "@/api/chat";
import BackgroundIcons from "@/components/BackgroundIcons";
import ChatContainer from "@/components/ChatContainer";
import ChatInput from "@/components/ChatInput";
import HeroSection from "@/components/HeroSection";
import LanguageSelector from "@/components/LanguageSelector";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip } from "@/components/ui/tooltip";
import useAppStore from "@/state/zustand";
import { motion } from "framer-motion";
import { ArrowUpRight, MessageSquareDiff, Send, SendHorizontal, Turtle } from "lucide-react";
import { FiSend } from "react-icons/fi";

import { useState } from "react";

export default function App() {

 

  const [isFocused, setIsFocused] = useState(false);
  const [messages, setMessages] = useState([{text: "Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!", isUser: false, isLoading: false}]);
  const [isChat, setIsChat] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [convHistory,setConvHistory] = useState([{role: 'assistant', content:{SQL_QUERY:'No',Response:"Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!"}}])
  // [{"role":"assistent", "content": {"SQL_QUERY":"No","Response":insight}}, {"role":"user", "content": {"SQL_QUERY":"No","Response":user_input}} ]

  const [language,setLanguage] = useState('English')


  const examples = [
    {
      exampleText: "🏠 Nearby properties",
      prompt: "Please show me a list of properties available for sale or rent near my current location."
    },
    {
      exampleText: "💰 Budget homes",
      prompt: "Can you help me find homes that are within my specified budget range and preferred location?"
    },
    {
      exampleText: "🌟 Popular areas",
      prompt: "I'd like to explore popular neighborhoods in the city to consider for buying or renting a home."
    },
    {
      exampleText: "🏡 Luxury villas",
      prompt: "Show me a collection of luxury villas available for purchase or rent in high-end neighborhoods."
    },
    {
      exampleText: "🏢 Commercial spaces",
      prompt: "I’m looking for commercial spaces nearby that are suitable for offices or retail stores."
    },
    {
      exampleText: "🌊 Waterfront homes",
      prompt: "Can you provide options for waterfront properties available for sale or rent in my area?"
    }
  ];
  



  const handleSend = async () => {
    if (!inputValue.trim()) return;
   
    if (!isChat) {
      setIsChat(true);
    }
    // Add user message
    setMessages((prev) => [
      ...prev,
      { text: inputValue, isUser: true, isLoading: false },
    ]);
    setConvHistory((prev)=>[...prev,{role: 'user', content:{SQL_QUERY:"No",Response: inputValue} }])
    const tempMessage = { text: "", isUser: false, isLoading: true }
    setMessages((prev) => [
      ...prev,
      tempMessage,
    ]);
    // backend response from the api
    try {
     const data =   await chatService(inputValue,convHistory,language)
     console.log(data)
       setMessages((prev) => {
      const updatedMessages = [...prev];
      updatedMessages[updatedMessages.length - 1] = {
        // SQL_QUERY:data.SQL_QUERY,
        text: data.Response,
        isUser: false,
        isLoading: false,
      };
      return updatedMessages;
    });

    setConvHistory((prev)=>[...prev,{role: 'assistant', content:{SQL_QUERY:data.SQL_QUERY,Response: data.Response}}])

    } catch (error) {
      console.log(error.message || 'something went wrong')
    }

    setInputValue("");


    // Simulate bot response just for mocking
    // setTimeout(() => {
    //   const botResponse =
    //     "I'm your real estate assistant. I can help you find properties that match your criteria.";
    //   setMessages((prev) => {
    //     const updatedMessages = [...prev];
    //     updatedMessages[updatedMessages.length - 1] = {
    //       text: botResponse,
    //       isUser: false,
    //       isLoading: false,
    //     };
    //     return updatedMessages;
    //   });

    //   setConvHistory((prev) => [
    //     ...prev,
    //     { role: "assistant", content: botResponse },
    //   ]);
    // }, 5000);

    console.log(convHistory)
    console.log(language)
   
  };

  const handleNewChat = () =>{
    setIsChat(false)
    setConvHistory([{role: 'assistant', content:"Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!"}])
    setInputValue("")
    setMessages([{text: "Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!", isUser: false, isLoading: false}])
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-r from-slate-900 to-slate-700 text-white relative overflow-hidden">
      <BackgroundIcons />
      {/* Main Content */}
      <div className="container mx-auto  px-4 py-20 relative z-10">
      <div className={`chat-wrapper ${isChat ? "flex flex-col " : ""}`}>
    {isChat ? (
      <div className="h-[65vh] overflow-hidden rounded-xl max-w-3xl md:max-w-4xl w-full mx-auto">
      
        <ChatContainer messages={messages} />
      </div>
    ) : (
      <HeroSection />
    )}
  </div>

        {/* Chat Input */}
        {/* <ChatInput/> */}
        <div className="max-w-3xl md:max-w-4xl w-full mx-auto sticky">
          {/* Glowing Background Effect */}
          <motion.div
            className="absolute -inset-3 bg-cyan-500/15 rounded-xl blur-2xl"
            animate={{
              y: isChat ? "70vh" : 0,
              scale: isFocused ? 1.1 : 1,
              opacity: isFocused ? 0.8 : 0.5,
            }}
            transition={{
              duration: 0.3,
              ease: "easeInOut",
            }}
          />

          {/* Additional glow layers for more intensity */}
          <motion.div
            className="absolute -inset-3 bg-cyan-600/60 rounded-xl blur-3xl"
            animate={{
              scale: isFocused ? 1.15 : 1.05,
              opacity: isFocused ? 0.6 : 0.4,
            }}
            transition={{
              duration: 0.3,
              ease: "easeInOut",
            }}
          />

          <div className="relative border-slate-500 border min-h-[120px] bg-gray-900/90 rounded-3xl transition-all ease-in py-1 focus-within:border-2 focus-within:border-cyan-400">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="w-full h-20 border-none bg-transparent text-white placeholder:text-gray-400 text-lg p-6 rounded-3xl relative z-10 backdrop-blur-sm resize-none"
              placeholder="Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!"
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <div className="sendButton flex justify-end gap-2  items-center p-1 mr-1">
            {isChat&&<Button onClick={handleNewChat} className="bg-slate-700 rounded-full flex items-center" ><MessageSquareDiff className="h-12 w-12" absoluteStrokeWidth /> <span>New Chat</span></Button>}
              <LanguageSelector language={language} setLanguage={setLanguage} />
              <Button
              variant='outline'
              
                onClick={handleSend}
                className="text-slate-800  rounded-full  bg-white transition-all ease-in hover:bg-slate-800 hover:text-white"
              >
              
               <SendHorizontal className="h-16 w-16" strokeWidth={2.5} absoluteStrokeWidth />
              <span className="font-semibold">Send</span>
              </Button>

            </div>
          </div>
        </div>
        {/* Example Buttons */}
        {!isChat&&<div className="flex flex-wrap gap-2 justify-center max-w-3xl   mt-6  mx-auto ">
          <div className="suggestions flex flex-wrap gap-2 justify-center ">
            {examples.map((query,index) => (
              
              <Button
                key={index}
                onClick={()=>setInputValue(query.prompt)}
                className=" rounded-full bg-transparent text-slate-300 hover:bg-gray-900/50 transition-colors text-sm backdrop-blur-sm border border-slate-300"
              >
               <span>{query.exampleText}</span> 
               {/* <ArrowUpRight className="text-cyan-400"/> */}
              </Button>
             
            ))}
          </div>
        </div>}
        {/* Footer Text */}
        {/* <div className="text-center mt-20 text-gray-500">
          Loved by 30 million software creators, including teams at:
        </div> */}
      </div>
    </div>
  );
}
