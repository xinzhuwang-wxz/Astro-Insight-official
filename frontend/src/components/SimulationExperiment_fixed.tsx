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
    if (currentRunning) return

    setCurrentRunning(id)
    setExperiments(prev => 
      prev.map(exp => 
        exp.id === id 
          ? { ...exp, status: 'running', startTime: new Date() }
          : exp
      )
    )

    setTimeout(() => {
      const accuracy = Math.round((85 + Math.random() * 10) * 100) / 100
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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 p-6 relative overflow-hidden">
      <div className="absolute inset-0 opacity-30">
        <div className="stars"></div>
        <div className="twinkling"></div>
      </div>
      <style jsx>{`
        .stars, .twinkling {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
        }
        .stars {
          background: url('data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="0.5" fill="white" opacity="0.8"/><circle cx="80" cy="40" r="0.3" fill="white" opacity="0.6"/><circle cx="40" cy="70" r="0.4" fill="white" opacity="0.7"/><circle cx="90" cy="80" r="0.2" fill="white" opacity="0.5"/><circle cx="10" cy="90" r="0.3" fill="white" opacity="0.6"/></svg>') repeat;
          background-size: 200px 200px;
        }
        .twinkling {
          background: url('data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="30" cy="30" r="0.2" fill="cyan" opacity="0.8"/><circle cx="70" cy="60" r="0.1" fill="purple" opacity="0.6"/><circle cx="50" cy="10" r="0.15" fill="blue" opacity="0.7"/></svg>') repeat;
          background-size: 300px 300px;
          animation: move-twink-back 200s linear infinite;
        }
        @keyframes move-twink-back {
          from { background-position: 0 0; }
          to { background-position: -300px -300px; }
        }
      `}</style>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800/60 hover:bg-slate-700/60 rounded-lg backdrop-blur-md border border-slate-600/30 text-slate-200 transition-all duration-200 shadow-lg"
            >
              <ArrowLeft size={20} />
              返回相册
            </button>
            <button
              onClick={() => setShowAnalysisReport(true)}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 hover:bg-cyan-400/30 rounded-lg backdrop-blur-md border border-cyan-400/30 text-cyan-200 transition-all duration-200 shadow-lg"
            >
              <BarChart3 size={20} />
              查看分析报告
            </button>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl border border-blue-400/30 shadow-lg">
              <BarChart3 className="text-blue-300" size={28} />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-200 via-purple-200 to-cyan-200 bg-clip-text text-transparent">
              天体图像分类模型 - Epoch优化实验
            </h1>
          </div>
        </div>

        <div className="bg-slate-900/40 backdrop-blur-md border border-slate-700/50 rounded-xl p-6 mb-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Target className="text-emerald-300" size={24} />
            <h2 className="text-xl font-semibold text-slate-100">实验目标</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-emerald-300 mb-2">研究问题</h3>
              <p className="text-slate-300 leading-relaxed">
                探究训练epoch数量对CNN模型在天体图像分类任务中准确率的影响，寻找最优的训练轮次配置。
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-blue-300 mb-2">实验设计</h3>
              <div className="space-y-2 text-sm text-slate-300">
                <div><span className="text-yellow-300">自变量：</span> Epoch数量 (2, 3, 4, 5, 6)</div>
                <div><span className="text-green-300">因变量：</span> 模型验证准确率 (%)</div>
                <div><span className="text-purple-300">控制变量：</span> 模型架构、数据集、优化器、batch_size</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/40 backdrop-blur-md border border-slate-700/50 rounded-xl p-6 mb-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="text-purple-300" size={24} />
            <h2 className="text-xl font-semibold text-slate-100">控制变量配置</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="space-y-2">
              <div className="text-slate-400">模型架构</div>
              <div className="text-slate-200">CNN (Conv2D + MaxPooling2D)</div>
            </div>
            <div className="space-y-2">
              <div className="text-slate-400">优化器</div>
              <div className="text-slate-200">Adam</div>
            </div>
            <div className="space-y-2">
              <div className="text-slate-400">Batch Size</div>
              <div className="text-slate-200">32</div>
            </div>
            <div className="space-y-2">
              <div className="text-slate-400">图像尺寸</div>
              <div className="text-slate-200">128 × 128</div>
            </div>
            <div className="space-y-2">
              <div className="text-slate-400">损失函数</div>
              <div className="text-slate-200">sparse_categorical_crossentropy</div>
            </div>
            <div className="space-y-2">
              <div className="text-slate-400">数据集</div>
              <div className="text-slate-200">sample_data/images</div>
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

        <div className="mt-8 bg-slate-900/40 backdrop-blur-md border border-slate-700/50 rounded-xl p-6 shadow-2xl">
          <h3 className="text-lg font-semibold text-slate-100 mb-4">实验进度总览</h3>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-slate-500 rounded-full"></div>
              <span className="text-slate-300 text-sm">待开始: {experiments.filter(e => e.status === 'pending').length}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
              <span className="text-slate-300 text-sm">运行中: {experiments.filter(e => e.status === 'running').length}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-slate-300 text-sm">已完成: {experiments.filter(e => e.status === 'completed').length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

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
          const newProgress = prev + (100 / 100)
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
      case 'pending': return 'border-slate-600/50 bg-slate-800/30'
      case 'running': return 'border-blue-400/60 shadow-lg shadow-blue-500/20 bg-blue-900/20'
      case 'completed': return 'border-green-400/60 shadow-lg shadow-green-500/20 bg-green-900/20'
      default: return 'border-slate-600/50 bg-slate-800/30'
    }
  }

  const getStatusIcon = () => {
    switch (experiment.status) {
      case 'pending': return <Clock className="text-slate-400" size={20} />
      case 'running': return <Play className="text-blue-300 animate-pulse" size={20} />
      case 'completed': return <CheckCircle className="text-green-300" size={20} />
    }
  }

  return (
    <div className={`backdrop-blur-md border ${getStatusColor()} rounded-xl p-6 transition-all duration-300 shadow-xl`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="font-semibold text-slate-100">{experiment.id}</h3>
            <p className="text-sm text-slate-400">Epoch {experiment.epoch}</p>
          </div>
        </div>
        {experiment.status === 'pending' && (
          <button
            onClick={onStart}
            disabled={disabled}
            className="px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 disabled:bg-slate-600/20 disabled:cursor-not-allowed border border-blue-400/40 rounded-lg text-blue-300 disabled:text-slate-500 text-sm transition-all duration-200"
          >
            开始
          </button>
        )}
      </div>

      {experiment.status === 'running' && (
        <div className="mb-4">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>训练进度</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-700/50 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Epoch</span>
          <span className="text-slate-200">{experiment.epoch}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">状态</span>
          <span className={`
            ${experiment.status === 'pending' ? 'text-slate-400' : ''}
            ${experiment.status === 'running' ? 'text-blue-300' : ''}
            ${experiment.status === 'completed' ? 'text-green-300' : ''}
          `}>
            {experiment.status === 'pending' ? '待开始' : 
             experiment.status === 'running' ? '运行中' : '已完成'}
          </span>
        </div>
        {experiment.startTime && (
          <div className="flex justify-between">
            <span className="text-slate-400">耗时</span>
            <span className="text-slate-200">
              {formatDuration(experiment.startTime, experiment.completionTime)}
            </span>
          </div>
        )}
        {experiment.accuracy && (
          <div className="flex justify-between">
            <span className="text-slate-400">验证准确率</span>
            <span className="text-green-300 font-medium">{experiment.accuracy}%</span>
          </div>
        )}
      </div>

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