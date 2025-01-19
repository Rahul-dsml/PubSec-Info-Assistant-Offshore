import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, X } from 'lucide-react'
import { Button } from "@/components/ui/button"
import MapContainer from './MapContainer'
import useAppStore from '@/state/zustand'

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

const dummyLatData=[{'project_id': 15, 'Project URL': 'https://sakani.sa/app/offplan-projects/15', 'project_name_eng': 'Abha - Ali Shar - Abha Hills', 'project_latitude': 18.286109, 'project_longitude': 42.513347}]


const RecommenderComponent = () => {
const {showRecommendation,setShowRecommendation,latLongDetails} = useAppStore()  

  return (
    <motion.div
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 20 }}
      className='h-screen w-[60vw] rounded-3xl rounded-r-none bg-slate-600 shadow-xl overflow-hidden flex flex-col'
    >
      <div className="p-2">
       <span className='flex items-center cursor-pointer' onClick={()=>{setShowRecommendation(!showRecommendation)}}>
          <X className=" ml-2  h-8 w-8 hover:translate-x-[-3px] transition-all ease-in hover:text-cyan-400" /> 
       
          </span>
      </div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex-grow overflow-auto"
      >
        <div className="p-2">
          <MapContainer locations={dummyLatData} />
        </div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="p-4  rounded-t-3xl mt-2"
        >
        
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

export default RecommenderComponent

