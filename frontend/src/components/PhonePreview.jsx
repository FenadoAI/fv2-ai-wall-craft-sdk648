import React from 'react';
import { Loader2 } from 'lucide-react';

const PhonePreview = ({ imageUrl, isLoading }) => {
  return (
    <div className="relative">
      {/* iPhone Frame */}
      <div className="relative w-64 h-[520px] bg-black rounded-[3rem] p-2 shadow-2xl">
        {/* Outer frame with realistic phone styling */}
        <div className="relative w-full h-full bg-gray-900 rounded-[2.5rem] overflow-hidden">
          {/* Notch */}
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-black rounded-full z-20"></div>

          {/* Screen */}
          <div className="relative w-full h-full bg-gray-100 rounded-[2.2rem] overflow-hidden">
            {/* Status bar */}
            <div className="absolute top-0 left-0 right-0 h-10 bg-black/5 flex items-center justify-between px-6 pt-2 z-10">
              <div className="flex items-center space-x-1">
                <div className="text-xs font-semibold">9:41</div>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-2 bg-black rounded-sm"></div>
                <div className="w-6 h-3 border border-black rounded-sm">
                  <div className="w-4 h-1.5 bg-green-500 rounded-sm mt-0.5 ml-0.5"></div>
                </div>
              </div>
            </div>

            {/* Wallpaper Display */}
            <div className="absolute inset-0 flex items-center justify-center">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center space-y-4 text-gray-500">
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <p className="text-sm">Generating...</p>
                </div>
              ) : imageUrl ? (
                <img
                  src={imageUrl}
                  alt="Generated wallpaper"
                  className="w-full h-full object-cover"
                  style={{ objectPosition: 'center center' }}
                />
              ) : (
                <div className="flex flex-col items-center justify-center space-y-4 text-gray-400">
                  <div className="w-16 h-16 border-2 border-gray-300 rounded-lg flex items-center justify-center">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-sm text-center">Your wallpaper will appear here</p>
                </div>
              )}
            </div>

            {/* Home indicator */}
            <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-black/30 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Phone shadow */}
      <div className="absolute inset-0 -z-10 transform translate-y-2 blur-xl opacity-25">
        <div className="w-64 h-[520px] bg-black rounded-[3rem]"></div>
      </div>
    </div>
  );
};

export default PhonePreview;