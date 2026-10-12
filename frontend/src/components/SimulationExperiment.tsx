"use client"
import React, { useState, useEffect } from 'react'
import { ArrowLeft, Play, CheckCircle, Clock, Settings, Target, BarChart3 } from 'lucide-react'
import AnalysisReport from './AnalysisReport'

interface ExperimentConfig {
  id: string
  epoch: number
  status: 'pending' | 'running' | 'completed'
  accuracy?: number
  startTime?: Date
  completionTime?: Date
}

interface SimulationExperimentProps {
  onBack: () => void
}

const SimulationExperiment: React.FC<SimulationExperimentProps> = ({ onBack }) => {
  const [experiments, setExperiments] = useState<ExperimentConfig[]>([
    { id: 'EXP-001', epoch: 2, status: 'pending' },
    { id: 'EXP-002', epoch: 3, status: 'pending' },
    { id: 'EXP-003', epoch: 4, status: 'pending' },
    { id: 'EXP-004', epoch: 5, status: 'pending' },
    { id: 'EXP-005', epoch: 6, status: 'pending' },
  ])

  const [currentRunning, setCurrentRunning] = useState<string | null>(null)
  const [showAnalysisReport, setShowAnalysisReport] = useState(false)

  const startExperiment = (id: string) => {
    if (currentRunning) return // 防止同时运行多个实验

    setCurrentRunning(id)
    setExperiments(prev => 
      prev.map(exp => 
        exp.id === id 
          ? { ...exp, status: 'running', startTime: new Date() }
          : exp
      )
    )

    // 10秒后完成实验
    setTimeout(() => {
      const accuracy = Math.round((85 + Math.random() * 10) * 100) / 100 // 85-95%的随机准确率
      setExperiments(prev => 
        prev.map(exp => 
          exp.id === id 
            ? { 
                ...exp, 
                status: 'completed', 
                accuracy,
                completionTime: new Date() 
              }
            : exp
        )
      )
      setCurrentRunning(null)
    }, 10000)
  }

  const formatDuration = (start: Date, end?: Date) => {
    const endTime = end || new Date()
    const duration = Math.floor((endTime.getTime() - start.getTime()) / 1000)
    return `${duration}s`
  }

  if (showAnalysisReport) {
    return <AnalysisReport onBack={() => setShowAnalysisReport(false)} />
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 深色星空背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-slate-950 to-black">
        {/* 星空层 */}
        <div className="absolute inset-0">
          <div className="stars-layer-1"></div>
          <div className="stars-layer-2"></div>
          <div className="stars-layer-3"></div>
        </div>
        {/* 深层光晕 */}
        <div className="absolute inset-0 bg-gradient-radial from-blue-950/20 via-purple-950/10 to-transparent"></div>
        {/* 动态粒子 */}
        <div className="floating-particles"></div>
      </div>
      
      <style jsx>{`
        .stars-layer-1, .stars-layer-2, .stars-layer-3, .floating-particles {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
        }
        .stars-layer-1 {
          background: radial-gradient(1px 1px at 20px 30px, #fff, transparent),
                      radial-gradient(1px 1px at 40px 70px, #fff, transparent),
                      radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                      radial-gradient(1px 1px at 130px 80px, #fff, transparent),
                      radial-gradient(1px 1px at 160px 30px, #fff, transparent);
          background-repeat: repeat;
          background-size: 200px 100px;
          animation: twinkle 4s ease-in-out infinite alternate;
          opacity: 0.8;
        }
        .stars-layer-2 {
          background: radial-gradient(1px 1px at 30px 50px, #60a5fa, transparent),
                      radial-gradient(1px 1px at 80px 20px, #a855f7, transparent),
                      radial-gradient(1px 1px at 120px 90px, #06b6d4, transparent);
          background-repeat: repeat;
          background-size: 250px 150px;
          animation: drift 80s linear infinite;
          opacity: 0.6;
        }
        .stars-layer-3 {
          background: radial-gradient(0.5px 0.5px at 15px 25px, #fff, transparent),
                      radial-gradient(0.5px 0.5px at 75px 65px, #fff, transparent),
                      radial-gradient(0.5px 0.5px at 115px 15px, #fff, transparent);
          background-repeat: repeat;
          background-size: 150px 80px;
          animation: sparkle 6s ease-in-out infinite;
          opacity: 0.4;
        }
        .floating-particles {
          background: radial-gradient(2px 2px at 100px 100px, rgba(96, 165, 250, 0.3), transparent),
                      radial-gradient(1.5px 1.5px at 300px 200px, rgba(168, 85, 247, 0.4), transparent),
                      radial-gradient(1px 1px at 200px 350px, rgba(6, 182, 212, 0.5), transparent);
          background-repeat: repeat;
          background-size: 400px 400px;
          animation: float 100s linear infinite;
          opacity: 0.3;
        }
        @keyframes twinkle {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
        @keyframes drift {
          from { background-position: 0 0; }
          to { background-position: -250px -150px; }
        }
        @keyframes sparkle {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.2); }
        }
        @keyframes float {
          from { background-position: 0 0; }
          to { background-position: -400px -400px; }
        }
      `}</style>
      
      <div className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-4 py-2 bg-black/40 hover:bg-black/60 rounded-lg backdrop-blur-xl border border-gray-700/50 text-gray-200 transition-all duration-200 shadow-2xl"
              >
                <ArrowLeft size={20} />
                返回相册
              </button>
              <button
                onClick={() => setShowAnalysisReport(true)}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 hover:bg-cyan-400/30 rounded-lg backdrop-blur-xl border border-cyan-400/30 text-cyan-200 transition-all duration-200 shadow-2xl"
              >
                <BarChart3 size={20} />
                查看分析报告
              </button>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl border border-blue-400/30 shadow-2xl backdrop-blur-xl">
                <BarChart3 className="text-blue-300" size={28} />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-200 via-purple-200 to-cyan-200 bg-clip-text text-transparent">
                天体图像分类模型 - Epoch优化实验
              </h1>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-xl border border-gray-700/50 rounded-xl p-6 mb-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <Target className="text-emerald-300" size={24} />
              <h2 className="text-xl font-semibold text-gray-100">实验目标</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-emerald-300 mb-2">研究问题</h3>
                <p className="text-gray-300 leading-relaxed">
                  探究训练epoch数量对CNN模型在天体图像分类任务中准确率的影响，寻找最优的训练轮次配置。
                </p>
              </div>
              <div>
                <h3 className="text-lg font-medium text-blue-300 mb-2">实验设计</h3>
                <div className="space-y-2 text-sm text-gray-300">
                  <div><span className="text-yellow-300">自变量：</span> Epoch数量 (2, 3, 4, 5, 6)</div>
                  <div><span className="text-green-300">因变量：</span> 模型验证准确率 (%)</div>
                  <div><span className="text-purple-300">控制变量：</span> 模型架构、数据集、优化器、batch_size</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-xl border border-gray-700/50 rounded-xl p-6 mb-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <Settings className="text-purple-300" size={24} />
              <h2 className="text-xl font-semibold text-gray-100">控制变量配置</h2>
            </div>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-2">
                <div className="text-gray-400">模型架构</div>
                <div className="text-gray-200">CNN (Conv2D + MaxPooling2D)</div>
              </div>
              <div className="space-y-2">
                <div className="text-gray-400">优化器</div>
                <div className="text-gray-200">Adam</div>
              </div>
              <div className="space-y-2">
                <div className="text-gray-400">Batch Size</div>
                <div className="text-gray-200">32</div>
              </div>
              <div className="space-y-2">
                <div className="text-gray-400">图像尺寸</div>
                <div className="text-gray-200">128 × 128</div>
              </div>
              <div className="space-y-2">
                <div className="text-gray-400">损失函数</div>
                <div className="text-gray-200">sparse_categorical_crossentropy</div>
              </div>
              <div className="space-y-2">
                <div className="text-gray-400">数据集</div>
                <div className="text-gray-200">sample_data/images</div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {experiments.map((exp) => (
              <ExperimentCard
                key={exp.id}
                experiment={exp}
                onStart={() => startExperiment(exp.id)}
                formatDuration={formatDuration}
                isRunning={currentRunning === exp.id}
                disabled={!!currentRunning && currentRunning !== exp.id}
              />
            ))}
          </div>

          <div className="mt-8 bg-black/30 backdrop-blur-xl border border-gray-700/50 rounded-xl p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">实验进度总览</h3>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                <span className="text-gray-300 text-sm">待开始: {experiments.filter(e => e.status === 'pending').length}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-gray-300 text-sm">运行中: {experiments.filter(e => e.status === 'running').length}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">已完成: {experiments.filter(e => e.status === 'completed').length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 实验卡片组件
const ExperimentCard: React.FC<{
  experiment: ExperimentConfig
  onStart: () => void
  formatDuration: (start: Date, end?: Date) => string
  isRunning: boolean
  disabled: boolean
}> = ({ experiment, onStart, formatDuration, isRunning, disabled }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (experiment.status === 'running') {
      const interval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + (100 / 100) // 10秒完成，每100ms增加1%
          return newProgress >= 100 ? 100 : newProgress
        })
      }, 100)

      return () => clearInterval(interval)
    } else if (experiment.status === 'completed') {
      setProgress(100)
    } else {
      setProgress(0)
    }
  }, [experiment.status])

  const getStatusColor = () => {
    switch (experiment.status) {
      case 'pending': return 'border-gray-600/50 bg-black/20'
      case 'running': return 'border-blue-400/60 shadow-lg shadow-blue-500/20 bg-blue-950/30'
      case 'completed': return 'border-green-400/60 shadow-lg shadow-green-500/20 bg-green-950/30'
      default: return 'border-gray-600/50 bg-black/20'
    }
  }

  const getStatusIcon = () => {
    switch (experiment.status) {
      case 'pending': return <Clock className="text-gray-400" size={20} />
      case 'running': return <Play className="text-blue-300 animate-pulse" size={20} />
      case 'completed': return <CheckCircle className="text-green-300" size={20} />
    }
  }

  return (
    <div className={`backdrop-blur-xl border ${getStatusColor()} rounded-xl p-6 transition-all duration-300 shadow-2xl`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="font-semibold text-gray-100">{experiment.id}</h3>
            <p className="text-sm text-gray-400">Epoch {experiment.epoch}</p>
          </div>
        </div>
        {experiment.status === 'pending' && (
          <button
            onClick={onStart}
            disabled={disabled}
            className="px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 disabled:bg-gray-600/20 disabled:cursor-not-allowed border border-blue-400/40 rounded-lg text-blue-300 disabled:text-gray-500 text-sm transition-all duration-200"
          >
            开始
          </button>
        )}
      </div>

      {/* 进度条 */}
      {experiment.status === 'running' && (
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>训练进度</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-700/50 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* 实验参数 */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">Epoch</span>
          <span className="text-gray-200">{experiment.epoch}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">状态</span>
          <span className={`
            ${experiment.status === 'pending' ? 'text-gray-400' : ''}
            ${experiment.status === 'running' ? 'text-blue-300' : ''}
            ${experiment.status === 'completed' ? 'text-green-300' : ''}
          `}>
            {experiment.status === 'pending' ? '待开始' : 
             experiment.status === 'running' ? '运行中' : '已完成'}
          </span>
        </div>
        {experiment.startTime && (
          <div className="flex justify-between">
            <span className="text-gray-400">耗时</span>
            <span className="text-gray-200">
              {formatDuration(experiment.startTime, experiment.completionTime)}
            </span>
          </div>
        )}
        {experiment.accuracy && (
          <div className="flex justify-between">
            <span className="text-gray-400">验证准确率</span>
            <span className="text-green-300 font-medium">{experiment.accuracy}%</span>
          </div>
        )}
      </div>

      {/* 运行动效 */}
      {experiment.status === 'running' && (
        <div className="mt-4 flex items-center gap-2 text-xs text-blue-300">
          <div className="flex gap-1">
            <div className="w-1 h-1 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-1 h-1 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-1 h-1 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span>正在训练模型...</span>
        </div>
      )}
    </div>
  )
}

export default SimulationExperiment