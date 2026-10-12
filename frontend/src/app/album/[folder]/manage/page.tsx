import React from 'react'

export default function ManagePage({ params }: { params: { folder: string } }) {
  const { folder } = params
  return (
    <div className="min-h-screen bg-[#05060b] text-white py-12">
      <div className="max-w-4xl mx-auto bg-[rgba(2,6,23,0.9)] rounded-xl p-8 shadow-md">
        <h2 className="text-2xl font-bold mb-4">{folder} - 图片管理</h2>
        <p className="mb-4 text-sm text-slate-300">这里可以实现批量重命名、标签优化等功能（占位）。</p>
        <div className="flex space-x-2">
          <button className="px-4 py-2 bg-sky-600 rounded">图片名字统一优化</button>
          <button className="px-4 py-2 bg-white/6 rounded">下载所有</button>
        </div>
      </div>
    </div>
  )
}
