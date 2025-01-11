import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion';

const HeroSection = () => {
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
    className="text-center mt-24 mb-12"
  >
    {/* <h1 className='text-4xl font-extrabold text-white md:text-5xl'>Real Estate AI Assistant</h1> */}
    <h1 className=" font-heading font text-4xl font-bold text-white md:text-5xl ">
      Find Your{" "}
      <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent font-extrabold animate-pulse">Dream Property</span>{" "}
     {/* <br /> */}
      with Ease!
    </h1>
    <p className="mt-4 text-lg text-slate-300 md:text-xl">
      Let our{" "} Real Estate
        AI Assistant
   
      guide you to your perfect space.
    </p>
  </motion.div>

  )
}

export default HeroSection