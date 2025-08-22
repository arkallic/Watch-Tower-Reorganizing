import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import UserProfile from './pages/UserProfile';
import Cases from './pages/Cases';
import Moderators from './pages/Moderators';
import ModeratorProfile from './pages/ModeratorProfile';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Reports from './pages/Reports';
import AttachmentViewer from './pages/AttachmentViewer';
import SearchPage from './pages/SearchPage';
import ErrorBoundary from './components/ErrorBoundary';
import { ApiProvider } from './context/ApiContext';
import FirstTimeSetup from './setup/pages/FirstTimeSetup';
import Channels from './pages/Channels';
import Spotlight from './pages/Spotlight';
import SpotlightGate from './spotlight-gate/SpotlightGate';


function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isFirstTime, setIsFirstTime] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSetupStatus = async () => {
      try {
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const apiBase = isDevelopment ? 'http://localhost:8000' : '';
        const fetchUrl = `${apiBase}/api/pagedata/setup-check`;
        
        const response = await fetch(fetchUrl);
        const data = await response.json();

        if (data.reason === 'corruption') {
          alert(
            'Warning: Your settings file was detected but appears to be corrupt. \n\nYou will be taken to the setup wizard to re-configure the bot. Your old settings could not be read.'
          );
        }

        setIsFirstTime(data.isFirstTime);
      } catch (error) {
        console.error('Failed to check setup status:', error);
        setIsFirstTime(false);
      } finally {
        setLoading(false);
      }
    };

    checkSetupStatus();
  }, []); // The empty array ensures this runs only once on mount

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#1A1E23]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400 mx-auto"></div>
          <p className="text-white mt-4 text-lg">Loading Watch Tower...</p>
        </div>
      </div>
    );
  }

  if (isFirstTime) {
    return <FirstTimeSetup onComplete={() => setIsFirstTime(false)} />;
  }

  // Around line 40-90, replace the return statement with:

return (
  <ErrorBoundary>
    <ApiProvider>
      <Router>
        <Routes>
          {/* SpotlightGate route - standalone without sidebar */}
          <Route path="/spotlight/:userId/:key" element={<SpotlightGate />} />
          
          {/* All other routes with sidebar layout */}
          <Route path="*" element={
            <div className="relative flex h-screen bg-[#1A1E23] overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-0" 
                   style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(245, 194, 68, 0.15) 0%, rgba(26, 30, 35, 0) 70%)' }}>
              </div>

              <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

              <div className="relative z-10 flex-1 flex flex-col overflow-hidden lg:pl-64">
                <main className="flex-1 overflow-x-hidden overflow-y-auto">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/users" element={<Users />} />
                    <Route path="/users/:userId" element={<UserProfile />} />
                    <Route path="/cases" element={<Cases />} />
                    <Route path="/moderators" element={<Moderators />} />
                    <Route path="/moderators/:moderatorId" element={<ModeratorProfile />} />
                    <Route path="/spotlight" element={<Spotlight />} />
                    <Route path="/channels" element={<Channels />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/attachments" element={<AttachmentViewer />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/setup" element={<FirstTimeSetup onComplete={() => setIsFirstTime(false)} />} />
                  </Routes>
                </main>
              </div>
            </div>
          } />
        </Routes>
      </Router>
    </ApiProvider>
  </ErrorBoundary>
);
}

export default App;