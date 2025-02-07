import { chatService } from "@/api/chat";
import BackgroundIcons from "@/components/BackgroundIcons";
import ChatContainer from "@/components/ChatContainer";

import HeroSection from "@/components/HeroSection";
import LanguageSelector from "@/components/LanguageSelector";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import useAppStore from "@/state/zustand";
import { motion } from "framer-motion";
import StreamingAvatar from "../streamingAvatarComponent/StreamingAvatar";
import { Mic } from "lucide-react";
import {
  Map,
  MapPinned,
  MessageSquareDiff,
  SendHorizontal,
} from "lucide-react";

import { useEffect, useState } from "react";

import RecommenderComponent from "@/components/RecommenderComponent";
import { useTranslation } from "react-i18next";
import i18n from "@/i18n";
import CardsContainer from "@/components/CardsContainer";
import StreamingAvatarWrapper from "./AvatarPage";
import useStreamingAvatar from "../streamingAvatarComponent/use-streaming-avatar";
import { useSpeechRecognition } from "../components/useSpeechRecognition";

export default function App() {
  const { t } = useTranslation();

  const {
    stream,
    handleCreateNewSession,
    handleStart,
    handleCloseConnection,
    isConnectionOpen,
    handleRepeat,
    isStarted,
    isLoading,
    setSessionOptions,
    session,
    sessionOptions,
  } = useStreamingAvatar();

  // States for the page
  const [pageloading, setPageLoading] = useState(false);
  const [language, setLanguage] = useState(t("language"));
  const [chatLoading, setLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [isChat, setIsChat] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([
    { text: t("introMessage"), isUser: false, isLoading: false },
  ]);
  const [convHistory, setConvHistory] = useState([
    {
      role: "assistant",
      content: { SQL_QUERY: "No", Response: t("introMessage") },
    },
  ]);
  const {
    showRecommendation,
    setShowRecommendation,
    latLongDetails,
    setLatLongDetails,
    showRecommendationCards,
    setShowRecommendationCards,
  } = useAppStore();

  const startConversation = async () => {
    setPageLoading(true);
    await handleCreateNewSession();
    await handleStart();
    setPageLoading(false);
  };

  const restartSession = async () => {
    await handleCloseConnection(); // Close existing session first
    await handleCreateNewSession();
    await handleStart();
  };

  // Use effect for changing the text language whenever there is change in the language
  useEffect(() => {
    const handleLanguageChange = () => {
      setMessages([
        { text: t("introMessage"), isUser: false, isLoading: false },
      ]);
      setConvHistory([
        {
          role: "assistant",
          content: { SQL_QUERY: "No", Response: t("introMessage") },
        },
      ]);
      setSessionOptions({
        quality: "high",
        avatar_name: "Selina-blackabaya-20220608",
        voice: {
          voice_id: t("avatarVoice.voice_id"),
          language: t("avatarVoice.language"),
        },
      });

      setLanguage(t("language"));
      setSpeechLang(t("code"));
    };
    // listenere function to change the lnaguae of the page on every change in the language
    i18n.on("languageChanged", handleLanguageChange);

    // const startConversation = async ()=>{
    //  await handleCreateNewSession()
    //  await handleStart()
    // }
    // setTimeout(() => {
    //   startConversation()
    // }, 5000);
    if(isConnectionOpen){
      handleStart()
    }

    // To clean up on umount htat is
    return () => {
      i18n.off("languageChanged", handleLanguageChange);
      // handleCloseConnection()
    };
  }, [i18n, t]);

  const examples = t("examples", { returnObjects: true });

  const showAudioTranscript = (transcript) => {
    setInputValue(transcript);
  };

  // Handler funtion for the chat
  const handleSend = async (prompt) => {
    if (!prompt.trim()) return;
    setInputValue("");

    // if(!isConnectionOpen){
    //   await handleCreateNewSession()
    //   await handleStart()
    // }

    // if(!isConnectionOpen){
    //   await startConversation()
    // }
    //   if (!isConnectionOpen) {
    //     console.warn("Session lost! Restarting...");
    //     await restartSession();
    // }

    setLoading(true);
    // toggle the chat to true so that chatContaienr could come in place of heroSection
    if (!isChat) {
      setIsChat(true);
    }
    // to remove the recommendation cards when the user sends a new message if they are already showing there
    // if (showRecommendationCards) {
    //   setShowRecommendationCards(false);
    // }

    // Add user message
    setMessages((prev) => [
      ...prev,
      { text: prompt, isUser: true, isLoading: false },
    ]);
    setConvHistory((prev) => [
      ...prev,
      { role: "user", content: { SQL_QUERY: "No", Response: prompt } },
    ]);
    const tempMessage = { text: "", isUser: false, isLoading: true };
    setMessages((prev) => [...prev, tempMessage]);
    // backend response from the api
    try {
      const data = await chatService(prompt, convHistory, language);
      setLoading(false);
      await handleRepeat(data.Response);
      console.log(data);

      //  state updateer to update the state to include current response from the api at the last index
      setMessages((prev) => {
        const updatedMessages = [...prev];
        updatedMessages[updatedMessages.length - 1] = {
          text: data.Response,
          isUser: false,
          isLoading: false,
        };
        return updatedMessages;
      });
      console.log(data.lat_long_details_list?.length);

      // Google Map section toggler that checks if there is any object in the latlongDetails then set the latLongDetails to it and set show recommendation to true that displays the google map section from the right side
      if (data.lat_long_details_list?.length > 0) {
        setLatLongDetails(data.lat_long_details_list);
        setShowRecommendationCards(true);
        setShowRecommendation(true);

        console.log(data.lat_long_details_list);
      }

      setConvHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content: { SQL_QUERY: data.SQL_QUERY, Response: data.Response },
        },
      ]);
    } catch (error) {
      console.log(error);
      console.log(error.message || "something went wrong");
      setInputValue("");
      if (error.response?.status === 400) {
        console.error("Bad Request detected. Reloading page...");

        // Optionally show an error message to the user
        alert("An error occurred (400 Bad Request). The page will reload.");

        // Reload the page
        window.location.reload();
      }
      // setMessages((prev) => {
      //   const updatedMessages = [...prev];
      //   updatedMessages[updatedMessages.length - 1] = {
      //     text: "Something went wrong please try again",
      //     isUser: false,
      //     isLoading: false,
      //   };
      //   return updatedMessages;
      // });
      setLoading(false);
    }

    console.log(convHistory);
  };

  const {
    isListening,
    transcripts,
    error,
    startListening,
    stopListening,
    reset,
    setSpeechLang,
  } = useSpeechRecognition(handleSend);

  const speakAvatar = async () => {
    if (isListening)
      // handleRepeat("مرحبًا! كيف حالك؟ أتمنى لك يومًا سعيدًا ومليئًا بالنجاح")
      start();
  };
  const StopAvatar = async () => {
    stop();
    setInputValue(speechResult);
  };

  const handleNewChat = () => {
    handleCloseConnection();
    setIsChat(false);
    setConvHistory([{ role: "assistant", content: t("introMessage") }]);
    setInputValue("");
    setMessages([{ text: t("introMessage"), isUser: false, isLoading: false }]);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-r from-slate-900 to-slate-700 flex text-white relative overflow-hidden">
      <BackgroundIcons />
      {/* Main Content */}
      {pageloading ? (
        <p>Loading...</p>
      ) : (
        <div
          className={`"container mx-auto ${
            isChat ? "py-4" : "py-20"
          }  px-4 relative z-10"`}
        >
          <div className={`chat-wrapper ${isChat ? "flex flex-col " : ""}`}>
            {isChat ? (
              <div className="h-[75vh] overflow-y-hidden rounded-xl max-w-3xl md:max-w-4xl w-full mx-auto">
                {/* <ChatContainer messages={messages} handleSend={handleSend} /> */}
                {/* <StreamingAvatarWrapper/> */}
                <div
                  className={`${
                    showRecommendation
                      ? "max-w-xl overflow-hidden remove-scrollbar "
                      : ""
                  } bottom-6 container`}
                >
                  {stream ? (
                    <StreamingAvatar stream={stream} />
                  ) : (
                    <p>No stream available. Please start a session.</p>
                  )}
                </div>
              </div>
            ) : (
              <>
                <HeroSection />
                {/* <StreamingAvatarWrapper/> */}
              </>
            )}
          </div>
          {/* {showRecommendationCards && <div className=" mx-auto relative flex justify-center max-w-3xl md:max-w-4xl"> <CardsContainer/></div>} */}
          {/* {latLongDetails?.length > 1 && showRecommendationCards && (
          <div className="mx-auto relative flex justify-center max-w-3xl md:max-w-4xl">
            <CardsContainer handleSend={handleSend} />{" "}
          </div>
        )} */}
          <div className="max-w-3xl  md:max-w-4xl w-full mx-auto sticky">
            {/* Glowing Background Effect */}
            <motion.div
              className=" backgroundGradientOVerlay  absolute -inset-3 bg-cyan-500/15 rounded-xl blur-2xl"
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

            <div className="relative max-w-3xl md:max-w-4xl border-slate-500 border min-h-[120px] bg-gray-900/90 rounded-3xl transition-all ease-in py-1 focus-within:border-2 focus-within:border-cyan-400">
              { isConnectionOpen && isStarted ? (
                <Textarea
                  value={chatLoading ? "Loading......." : inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="w-full textarea h-20 border-none bg-transparent text-white placeholder:text-gray-400 text-lg p-6 rounded-3xl relative z-10 backdrop-blur-sm resize-none"
                  placeholder={t("textArea.placeholder")}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend(inputValue);
                    }
                  }}
                />
              ) : (
                <div className="relative max-w-3xl flex gap-4  justify-center items-center mx-auto  min-h-[120px] rounded-3xl transition-all ease-in py-1 ">
                  <Button
                    variant="outline"
                    className={`${
                      isConnectionOpen ? "bg-cyan-400" : "bg-gray-300"
                    } h-16 w-72 text-xl  text-black `}
                    onClick={handleCreateNewSession}
                    disabled={isConnectionOpen || isLoading}
                  >
                  {t("establishConnection")}
                  </Button>
                  <Button
                    variant="outline"
                    className={`${
                      isStarted ? "bg-cyan-400" : "bg-gray-300"
                    } h-16 w-72 text-xl   text-black `}
                    onClick={handleStart}
                    disabled={!isConnectionOpen || isStarted || isLoading}
                  >
                    {t("startConversation")}
                  </Button>
                  {/* <Button onClick={handleCloseConnection} disabled={!isConnectionOpen} >close</Button> */}
                </div>
              )}
              <div className="sendButton flex justify-end gap-4 transition-all ease-in  items-center p-1 mr-1">
                {isChat && (
                  <>
                    <Button
                      onClick={handleNewChat}
                      className="bg-slate-700 hover:border transition ease-in rounded-full flex items-center"
                    >
                      <MessageSquareDiff
                        className="h-12 w-12"
                        absoluteStrokeWidth
                      />{" "}
                      <span>{t("textArea.newChatBtn")}</span>
                    </Button>
                    <Button
                      onClick={() => setShowRecommendation(true)}
                      className="bg-slate-700 hover:border transition ease-in rounded-full flex items-center"
                    >
                      {" "}
                      <MapPinned /> <span>{t("textArea.mapBtn")}</span>{" "}
                    </Button>
                  </>
                )}
                <LanguageSelector
                  language={language}
                  setLanguage={setLanguage}
                />
                <Button
                  variant="outline"
                  onClick={() => handleSend(inputValue)}
                  disabled={!isChat && !isStarted}
                  className="text-slate-800  rounded-full  bg-white transition-all ease-in hover:bg-slate-800 hover:text-white"
                >
                  <SendHorizontal
                    className="h-16 w-16"
                    strokeWidth={2.5}
                    absoluteStrokeWidth
                    disabled={chatLoading}
                  />
                  <span className="font-semibold">{t("textArea.sendBtn")}</span>
                </Button>
                {!isListening ? (
                  <Button
                    size="icon"
                    variant="secondary"
                    className={` rounded-full`}
                    onClick={startListening}
                    disabled={!isChat && !isStarted}
                  >
                    <Mic className="h-8 w-8 font-bold" />
                  </Button>
                ) : (
                  <Button
                    size="icon"
                    variant="secondary"
                    className="bg-red-500 hover:bg-red-500 animate-pulse transition-all ease-in rounded-full"
                    onClick={stopListening}
                  >
                    {" "}
                    <Mic className=" text-white" />
                  </Button>
                )}
              </div>
            </div>
          </div>
          {/* Example Buttons */}
    
        </div>
      )}

      <div>
        {showRecommendation && (
          <RecommenderComponent handleRepeat={handleRepeat} />
        )}
      </div>
    </div>
  );
}
