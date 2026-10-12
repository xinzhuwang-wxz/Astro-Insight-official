"use client"
import React, { useState } from 'react'
import { ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Brain, Database, Settings, BarChart3, LineChart, Target } from 'lucide-react'

interface AnalysisReportProps {
  onBack: () => void
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ onBack }) => {
  const [activeSection, setActiveSection] = useState('overview')

  // 模拟的实验数据
  const epochData = [
    { epoch: 0, trainAcc: 0.53, valAcc: 0.40, trainLoss: 0.77, valLoss: 0.74 },
    { epoch: 1, trainAcc: 0.48, valAcc: 0.35, trainLoss: 0.65, valLoss: 0.68 },
    { epoch: 2, trainAcc: 0.83, valAcc: 0.80, trainLoss: 0.45, valLoss: 0.48 },
    { epoch: 3, trainAcc: 0.89, valAcc: 0.70, trainLoss: 0.30, valLoss: 0.52 },
    { epoch: 4, trainAcc: 0.92, valAcc: 0.73, trainLoss: 0.20, valLoss: 0.53 },
  ]

  const confusionMatrixData = [
    { epoch: 0, class1: { tp: 13, fn: 5 }, class2: { fp: 1, tn: 12 } },
    { epoch: 1, class1: { tp: 11, fn: 7 }, class2: { fp: 0, tn: 13 } },
    { epoch: 2, class1: { tp: 0, fn: 18 }, class2: { fp: 0, tn: 13 } },
    { epoch: 3, class1: { tp: 15, fn: 3 }, class2: { fp: 8, tn: 5 } },
    { epoch: 4, class1: { tp: 17, fn: 1 }, class2: { fp: 4, tn: 9 } },
  ]

  const renderNavigation = () => (
    <div className="flex flex-wrap gap-2 mb-8">
      {[
        { id: 'overview', label: '概述', icon: Target },
        { id: 'curves', label: '训练曲线分析', icon: LineChart },
        { id: 'confusion', label: '混淆矩阵分析', icon: BarChart3 },
        { id: 'recommendations', label: '优化建议', icon: Brain },
      ].map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => setActiveSection(id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 backdrop-blur-xl ${
            activeSection === id
              ? 'bg-cyan-500/30 border border-cyan-400/50 text-cyan-200 shadow-lg'
              : 'bg-black/30 border border-gray-700/50 text-gray-300 hover:bg-black/40'
          }`}
        >
          <Icon size={16} />
          {label}
        </button>
      ))}
    </div>
  )

  const renderOverview = () => (
    <div className="space-y-8">
      <div className="bg-black/40 backdrop-blur-xl border border-gray-700/50 rounded-xl p-8 shadow-2xl">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-200 to-cyan-200 bg-clip-text text-transparent mb-6">
          天文ZO2数据集分类模型训练结果分析报告
        </h2>
        <div className="prose prose-invert max-w-none">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-emerald-300 mb-4 flex items-center gap-2">
                <Database size={20} />
                实验概述
              </h3>
              <p className="text-gray-300 leading-relaxed">
                本报告对针对天文ZO2数据集的CNN分类模型训练结果进行深入分析。通过5个epoch的训练过程，
                我们观察到了明显的过拟合现象，并识别出了最佳训练停止点。
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                <AlertTriangle size={20} />
                关键发现
              </h3>
              <ul className="text-gray-300 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  严重过拟合：从Epoch 2开始出现
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-1">•</span>
                  最佳停止点：Epoch 2 (验证准确率80%)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">•</span>
                  分类偏差：不同epoch对类别的识别能力波动
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 性能指标卡片 */}
      <div className="grid md:grid-cols-4 gap-6">
        <MetricCard
          title="最佳验证准确率"
          value="80.0%"
          trend="up"
          description="Epoch 2 达成"
          icon={TrendingUp}
          color="emerald"
        />
        <MetricCard
          title="过拟合程度"
          value="严重"
          trend="down"
          description="验证损失上升"
          icon={AlertTriangle}
          color="red"
        />
        <MetricCard
          title="训练准确率"
          value="92.0%"
          trend="up"
          description="最终epoch"
          icon={BarChart3}
          color="blue"
        />
        <MetricCard
          title="建议停止点"
          value="Epoch 2"
          trend="stable"
          description="最佳泛化性能"
          icon={CheckCircle}
          color="cyan"
        />
      </div>
    </div>
  )

  const renderCurvesAnalysis = () => (
    <div className="space-y-8">
      <div className="bg-black/40 backdrop-blur-xl border border-gray-700/50 rounded-xl p-8 shadow-2xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-6 flex items-center gap-3">
          <LineChart className="text-blue-300" size={24} />
          训练和验证曲线分析
        </h2>
        
        {/* 训练曲线图表区域 */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-black/30 rounded-lg p-6 border border-gray-600/30">
            <h3 className="text-lg font-semibold text-gray-200 mb-4">准确率曲线</h3>
            <div className="h-64 bg-black/40 rounded-lg p-4 flex items-center justify-center border border-gray-700/30">
              <div className="w-full h-full relative">
                {/* 模拟图表 */}
                <svg viewBox="0 0 400 200" className="w-full h-full">
                  {/* 训练准确率曲线 (蓝色) */}
                  <polyline
                    points="0,160 80,170 160,80 240,60 320,40"
                    fill="none"
                    stroke="#60a5fa"
                    strokeWidth="3"
                    className="opacity-80"
                  />
                  {/* 验证准确率曲线 (绿色) */}
                  <polyline
                    points="0,180 80,190 160,100 240,120 320,110"
                    fill="none"
                    stroke="#34d399"
                    strokeWidth="3"
                    className="opacity-80"
                  />
                  {/* 标记点 */}
                  {epochData.map((data, i) => (
                    <g key={i}>
                      <circle cx={i * 80} cy={200 - data.trainAcc * 200} r="4" fill="#60a5fa" />
                      <circle cx={i * 80} cy={200 - data.valAcc * 200} r="4" fill="#34d399" />
                    </g>
                  ))}
                </svg>
                <div className="absolute bottom-2 left-2 text-xs">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-0.5 bg-blue-400"></div>
                      <span className="text-gray-400">训练准确率</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-0.5 bg-green-400"></div>
                      <span className="text-gray-400">验证准确率</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-black/30 rounded-lg p-6 border border-gray-600/30">
            <h3 className="text-lg font-semibold text-gray-200 mb-4">损失曲线</h3>
            <div className="h-64 bg-black/40 rounded-lg p-4 flex items-center justify-center border border-gray-700/30">
              <div className="w-full h-full relative">
                <svg viewBox="0 0 400 200" className="w-full h-full">
                  {/* 训练损失曲线 (红色) */}
                  <polyline
                    points="0,40 80,60 160,120 240,160 320,180"
                    fill="none"
                    stroke="#f87171"
                    strokeWidth="3"
                    className="opacity-80"
                  />
                  {/* 验证损失曲线 (紫色) */}
                  <polyline
                    points="0,50 80,70 160,110 240,120 320,110"
                    fill="none"
                    stroke="#a78bfa"
                    strokeWidth="3"
                    className="opacity-80"
                  />
                </svg>
                <div className="absolute bottom-2 left-2 text-xs">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-0.5 bg-red-400"></div>
                      <span className="text-gray-400">训练损失</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-0.5 bg-purple-400"></div>
                      <span className="text-gray-400">验证损失</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 阶段分析 */}
        <div className="grid md:grid-cols-3 gap-6">
          <AnalysisCard
            title="初期阶段 (Epoch 0-1)"
            status="learning"
            description="模型开始学习，准确率较低，存在欠拟合现象。训练和验证性能都在较低水平波动。"
            metrics={[
              { label: "训练准确率", value: "48-53%" },
              { label: "验证准确率", value: "35-40%" },
            ]}
          />
          <AnalysisCard
            title="最佳阶段 (Epoch 2)"
            status="optimal"
            description="模型达到最佳泛化性能，训练和验证准确率都较高且接近，是理想的停止点。"
            metrics={[
              { label: "训练准确率", value: "83%" },
              { label: "验证准确率", value: "80%" },
            ]}
          />
          <AnalysisCard
            title="过拟合阶段 (Epoch 3-4)"
            status="overfitting"
            description="严重过拟合，训练准确率持续上升，但验证准确率开始下降，泛化能力恶化。"
            metrics={[
              { label: "训练准确率", value: "89-92%" },
              { label: "验证准确率", value: "70-73%" },
            ]}
          />
        </div>
      </div>
    </div>
  )

  const renderConfusionAnalysis = () => (
    <div className="space-y-8">
      <div className="bg-black/40 backdrop-blur-xl border border-gray-700/50 rounded-xl p-8 shadow-2xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-6 flex items-center gap-3">
          <BarChart3 className="text-purple-300" size={24} />
          混淆矩阵分析
        </h2>
        
        <div className="grid lg:grid-cols-2 gap-8">
          {/* 不同epoch的混淆矩阵 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-200 mb-4">各Epoch混淆矩阵对比</h3>
            <div className="space-y-4">
              {confusionMatrixData.map((data, index) => (
                <div key={index} className="bg-black/30 rounded-lg p-4 border border-gray-600/30">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-200">Epoch {data.epoch}</h4>
                    <span className={`px-2 py-1 rounded text-xs ${
                      data.epoch === 2 ? 'bg-green-500/20 text-green-300 border border-green-400/30' :
                      data.epoch < 2 ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/30' :
                      'bg-red-500/20 text-red-300 border border-red-400/30'
                    }`}>
                      {data.epoch === 2 ? '最佳' : data.epoch < 2 ? '学习中' : '过拟合'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-green-500/10 border border-green-400/20 rounded p-2 text-center">
                      <div className="text-green-300 font-semibold">{data.class1.tp}</div>
                      <div className="text-gray-400 text-xs">Class1 正确</div>
                    </div>
                    <div className="bg-red-500/10 border border-red-400/20 rounded p-2 text-center">
                      <div className="text-red-300 font-semibold">{data.class1.fn}</div>
                      <div className="text-gray-400 text-xs">Class1 误判</div>
                    </div>
                    <div className="bg-red-500/10 border border-red-400/20 rounded p-2 text-center">
                      <div className="text-red-300 font-semibold">{data.class2.fp}</div>
                      <div className="text-gray-400 text-xs">Class2 误判</div>
                    </div>
                    <div className="bg-green-500/10 border border-green-400/20 rounded p-2 text-center">
                      <div className="text-green-300 font-semibold">{data.class2.tn}</div>
                      <div className="text-gray-400 text-xs">Class2 正确</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 分析总结 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-200 mb-4">关键发现</h3>
            <div className="space-y-4">
              <div className="bg-red-500/10 border border-red-400/30 rounded-lg p-4">
                <h4 className="font-semibold text-red-300 mb-2 flex items-center gap-2">
                  <AlertTriangle size={16} />
                  Epoch 2 异常
                </h4>
                <p className="text-gray-300 text-sm">
                  模型完全无法识别Class1，将其全部误分类为Class2。这与验证准确率上升趋势矛盾，
                  需要验证数据采集的一致性。
                </p>
              </div>
              
              <div className="bg-yellow-500/10 border border-yellow-400/30 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-300 mb-2 flex items-center gap-2">
                  <TrendingDown size={16} />
                  分类偏差
                </h4>
                <p className="text-gray-300 text-sm">
                  在不同epoch，模型对两个类别的识别能力存在显著波动，表明训练过程不够稳定。
                </p>
              </div>
              
              <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4">
                <h4 className="font-semibold text-blue-300 mb-2 flex items-center gap-2">
                  <BarChart3 size={16} />
                  性能评估
                </h4>
                <div className="space-y-2 text-sm text-gray-300">
                  <div className="flex justify-between">
                    <span>最佳精确率：</span>
                    <span className="text-green-300">Epoch 4 (Class1: 81%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>最佳召回率：</span>
                    <span className="text-green-300">Epoch 4 (Class1: 94%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>平衡性能：</span>
                    <span className="text-yellow-300">需要改进</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderRecommendations = () => (
    <div className="space-y-8">
      <div className="bg-black/40 backdrop-blur-xl border border-gray-700/50 rounded-xl p-8 shadow-2xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-6 flex items-center gap-3">
          <Brain className="text-cyan-300" size={24} />
          模型优化建议
        </h2>
        
        <div className="grid lg:grid-cols-2 gap-8">
          {/* 立即优化建议 */}
          <div>
            <h3 className="text-lg font-semibold text-emerald-300 mb-4 flex items-center gap-2">
              <CheckCircle size={18} />
              立即实施建议
            </h3>
            <div className="space-y-4">
              <RecommendationCard
                title="早期停止"
                priority="高"
                description="在Epoch 2处停止训练，避免过拟合，保持最佳泛化性能。"
                implementation="设置EarlyStopping回调，监控val_accuracy"
                color="green"
              />
              <RecommendationCard
                title="正则化技术"
                priority="高"
                description="添加Dropout层和L2正则化，减少过拟合风险。"
                implementation="在Dense层前添加Dropout(0.5)，kernel_regularizer=l2(0.001)"
                color="green"
              />
              <RecommendationCard
                title="学习率调度"
                priority="中"
                description="使用ReduceLROnPlateau动态调整学习率。"
                implementation="ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2)"
                color="yellow"
              />
            </div>
          </div>

          {/* 长期优化策略 */}
          <div>
            <h3 className="text-lg font-semibold text-blue-300 mb-4 flex items-center gap-2">
              <Settings size={18} />
              长期优化策略
            </h3>
            <div className="space-y-4">
              <RecommendationCard
                title="数据增强"
                priority="中"
                description="对天文图像进行旋转、翻转等数据增强，扩充训练集。"
                implementation="ImageDataGenerator with rotation, flip, zoom"
                color="blue"
              />
              <RecommendationCard
                title="交叉验证"
                priority="中"
                description="使用K折交叉验证评估模型稳定性。"
                implementation="StratifiedKFold(n_splits=5) 验证"
                color="blue"
              />
              <RecommendationCard
                title="集成学习"
                priority="低"
                description="训练多个模型并进行投票或平均，提高预测稳定性。"
                implementation="Voting Classifier 或 Model Averaging"
                color="purple"
              />
            </div>
          </div>
        </div>

        {/* 预期改进效果 */}
        <div className="mt-8 bg-black/30 rounded-lg p-6 border border-gray-600/30">
          <h3 className="text-lg font-semibold text-gray-200 mb-4">预期改进效果</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-300 mb-2">+15%</div>
              <div className="text-gray-400 text-sm">验证准确率提升</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-300 mb-2">-50%</div>
              <div className="text-gray-400 text-sm">过拟合程度降低</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-300 mb-2">+30%</div>
              <div className="text-gray-400 text-sm">模型稳定性提升</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

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
        <div className="absolute inset-0 bg-gradient-radial from-cyan-950/20 via-blue-950/10 to-transparent"></div>
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
          background: radial-gradient(1px 1px at 25px 35px, #fff, transparent),
                      radial-gradient(1px 1px at 45px 75px, #fff, transparent),
                      radial-gradient(1px 1px at 95px 45px, #fff, transparent),
                      radial-gradient(1px 1px at 135px 85px, #fff, transparent),
                      radial-gradient(1px 1px at 165px 35px, #fff, transparent);
          background-repeat: repeat;
          background-size: 220px 120px;
          animation: twinkle 5s ease-in-out infinite alternate;
          opacity: 0.9;
        }
        .stars-layer-2 {
          background: radial-gradient(1px 1px at 35px 55px, #06b6d4, transparent),
                      radial-gradient(1px 1px at 85px 25px, #8b5cf6, transparent),
                      radial-gradient(1px 1px at 125px 95px, #06b6d4, transparent);
          background-repeat: repeat;
          background-size: 280px 180px;
          animation: drift 90s linear infinite;
          opacity: 0.7;
        }
        .stars-layer-3 {
          background: radial-gradient(0.5px 0.5px at 18px 28px, #fff, transparent),
                      radial-gradient(0.5px 0.5px at 78px 68px, #fff, transparent),
                      radial-gradient(0.5px 0.5px at 118px 18px, #fff, transparent);
          background-repeat: repeat;
          background-size: 160px 90px;
          animation: sparkle 7s ease-in-out infinite;
          opacity: 0.5;
        }
        .floating-particles {
          background: radial-gradient(2px 2px at 120px 120px, rgba(6, 182, 212, 0.4), transparent),
                      radial-gradient(1.5px 1.5px at 320px 220px, rgba(139, 92, 246, 0.5), transparent),
                      radial-gradient(1px 1px at 220px 370px, rgba(6, 182, 212, 0.6), transparent);
          background-repeat: repeat;
          background-size: 450px 450px;
          animation: float 110s linear infinite;
          opacity: 0.4;
        }
        @keyframes twinkle {
          0%, 100% { opacity: 0.7; }
          50% { opacity: 1; }
        }
        @keyframes drift {
          from { background-position: 0 0; }
          to { background-position: -280px -180px; }
        }
        @keyframes sparkle {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 0.9; transform: scale(1.3); }
        }
        @keyframes float {
          from { background-position: 0 0; }
          to { background-position: -450px -450px; }
        }
      `}</style>

      <div className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 bg-black/40 hover:bg-black/60 rounded-lg backdrop-blur-xl border border-gray-700/50 text-gray-200 transition-all duration-200 shadow-2xl"
            >
              <ArrowLeft size={20} />
              返回实验
            </button>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl border border-cyan-400/30 shadow-2xl backdrop-blur-xl">
                <BarChart3 className="text-cyan-300" size={28} />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-200 via-blue-200 to-purple-200 bg-clip-text text-transparent">
                AstroZO2 模型分析报告
              </h1>
            </div>
          </div>

          {/* Navigation */}
          {renderNavigation()}

          {/* Content */}
          {activeSection === 'overview' && renderOverview()}
          {activeSection === 'curves' && renderCurvesAnalysis()}
          {activeSection === 'confusion' && renderConfusionAnalysis()}
          {activeSection === 'recommendations' && renderRecommendations()}
        </div>
      </div>
    </div>
  )
}

// 辅助组件
const MetricCard: React.FC<{
  title: string
  value: string
  trend: 'up' | 'down' | 'stable'
  description: string
  icon: React.ComponentType<{ size: number; className?: string }>
  color: 'emerald' | 'red' | 'blue' | 'cyan'
}> = ({ title, value, trend, description, icon: Icon, color }) => {
  const colorClasses = {
    emerald: 'from-emerald-500/20 to-green-500/20 border-emerald-400/30 text-emerald-300',
    red: 'from-red-500/20 to-pink-500/20 border-red-400/30 text-red-300',
    blue: 'from-blue-500/20 to-indigo-500/20 border-blue-400/30 text-blue-300',
    cyan: 'from-cyan-500/20 to-teal-500/20 border-cyan-400/30 text-cyan-300',
  }

  const trendIcons = {
    up: <TrendingUp size={16} className="text-green-400" />,
    down: <TrendingDown size={16} className="text-red-400" />,
    stable: <div className="w-4 h-4 rounded-full bg-yellow-400"></div>,
  }

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-xl border rounded-xl p-6 shadow-2xl`}>
      <div className="flex items-center justify-between mb-3">
        <Icon size={24} className="opacity-80" />
        {trendIcons[trend]}
      </div>
      <div className="text-2xl font-bold text-gray-100 mb-1">{value}</div>
      <div className="text-sm text-gray-300 mb-2">{title}</div>
      <div className="text-xs text-gray-400">{description}</div>
    </div>
  )
}

const AnalysisCard: React.FC<{
  title: string
  status: 'learning' | 'optimal' | 'overfitting'
  description: string
  metrics: Array<{ label: string; value: string }>
}> = ({ title, status, description, metrics }) => {
  const statusStyles = {
    learning: 'border-yellow-400/40 bg-yellow-500/10',
    optimal: 'border-green-400/40 bg-green-500/10',
    overfitting: 'border-red-400/40 bg-red-500/10',
  }

  const statusColors = {
    learning: 'text-yellow-300',
    optimal: 'text-green-300',
    overfitting: 'text-red-300',
  }

  return (
    <div className={`${statusStyles[status]} backdrop-blur-xl border rounded-lg p-6 shadow-2xl`}>
      <h4 className={`font-semibold ${statusColors[status]} mb-3`}>{title}</h4>
      <p className="text-gray-300 text-sm mb-4 leading-relaxed">{description}</p>
      <div className="space-y-2">
        {metrics.map((metric, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-gray-400">{metric.label}</span>
            <span className="text-gray-200 font-medium">{metric.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const RecommendationCard: React.FC<{
  title: string
  priority: string
  description: string
  implementation: string
  color: 'green' | 'yellow' | 'blue' | 'purple'
}> = ({ title, priority, description, implementation, color }) => {
  const colorClasses = {
    green: 'border-green-400/30 bg-green-500/10',
    yellow: 'border-yellow-400/30 bg-yellow-500/10',
    blue: 'border-blue-400/30 bg-blue-500/10',
    purple: 'border-purple-400/30 bg-purple-500/10',
  }

  const priorityColors = {
    高: 'bg-red-500/20 text-red-300 border-red-400/30',
    中: 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30',
    低: 'bg-gray-500/20 text-gray-300 border-gray-400/30',
  }

  return (
    <div className={`${colorClasses[color]} backdrop-blur-xl border rounded-lg p-4 shadow-2xl`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-200">{title}</h4>
        <span className={`px-2 py-1 rounded text-xs border ${priorityColors[priority as keyof typeof priorityColors]}`}>
          {priority}优先级
        </span>
      </div>
      <p className="text-gray-300 text-sm mb-3 leading-relaxed">{description}</p>
      <div className="bg-black/30 rounded p-3 border border-gray-600/30">
        <div className="text-xs text-gray-400 mb-1">实施方案:</div>
        <code className="text-xs text-cyan-300">{implementation}</code>
      </div>
    </div>
  )
}

export default AnalysisReport