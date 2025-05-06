import React, { useEffect, useRef, useState } from 'react';
import { GoogleMap, Marker, useJsApiLoader } from '@react-google-maps/api';
import '../styles/MapModal.css';

const containerStyle = {
  width: '100%',
  height: '300px',
};
const GLOBAL_IP = 'http://localhost:5001';

const libraries = ['places'];

const MapModal = ({ onClose, userLocation }) => {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries,
  });

  const [doctorList, setDoctorList] = useState([]);
  const [selected, setSelected] = useState(null);
  const mapRef = useRef();

  useEffect(() => {
    if (userLocation?.lat && userLocation?.lng) {
      fetchNearbyDoctors(userLocation.lat, userLocation.lng);
    }
  }, [userLocation]);

  const fetchNearbyDoctors = async (lat, lng) => {
    try {
      const res = await fetch(`${GLOBAL_IP}/api/nearby-doctors?lat=${lat}&lng=${lng}`);
      const data = await res.json();
      setDoctorList(data.results || []);
    } catch (err) {
      console.error('Error fetching doctors:', err);
    }
  };

  if (loadError) return <div>Error loading maps</div>;
  if (!isLoaded) return <div>Loading Map...</div>;

  return (
    <div className="map-modal-overlay">
      <div className="map-modal">
        <h2>🆘 Immediate Help</h2>
        <p>Here are some nearby doctors and emergency resources:</p>

        <GoogleMap
          mapContainerStyle={containerStyle}
          center={userLocation}
          zoom={13}
          onLoad={(map) => (mapRef.current = map)}
        >
          {doctorList.map((place, index) => (
            <Marker
              key={index}
              position={{
                lat: place.geometry.location.lat,
                lng: place.geometry.location.lng,
              }}
              title={place.name}
            />
          ))}
        </GoogleMap>

        <ul className="doctor-list">
          {doctorList.map((doc, index) => (
            <li
              key={index}
              className={selected === index ? 'selected-doc' : ''}
              onClick={() => {
                setSelected(index);
                mapRef.current?.panTo({
                  lat: doc.geometry.location.lat,
                  lng: doc.geometry.location.lng,
                });
              }}
            >
              <strong>{doc.name}</strong>
              <br />
              <small>{doc.vicinity}</small>
            </li>
          ))}
        </ul>

        <h4 className="helpline-title">📞 Emergency Helplines:</h4>
        <div className="helpline-list">
            <div>988 – Suicide & Crisis Lifeline (USA)</div>
            <div>911 – Emergency Services</div>
            <div>
                🌍 International:{' '}
             <a
                href="https://findahelpline.com"
                target="_blank"
                rel="noreferrer"
                className="helpline-link"
             >
                findahelpline.com
            </a>
            </div>
        </div>

        <button className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default MapModal;
