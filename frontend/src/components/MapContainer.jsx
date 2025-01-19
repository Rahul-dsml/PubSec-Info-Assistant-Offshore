import React, { useEffect, useState } from "react";
// import {
//   GoogleMap,
//   LoadScript,
//   Marker,
//   InfoWindow,
//   DirectionsRenderer,
// } from "@react-google-maps/api";
import { Button } from "@/components/ui/button"; // ShadCN Button component
import { Card, CardContent, CardFooter } from "@/components/ui/card"; // ShadCN Card components
import {
  AdvancedMarker,
  Marker,
  APIProvider,
  Map,
  InfoWindow,
} from "@vis.gl/react-google-maps";
import useAppStore from "@/state/zustand";

let apiKey = "AIzaSyA9w9eOWbbTRa9XI2G4HrSn5mexzZiftoo";

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

const MapContainer = ({ locations }) => {
  const {latLongDetails} = useAppStore()
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [directionsResponse, setDirectionsResponse] = useState(null);
  const [mapCenter,setMapCenter] = useState({lat: 18.286109,
    lng: 42.513347,})


  const defaultCenter = {
    lat: 18.286109,
    lng: 42.513347,
  };
  console.log(locations);

  useEffect(()=>{
    setMapCenter({
      lat: locations?.project_latitude,
      lng: locations?.project_longitude,
    })
  },[locations])
  // console.log(latLongDetails)
  // Handle fetching directions
  // const getDirections = async (destination) => {
  //   if (navigator.geolocation) {
  //     navigator.geolocation.getCurrentPosition(
  //       async (position) => {
  //         const { latitude, longitude } = position.coords;

  //         const directionsService = new window.google.maps.DirectionsService();
  //         const result = await directionsService.route({
  //           origin: { lat: latitude, lng: longitude },
  //           destination,
  //           travelMode: window.google.maps.TravelMode.DRIVING,
  //         });

  //         setDirectionsResponse(result);
  //       },
  //       () => {
  //         alert("Failed to fetch your current location.");
  //       }
  //     );
  //   } else {
  //     alert("Geolocation is not supported by your browser.");
  //   }
  // };

  return (
    <div className="rounded-3xl border-2 overflow-hidden">
      <APIProvider apiKey={apiKey}>
        <Map
          className={"w-full h-[90vh]  shadow-md"}
          styles={customMapStyle}
          defaultCenter={mapCenter}
          defaultZoom={14}
          // options={{
          //   mapTypeControl: true,
          //   styles: customMapStyle, // Custom styles applied
          // }}
        >
          {/* Render Markers and Default InfoWindows */}
          {locations.map((location, index) => (
            <React.Fragment key={index}>
              <Marker
                position={{ lat: location.project_latitude, lng: location.project_longitude}}
                onClick={() => setSelectedLocation(location)}
              />
              <InfoWindow
                position={{
                  lat: location.project_latitude,
                  lng: location.project_longitude,
                }}
              >
                <Card className="max-w-60 border-none rounded-lg shadow-lg bg-white">
                  <CardContent className="p-4">
                    {/* <img
                      src={`https://maps.googleapis.com/maps/api/streetview?size=400x200&location=${location.project_latitude},${location.project_longitude}&key=${apiKey}`}
                      alt="Street View"
                      className="w-full h-auto"
                    /> */}
                    <h3 className="font-bold">{location.project_name_eng}</h3>
                    <a
                      href={location["Project URL"]}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-600 hover:underline text-xs"
                    >
                      {location["Project URL"]}
                    </a>
                  </CardContent>
                </Card>
              </InfoWindow>
            </React.Fragment>
          ))}

          {/* Render InfoWindow for Selected Location */}
          {selectedLocation?.project_latitude && selectedLocation?.project_longitude && (
            <InfoWindow
              position={{
                lat: selectedLocation.project_latitude,
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
                      rel="noopener noreferrer"
                      className="text-cyan-600 hover:underline text-xs"
                    >
                      {selectedLocation["Project URL"]}
                    </a>
                </CardContent>
                {/* <CardFooter>
                  <Button
                  // onClick={() =>
                  //   getDirections({
                  //     lat: selectedLocation.lat,
                  //     lng: selectedLocation.lng,
                  //   })
                  // }
                  >
                    Get Directions
                  </Button>
                </CardFooter> */}
              </Card>
            </InfoWindow>
          )}

          {/* Render Directions if Available */}
          {directionsResponse && (
            <DirectionsRenderer directions={directionsResponse} />
          )}
        </Map>
      </APIProvider>
    </div>
  );
};

export default MapContainer;
