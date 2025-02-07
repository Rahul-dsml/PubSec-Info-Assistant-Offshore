import { useEffect, useRef, useState, useCallback } from "react";


export const  useSpeechRecognition = (onFinalTranscript, initialLang = "en-US") => {
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [transcripts, setTranscripts] = useState([]);
  const [error, setError] = useState(null);
  const [speechLang, setSpeechLang] = useState(initialLang);

  useEffect(() => {
    if (typeof window !== "undefined" && "webkitSpeechRecognition" in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = speechLang;
    } else {
      console.error("Speech recognition is not supported in this browser.");
      setError("Speech recognition is not supported in this browser.");
    }
  }, [speechLang]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;

    let accumulatedTranscript = "";

    recognitionRef.current.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      if (result.isFinal) {
        const newTranscript = result[0]?.transcript.trim();
        accumulatedTranscript += newTranscript + " ";
        setTranscripts((prev) => [...prev, newTranscript]);
        console.log("Partial transcript:", accumulatedTranscript);
      }
    };

    recognitionRef.current.onend = () => {
      if (accumulatedTranscript) {
        console.log("Final transcript:", accumulatedTranscript);
        onFinalTranscript(accumulatedTranscript); // Pass the final transcript to the parent component
        accumulatedTranscript = "";
      } else {
        console.warn("No valid input detected.");
        
      }
      setIsListening(false);
    };

    recognitionRef.current.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setError(event.error);
      setIsListening(false);
    };

    recognitionRef.current.start();
    setIsListening(true);
  }, [onFinalTranscript]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsListening(false);
    setTranscripts([]);
    setError(null);
  }, []);

  return {
    isListening,
    transcripts,
    error,
    startListening,
    stopListening,
    reset,
    setSpeechLang, // Expose this to allow language changing
  };
};
