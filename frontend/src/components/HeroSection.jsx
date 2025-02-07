import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion';
import ChatMessage from './ChatMessage';
import { useTranslation } from 'react-i18next';
import i18next from 'i18next';

const HeroSection = () => {

  const {t} = useTranslation()

  const currentLanguage = i18next.language;

  const phrases = [
    "Dream Property",
    "Ideal Home",
    "Perfect Investment",
    "Luxury Living",
  ];

  return (

    <motion.div
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 1, ease: "easeOut" }}
    className="text-center mt-24 mb-10"
  >
    {/* <h1 className='text-4xl font-extrabold text-white md:text-5xl'>Real Estate AI Assistant</h1> */}
    <h1 className={` ${currentLanguage==='ar'?"font-arabicHeading":"font-heading"} text-4xl font-bold text-white md:text-5xl `}>
       {t("hero.titlePart1")} {" "}
      <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent font-extrabold animate-pulse">{t("hero.titlePart2")}</span>{" "}
    
      {t("hero.titlePart3")}
     
    </h1>
    <p className={`${currentLanguage==='ar'?"font-arabicHeading":"font-heading"} mt-2 text-lg text-slate-300 md:text-xl`}>
    {t("hero.subtitle")}
    </p>
    {/* <div className=' flex justify-center mx-auto max-w-4xl mt-20'>
    <ChatMessage isUser={false} isLoading={false} message={'Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!'} />
    </div> */}
  </motion.div>

  )
}

export default HeroSection