'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth'
import ProtectedRoute from '@/components/ProtectedRoute'
import EngagementChart from '@/components/EngagementChart'
import AccountsPage from '@/app/accounts/page'
import PromptsPage from '@/app/prompts/page'
import ImagesPage from '@/app/images/page'

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')

  const handleSignOut = async () => {
    await signOut()
  }

  return (
    <ProtectedRoute>
                   <div className="min-h-screen relative">
               {/* Background decorative elements */}
               <div className="absolute inset-0 overflow-hidden pointer-events-none">
                 <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
                 <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
                 
                 {/* Decorative lines */}
                 <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
                 <div className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
                 
                 {/* Decorative circles */}
                 <div className="absolute top-1/3 right-1/4 w-32 h-32 border border-purple-500/20 rounded-full"></div>
                 <div className="absolute bottom-1/3 left-1/4 w-24 h-24 border border-purple-500/15 rounded-full"></div>
                 <div className="absolute top-2/3 right-1/3 w-16 h-16 border border-purple-500/25 rounded-full"></div>
               </div>

                       {/* Header */}
               <header className="modern-nav relative z-10">
                 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                   <div className="flex justify-between items-center h-20">
                     <div className="flex items-center space-x-8">
                       <h1 className="text-3xl font-bold gradient-text">
                         } Threads Bot Dashboard
                       </h1>
                       <div className="hidden md:flex items-center space-x-8 text-sm">
                         <span className="text-gray-300">DASHBOARD</span>
                         <span className="text-gray-300">ACCOUNTS</span>
                         <span className="text-gray-300">PROMPTS</span>
                         <span className="text-gray-300">SCHEDULE</span>
                       </div>
                     </div>
                     <div className="flex items-center space-x-6">
                       <span className="text-sm text-gray-300">
                         Welcome, {user?.email}
                       </span>
                       <button
                         onClick={handleSignOut}
                         className="modern-button px-6 py-2 text-sm"
                       >
                         Sign Out
                       </button>
                     </div>
                   </div>
                 </div>
               </header>

        {/* Navigation */}
        <nav className="modern-nav relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {[
                { id: 'dashboard', name: 'Dashboard' },
                { id: 'accounts', name: 'Accounts' },
                { id: 'prompts', name: 'Prompts' },
                { id: 'schedule', name: 'Schedule' },
                                     { id: 'images', name: 'Images' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-link py-6 px-1 font-medium text-sm transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Content */}
        <main className="relative z-10 max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
          {activeTab === 'dashboard' && <DashboardContent />}
          {activeTab === 'accounts' && <AccountsContent />}
          {activeTab === 'prompts' && <PromptsContent />}
          {activeTab === 'schedule' && <ScheduleContent />}
                           {activeTab === 'images' && <ImagesContent />}
        </main>
      </div>
    </ProtectedRoute>
  )
}

       function DashboardContent() {
         return (
           <div className="space-y-8">
             {/* Hero Section */}
             <div className="modern-card p-12 floating">
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                 <div>
                   <h2 className="text-4xl font-bold gradient-text mb-6">
                     } Threads Bot Is a Premier Social Media Automation Platform
                   </h2>
                   <p className="text-lg text-gray-300 mb-8 leading-relaxed">
                     } Renowned for powering the backbone of social media ecosystems with our state-of-the-art automation services, content scheduling & engagement tracking.
                   </p>
                   <button className="modern-button px-8 py-4 text-lg glow-on-hover">
                     GET STARTED
                   </button>
                 </div>
                 <div className="relative">
                   <div className="grid grid-cols-2 gap-6">
                     <div className="modern-card p-6 text-center">
                       <div className="text-5xl font-bold gradient-text mb-2">192k</div>
                       <div className="text-sm text-gray-300">Total Posts</div>
                       <div className="mt-4 w-8 h-8 bg-purple-500 rounded-full mx-auto opacity-60"></div>
                     </div>
                     <div className="modern-card p-6 text-center">
                       <div className="text-5xl font-bold gradient-text mb-2">34</div>
                       <div className="text-sm text-gray-300">Active Accounts</div>
                       <div className="mt-4 w-8 h-8 bg-green-500 rounded-full mx-auto opacity-60"></div>
                     </div>
                   </div>
                   
                   {/* Connection lines */}
                   <div className="absolute top-1/2 left-1/2 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent transform -translate-y-1/2"></div>
                   <div className="absolute top-1/2 left-1/2 w-px h-full bg-gradient-to-b from-transparent via-purple-500/30 to-transparent transform -translate-x-1/2"></div>
                 </div>
               </div>
             </div>

             {/* Dashboard Overview */}
             <div className="modern-card p-8">
               <h3 className="text-2xl font-bold text-white mb-8">
                 Dashboard Overview
               </h3>
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                 <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
                   <div className="text-4xl font-bold gradient-text mb-2">0</div>
                   <div className="text-sm text-gray-300">Total Accounts</div>
                   <div className="mt-4 w-8 h-8 bg-purple-500 rounded-full mx-auto opacity-60"></div>
                 </div>
                 <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
                   <div className="text-4xl font-bold gradient-text mb-2">0</div>
                   <div className="text-sm text-gray-300">Active</div>
                   <div className="mt-4 w-8 h-8 bg-green-500 rounded-full mx-auto opacity-60"></div>
                 </div>
                 <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
                   <div className="text-4xl font-bold gradient-text mb-2">0</div>
                   <div className="text-sm text-gray-300">Scheduled</div>
                   <div className="mt-4 w-8 h-8 bg-yellow-500 rounded-full mx-auto opacity-60"></div>
                 </div>
                 <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
                   <div className="text-4xl font-bold gradient-text mb-2">0</div>
                   <div className="text-sm text-gray-300">Errors</div>
                   <div className="mt-4 w-8 h-8 bg-red-500 rounded-full mx-auto opacity-60"></div>
                 </div>
               </div>
             </div>
      
      {/* Engagement Analytics */}
      <div className="modern-card p-8">
        <EngagementChart />
      </div>
    </div>
  )
}

function AccountsContent() {
  return <AccountsPage />
}

function PromptsContent() {
  return <PromptsPage />
}

function ScheduleContent() {
  return (
    <div className="modern-card p-8">
      <h3 className="text-2xl font-bold text-white mb-6">
        Schedule
      </h3>
      <p className="text-gray-300">No scheduled posts yet.</p>
    </div>
  )
}

       function ImagesContent() {
         return <ImagesPage />
       } 