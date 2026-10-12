"use client"
import React from 'react'

const AlbumKit: React.FC = () => {
  return (
    <div className="fixed right-4 bottom-4 z-50">
      <div className="flex flex-col items-end space-y-2">
        <a href="#" className="inline-flex items-center space-x-2 bg-white/6 text-white px-3 py-2 rounded backdrop-blur-md hover:bg-white/8">
          <span className="text-sm">⚙️</span>
          <span className="text-sm">工具</span>
        </a>
        <a href="#" className="inline-flex items-center space-x-2 bg-white/6 text-white px-3 py-2 rounded backdrop-blur-md hover:bg-white/8">
          <span className="text-sm">⬇️</span>
          <span className="text-sm">下载</span>
        </a>
      </div>
    </div>
  )
}

export default AlbumKit
