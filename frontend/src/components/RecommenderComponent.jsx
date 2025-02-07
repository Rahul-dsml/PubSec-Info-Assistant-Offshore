import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import MapContainer from "./MapContainer";
import useAppStore from "@/state/zustand";
import CardsContainer from "./CardsContainer";
import ChatMessage from "./ChatMessage";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {useTranslation} from "react-i18next";
import ReportContainer from "./ReportContainer";

const locations = [
  {
    lat: 24.7136,
    lng: 46.6753,
    name: "Kingdom Tower",
    description: "Iconic skyscraper in Riyadh.",
  },
  {
    lat: 21.4858,
    lng: 39.1925,
    name: "Jeddah Corniche",
    description: "Beautiful seaside promenade in Jeddah.",
  },
  {
    lat: 24.7742,
    lng: 46.7386,
    name: "Riyadh Front",
    description: "Popular shopping and entertainment area in Riyadh.",
  },
];

const dummyLatData = [
  {
    project_id: 15,
    "Project URL": "https://sakani.sa/app/offplan-projects/15",
    project_name_eng: "Abha - Ali Shar - Abha Hills",
    project_latitude: 18.286109,
    project_longitude: 42.513347,
  },
];

const RecommenderComponent = ({ handleRepeat }) => {
  const {
    showRecommendation,
    setShowRecommendation,
    latLongDetails,
    showRecommendationCards,
    showReport,
    setShowReport,
    reportResults
  } = useAppStore();

const {t} = useTranslation()
 const showReportHandler = () => {
  setShowReport(!showReport);
 }


  return (
    <motion.div
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="h-screen w-[60vw] p-4  rounded-3xl border-cyan-400 border-2 overflow-y-scroll rounded-r-none bg-slate-600 shadow-xl  flex flex-col"
    >
      <div className="controlButtons mb-2  w-96 items-center flex gap-12">
      <span
        className="flex items-center   cursor-pointer w-fit"
        onClick={() => {
          setShowRecommendation(!showRecommendation);
        }}
      >
        <X className=" text-gray-300  h-8 w-8 hover:translate-x-[-3px] transition-all ease-in hover:text-cyan-400" />
      </span>
      <Button variant="outline"   className={` ${showReport?"bg-cyan-600 ":"bg-transparent order-1"}    hover:translate-x-1 transition-all ease-in`} onClick={showReportHandler} > {showReport?t("hideReport"):t("report")} </Button>
      </div>


        {showReport ? (
          <div className="container w-full ml-2  relative backdrop-blur-sm">
            {/* <ReactMarkdown
              children={reportResults}
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => <h1 className="text-3xl text-cyan-300 font-bold">{children}</h1>,
                h2: ({ children }) => <h2 className="text-xl text-cyan-300 font-semibold">{children}</h2>,
                h3: ({ children }) => <h3 className="text-lg text-cyan-300 font-medium">{children}</h3>,
                p: ({ children }) => <p className="mb-2">{children}</p>,
                strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                ul: ({ children }) => <ul className="list-disc pl-5">{children}</ul>,
                ol: ({ children }) => <ol className="list-disc pl-5">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                a: ({ children}) => <a target='_blank' className="text-cyan-600 hover:underline">{children}</a>
              }}
            >
              {reportResults.replace(/•/g, "-")}
            </ReactMarkdown> */}
            {/* Report Container  */}
            <ReportContainer data={reportResults} /> 
          </div>
      ) : (
        <>
          {/* Actual conditional logic for rendering */}
          {/* {latLongDetails?.length>1 && showRecommendationCards && <CardsContainer handleSend={handleSend} />} */}
          {showRecommendationCards && (
            <CardsContainer handleRepeat={handleRepeat}  />
          )}

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex-grow "
          >
            <div className="">
              <MapContainer locations={dummyLatData} />
            </div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="p-4  rounded-t-3xl mt-2"
            ></motion.div>
          </motion.div>
        </>
      )}
    </motion.div>
  );
};

export default RecommenderComponent;
