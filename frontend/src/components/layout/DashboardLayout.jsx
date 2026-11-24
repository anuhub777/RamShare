import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export const DashboardLayout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-navy-950">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
