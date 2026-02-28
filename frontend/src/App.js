import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import TripPlannerPage from './pages/TripPlannerPage';
import ResultsPage from './pages/ResultsPage';
import DestinationDetailsPage from './pages/DestinationDetailsPage';

function App() {
  const [recommendations, setRecommendations] = useState(null);
  const [userPrefs, setUserPrefs] = useState(null);
  const [selectedDestination, setSelectedDestination] = useState(null);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/plan"
          element={
            <TripPlannerPage
              setRecommendations={setRecommendations}
              setUserPrefs={setUserPrefs}
            />
          }
        />
        <Route
          path="/results"
          element={
            <ResultsPage
              recommendations={recommendations}
              userPrefs={userPrefs}
              setSelectedDestination={setSelectedDestination}
            />
          }
        />
        <Route
          path="/destination/:name"
          element={
            <DestinationDetailsPage
              destination={selectedDestination}
              userPrefs={userPrefs}
            />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
