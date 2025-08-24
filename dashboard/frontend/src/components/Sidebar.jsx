import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  XMarkIcon,
  HomeIcon,
  UsersIcon,
  ShieldCheckIcon,
  CogIcon,
  DocumentTextIcon,
  PaperClipIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  ScaleIcon,
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  FolderIcon,
  ChevronDownIcon,
  UserGroupIcon,
  ClockIcon, // <-- Import new icon
  ArchiveBoxIcon
} from '@heroicons/react/24/outline';

// Navigation structure with Timeline added to Moderation
const navigation = [
  // 1. Main View
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  // 2. Moderation Dropdown (Core Tools)
  {
    name: 'Moderation',
    icon: ShieldCheckIcon,
    children: [
      { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
      { name: 'Cases', href: '/cases', icon: ScaleIcon },
      { name: 'Timeline', href: '/timeline', icon: ClockIcon }, // <-- ADDED
      { name: 'Channels', href: '/channels', icon: ChatBubbleLeftRightIcon },
      { name: 'Spotlight', href: '/spotlight', icon: LightBulbIcon },
      { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
    ]
  },
  // 3. Community Dropdown (Management)
  {
    name: 'Community',
    icon: UserGroupIcon,
    children: [
      { name: 'Users', href: '/users', icon: UsersIcon },
      { name: 'Moderators', href: '/moderators', icon: ShieldCheckIcon },
      { name: 'Cohorts', href: '/cohorts', icon: ArchiveBoxIcon }
    ]
  },
  // 4. Resources Dropdown (Assets)
  {
    name: 'Resources',
    icon: FolderIcon,
    children: [
      { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
      { name: 'Attachments', href: '/attachments', icon: PaperClipIcon },
    ]
  },
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
  const [openMenus, setOpenMenus] = useState({});

  // Effect to automatically open the parent menu if a child route is active on page load
  useEffect(() => {
    const newOpenMenus = {};
    navigation.forEach(item => {
      if (item.children) {
        const isParentActive = item.children.some(child => location.pathname === child.href || (child.href !== '/' && location.pathname.startsWith(child.href)));
        if (isParentActive) {
          newOpenMenus[item.name] = true;
        }
      }
    });
    setOpenMenus(newOpenMenus);
  }, [location.pathname]);

  const toggleMenu = (name) => {
    setOpenMenus(prev => ({ ...prev, [name]: !prev[name] }));
  };

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

      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => {
           const isParentActive = item.children && item.children.some(child => location.pathname === child.href || (child.href !== '/' && location.pathname.startsWith(child.href)));
          
          return item.children ? (
            <div key={item.name}>
              <button
                onClick={() => toggleMenu(item.name)}
                className={classNames(
                  isParentActive
                    ? 'text-amber-300'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                  'group w-full flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-all duration-200'
                )}
              >
                <item.icon
                  className={classNames(
                   isParentActive
                      ? 'text-amber-300'
                      : 'text-gray-500 group-hover:text-white',
                    'mr-3 h-5 w-5 transition-colors duration-200'
                  )}
                />
                <span className="flex-1 text-left">{item.name}</span>
                <ChevronDownIcon
                  className={classNames(
                    'h-5 w-5 transform transition-transform duration-200',
                    openMenus[item.name] ? 'rotate-180' : ''
                  )}
                />
              </button>
              {openMenus[item.name] && (
                <div className="pt-1 pl-5 space-y-1">
                  {item.children.map((child) => {
                    const isActive = location.pathname === child.href || (child.href !== '/' && location.pathname.startsWith(child.href));
                    return (
                      <NavLink
                        key={child.name}
                        to={child.href}
                        onClick={onClose}
                        className={classNames(
                          isActive
                            ? 'bg-amber-500/10 text-amber-300'
                            : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                          'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200'
                        )}
                      >
                        {child.name}
                      </NavLink>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={classNames(
                location.pathname === item.href
                  ? 'bg-amber-500/10 text-amber-300 shadow-[0_0_15px_rgba(252,211,77,0.3)]'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                'group flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-all duration-200'
              )}
            >
              <item.icon
                className={classNames(
                  location.pathname === item.href ? 'text-amber-300' : 'text-gray-500 group-hover:text-white',
                  'mr-3 h-5 w-5 transition-colors duration-200'
                )}
              />
              {item.name}
            </NavLink>
          )
        })}
      </nav>

      <div className="px-4 py-4 border-t border-gray-800">
        <div className="flex justify-between items-center">
            {/* Left Side: System Status */}
            <div className="text-left">
                <div className="flex items-center space-x-2 text-xs text-gray-400">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span>System Online</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">v1.0.0</p>
            </div>

            {/* Right Side: Settings Icon Link */}
            <NavLink
                to="/settings"
                onClick={onClose}
                aria-label="Settings"
                className={({ isActive }) => classNames(
                    isActive
                        ? 'bg-amber-500/10 text-amber-300'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                    'p-2 rounded-md transition-colors duration-200'
                )}
            >
                <CogIcon className="h-5 w-5" />
            </NavLink>
        </div>
      </div>
    </>
  );
}