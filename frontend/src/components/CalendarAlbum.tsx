"use client"
import React from 'react'
import type { FC } from 'react'
import SimulationExperiment from './SimulationExperiment'

type Props = {
  folder: string
  images: string[]
  labels?: { [key: string]: string }
}

const CalendarAlbum: FC<Props> = ({ folder, images, labels }) => {
  const [showLogs, setShowLogs] = React.useState(false)
  const [logs, setLogs] = React.useState<unknown>(null)
  const [showSimulation, setShowSimulation] = React.useState(false)

  const toggleLogs = async () => {
    // If toggling on, fetch latest logs once
    if (!showLogs) {
      try {
        const ts = Date.now()
        const res = await fetch(`/copilot-last-output.json?_=${ts}`, { cache: 'no-store' })
        if (res.ok) {
          const data = await res.json()
          setLogs(data)
        } else {
          setLogs({ error: `HTTP ${res.status}` })
        }
      } catch (e: any) {
        setLogs({ error: e?.message || 'fetch failed' })
      }
    }
    setShowLogs(v => !v)
  }
  const handleImageClick = (index: number, src: string) => {
    if (index === 0) {
      // 点击第一个图片进入模拟实验页面
      setShowSimulation(true)
    } else {
      // 其他图片保持原有行为
      try { 
        window.open(src, '_blank') 
      } catch (e) { 
        window.location.href = src 
      }
    }
  }

  if (showSimulation) {
    return <SimulationExperiment onBack={() => setShowSimulation(false)} />
  }

  return (
    <div className="w-full p-6">
      <div className="max-w-6xl mx-auto bg-[rgba(2,6,23,0.9)] rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white text-2xl font-bold">{folder} — 相册</h3>
          <button
            onClick={toggleLogs}
            className="ml-4 inline-flex items-center rounded-md border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-sky-100 hover:bg-white/10 transition-colors"
          >
            {showLogs ? '隐藏Copilot输出' : '显示Copilot输出'}
          </button>
        </div>

        {showLogs && (
          <div className="mb-4 rounded-lg border border-white/10 bg-black/30 p-3 text-xs text-sky-100 max-h-64 overflow-auto">
            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(logs, null, 2)}</pre>
          </div>
        )}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {images.map((src, i) => (
            <div key={i} className="relative overflow-hidden rounded-lg bg-black/20 p-1">
              <button
                onClick={() => handleImageClick(i, src)}
                className={`w-full h-40 block p-0 m-0 rounded-md overflow-hidden focus:outline-none ${
                  i === 0 ? 'ring-2 ring-blue-400/50 ring-offset-2 ring-offset-transparent' : ''
                }`}
                aria-label={i === 0 ? '进入模拟实验' : `打开图片 ${i + 1}`}
              >
                <img src={src} alt={`${folder} image ${i + 1}`} loading="lazy" className="w-full h-full object-cover rounded-md transform transition-all duration-300 hover:scale-105" />
                {/* 第一个图片添加实验标识 */}
                {i === 0 && (
                  <div className="absolute top-2 left-2 bg-blue-500/80 text-white text-xs px-2 py-1 rounded backdrop-blur-sm border border-blue-400/50">
                    🔬 模拟实验
                  </div>
                )}
              </button>

              {/* label badge: derive filename */}
              <div className="absolute right-2 bottom-2 bg-black/60 text-xs text-sky-100 px-2 py-1 rounded backdrop-blur-sm border border-white/6 max-w-[70%]">
                {(function(){
                  const parts = src.split('/')
          const fname = parts[parts.length - 1]
          const tag = (labels && labels[fname]) ? labels[fname] : ''
          // display name without extension
          const displayName = fname.includes('.') ? fname.replace(/\.[^/.]+$/, '') : fname
                  return (
                    <div className="text-right">
                      <div className="text-[11px] font-medium leading-tight">{tag}</div>
            <div className="text-[10px] text-slate-200 truncate max-w-[120px]">{displayName}</div>
                    </div>
                  )
                })()}
              </div>

              {/* edge effect: soft glow and gradient mask */}
              <div className="pointer-events-none absolute inset-0 rounded-md" style={{ boxShadow: '0 6px 30px rgba(2,8,23,0.6), inset 0 0 18px rgba(255,255,255,0.02)' }}>
                <div className="absolute inset-0 rounded-md" style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.12) 100%)', mixBlendMode: 'overlay' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CalendarAlbum
