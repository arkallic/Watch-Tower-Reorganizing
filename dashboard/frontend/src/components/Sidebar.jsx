import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { LightBulbIcon } from '@heroicons/react/24/outline';
import {
  HomeIcon,
  UsersIcon,
  ShieldCheckIcon,
  CogIcon,
  DocumentTextIcon,
  PaperClipIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  ScaleIcon,
  ChatBubbleLeftRightIcon // Added for Channels
  
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Users', href: '/users', icon: UsersIcon },
  { name: 'Cases', href: '/cases', icon: ScaleIcon },
  { name: 'Channels', href: '/channels', icon: ChatBubbleLeftRightIcon }, // Added Channels link
  { name: 'Moderators', href: '/moderators', icon: ShieldCheckIcon },
  { name: 'Spotlight', href: '/spotlight', icon: LightBulbIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
  { name: 'Attachments', href: '/attachments', icon: PaperClipIcon },
  { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsOpen(false)} />
          <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-gray-900 border-r border-gray-700">
            <SidebarContent navigation={navigation} location={location} onClose={() => setIsOpen(false)} />
          </div>
        </div>
      )}

      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col z-50">
        <div className="flex min-h-0 flex-1 flex-col bg-gray-900 border-r border-gray-800">
          <SidebarContent navigation={navigation} location={location} />
        </div>
      </div>
    </>
  );
}

function SidebarContent({ navigation, location, onClose }) {
  return (
    <>
      <div className="flex flex-col items-center py-6 px-4 border-b border-gray-800 relative">
        <img 
          src="/images/logo.png" 
          alt="Watch Tower Logo" 
          className="h-36 w-36 mb-3" 
        />
        <h1 className="text-xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
          Watch Tower
        </h1>
        <p className="text-xs text-gray-400">Moderation Dashboard</p>
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        )}
      </div>

      <nav className="flex-1 px-4 py-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={classNames(
                isActive
                  ? 'bg-amber-500/10 text-amber-300 shadow-[0_0_15px_rgba(252,211,77,0.3)]'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                'group flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-all duration-200'
              )}
            >
              <item.icon
                className={classNames(
                  isActive ? 'text-amber-300' : 'text-gray-500 group-hover:text-white',
                  'mr-3 h-5 w-5 transition-colors duration-200'
                )}
              />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-gray-800">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 text-xs text-gray-400">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span>System Online</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">v1.0.0</p>
        </div>
      </div>
    </>
  );
}