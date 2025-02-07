import React, { useEffect, useRef, useState } from "react";

import { Card, CardContent, CardFooter } from "@/components/ui/card"; // ShadCN Card components
import {
  AdvancedMarker,
  Marker,
  APIProvider,
  Map,
  InfoWindow,
  useAdvancedMarkerRef
} from "@vis.gl/react-google-maps";
import useAppStore from "@/state/zustand";
import { useTranslation } from "react-i18next";

let apiKey = import.meta.env.VITE_GOOGLEMAPS_API_KEY;

// Map container styles using Tailwind CSS
const mapContainerClassName = "w-full h-40  shadow-md";

// Default center for the map (Riyadh, Saudi Arabia)

// Custom map styles (use Snazzy Maps or similar for other styles)
const customMapStyle = [
  {
    featureType: "all",
    elementType: "geometry",
    stylers: [{ color: "#f2f2f2" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#c9e6f2" }],
  },
];

const MapContainer = () => {
  const {latLongDetails} = useAppStore()
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [directionsResponse, setDirectionsResponse] = useState(null);
  const [mapCenter, setMapCenter] = useState({ lat: 0, lng: 0 });
  const [mapZoom, setMapZoom] = useState(14);
  const [markerRef, marker] = useAdvancedMarkerRef();

  const {t} = useTranslation()


let defaultCenter = { };
let testCoordinates = [
  {
    "project_id": 1,
    "Project URL": "https://sakani.sa/app/offplan-projects/1",
    "project_name_eng": "Riyadh Skyline",
    "project_latitude": 24.774265,
    "project_longitude": 46.738586
  },
  {
    "project_id": 2,
    "Project URL": "https://sakani.sa/app/offplan-projects/2",
    "project_name_eng": "Kingdom Tower View",
    "project_latitude": 24.713552,
    "project_longitude": 46.675296
  },
  {
    "project_id": 3,
    "Project URL": "https://sakani.sa/app/offplan-projects/3",
    "project_name_eng": "Al Faisaliah Residences",
    "project_latitude": 24.690247,
    "project_longitude": 46.685400
  },
  {
    "project_id": 5,
    "Project URL": "https://sakani.sa/app/offplan-projects/4",
    "project_name_eng": "Riyadh Green Oasis",
    "project_latitude": 24.726658,
    "project_longitude": 46.767417
  },
  {
    "project_id": 5,
    "Project URL": "https://sakani.sa/app/offplan-projects/5",
    "project_name_eng": "Diplomatic Quarter Heights",
    "project_latitude": 24.709371,
    "project_longitude": 46.641861
  },
  {
    "project_id": 6,
    "Project URL": "https://sakani.sa/app/offplan-projects/6",
    "project_name_eng": "Riyadh Downtown Living",
    "project_latitude": 24.631900,
    "project_longitude": 46.715000
  },
  {
    "project_id": 7,
    "Project URL": "https://sakani.sa/app/offplan-projects/7",
    "project_name_eng": "North Riyadh Residences",
    "project_latitude": 24.850000,
    "project_longitude": 46.700000
  },
  {
    "project_id": 8,
    "Project URL": "https://sakani.sa/app/offplan-projects/8",
    "project_name_eng": "Eastern Riyadh Villas",
    "project_latitude": 24.710400,
    "project_longitude": 46.810000
  }
]


  // useEffect(()=>{
  //   defaultCenter = {
  //     lat: testCoordinates[0]?.project_latitude,
  //     lng: testCoordinates[0]?.project_longitude,
  //   }
  //   console.log(defaultCenter)
  // },[testCoordinates])
 

  return (
    <>
    <h3 className="text-white font-semibold text-xl mb-4">{t("mapView")}</h3>
    <div className="rounded-3xl border-2  overflow-hidden">
     
      <APIProvider apiKey={apiKey} libraries={['marker']}>
        <Map
          className={"w-full h-[60vh] overflow-y-scroll shadow-md"}
          styles={customMapStyle}
          defaultCenter={mapCenter}
         
          defaultZoom={11}
          // options={{
          //   styles: customMapStyle, 
          // }}
        >
          {/* Render Markers and Default InfoWindows */}
          {latLongDetails.map((location, index) => (
            <React.Fragment key={index}>
              <Marker
                 
                position={{ lat: location.project_latitude, lng: location.project_longitude}}
                onClick={() => setSelectedLocation(location)}
              
              />
              <InfoWindow
             
                position={{
                  lat: location.project_latitude + 0.0205,
                  lng: location.project_longitude,
                }}
              >
                <div className="max-w-60 border-none rounded-lg p-1 shadow-lg bg-white">
                  
                    <h3 className="font-bold text-black">{location.project_name_eng}</h3>
                    <a
                      href={location["Project URL"]}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-600 hover:underline text-xs"
                    >
                      {location["Project URL"]}
                    </a>
                  
                </div>
              </InfoWindow>
            </React.Fragment>
          ))}

          {/* Render InfoWindow for Selected Location */}
          {selectedLocation?.project_latitude && selectedLocation?.project_longitude && (
            <InfoWindow
              position={{
                lat: selectedLocation.project_latitude + 0.0105,
                lng: selectedLocation.project_longitude,
              }}
              onCloseClick={() => setSelectedLocation(null)}
            >
              <Card className="w-72 border-none">
                <CardContent>
                  <h3 className="font-bold">{selectedLocation.project_name_eng}</h3>
                  <a
                      href={location["Project URL"]}
                      target="_blank"
                      className="text-cyan-600 hover:underline text-xs"
                    >
                      {selectedLocation["Project URL"]}
                    </a>
                </CardContent>
               
              </Card>
            </InfoWindow>
          )}
        </Map>
      </APIProvider>
    </div>
    </>
  );
};

export default MapContainer;
