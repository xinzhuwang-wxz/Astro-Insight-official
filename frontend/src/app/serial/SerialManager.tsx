'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useSerial } from '@/hooks/useSerial';
import { Button } from '@/components/ui/button';

const SerialManager: React.FC = () => {
  const {
    ports,
    status,
    receivedMessages,
    sentMessages,
    loading,
    errors,
    notifications,
    refreshPorts,
    connect,
    disconnect,
    sendData,
    getStatus,
    autoDetectAndConnect,
    clearNotifications,
    clearErrors,
  } = useSerial();

  const [selectedPort, setSelectedPort] = useState('');
  const [sendMessage, setSendMessage] = useState('');
  const [filter, setFilter] = useState('');
  const recvEndRef = useRef<HTMLDivElement|null>(null);
  const sentEndRef = useRef<HTMLDivElement|null>(null);

  useEffect(() => { void getStatus(); }, [getStatus]);

  const handleConnect = async () => {
    if (!selectedPort) { alert('请选择一个串口'); return; }
    try { await connect(selectedPort); } catch (e) { console.error(e); }
  };
  const handleDisconnect = async () => { try { await disconnect(); } catch (e) { console.error(e); } };
  const handleSendData = async () => { if (!sendMessage.trim()) return; try { await sendData(sendMessage); setSendMessage(''); } catch (e) { console.error(e); } };
  const handleAutoConnect = async () => { try { await autoDetectAndConnect(); } catch (e) { console.error(e); } };
  const statusColor = status.connected ? 'text-emerald-300' : 'text-rose-400';
  const fmt = (t:number)=> new Date(t).toLocaleTimeString();
  const filteredReceived = receivedMessages.filter(m=>!filter||m.data.includes(filter)||m.message_type.includes(filter));
  const filteredSent = sentMessages.filter(m=>!filter||m.data.includes(filter)||m.message_type.includes(filter));
  useEffect(()=>{ recvEndRef.current?.scrollIntoView({behavior:'smooth'}); }, [filteredReceived.length]);
  useEffect(()=>{ sentEndRef.current?.scrollIntoView({behavior:'smooth'}); }, [filteredSent.length]);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="rounded-lg p-6 shadow-sm border" style={{background:'var(--surface)'}}>
        <h2 className="text-2xl font-semibold mb-1">串口通信管理</h2>
        <p className="text-sm text-muted-foreground">自动检测和管理串口连接，支持实时数据通信</p>
      </div>
      {(notifications.length>0||errors.length>0)&&(
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {notifications.length>0&&(
            <div className="rounded-lg p-4 border" style={{background:'var(--surface-alt)'}}>
              <div className="flex justify之间 items-center mb-2"><h3 className="text-sm font-medium">实时通知</h3><Button variant="ghost" size="sm" onClick={clearNotifications}>清除</Button></div>
              <div className="space-y-2 max-h-32 overflow-y-auto">{notifications.slice(0,5).map((n,i)=>(<div key={i} className="text-sm px-2 py-1 rounded bg-slate-800/50">{n}</div>))}</div>
            </div>)}
          {errors.length>0&&(
            <div className="rounded-lg p-4 border" style={{background:'var(--surface-alt)'}}>
              <div className="flex justify之间 items-center mb-2"><h3 className="text-sm font-medium text-destructive">错误信息</h3><Button variant="ghost" size="sm" onClick={clearErrors}>清除</Button></div>
              <div className="space-y-2 max-h-32 overflow-y-auto">{errors.slice(0,5).map((er,i)=>(<div key={i} className="text-sm px-2 py-1 rounded bg-rose-900/40 text-rose-300">{er}</div>))}</div>
            </div>)}
        </div>)}
      <div className="rounded-lg p-6 border" style={{background:'var(--panel)'}}>
        <h3 className="text-lg font-medium mb-4">连接状态</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded p-3 bg-slate-800/20 dark:bg-slate-800/40"><span className="text-sm text-muted-foreground">状态: </span><span className={statusColor}>{status.connected?'已连接':'未连接'}</span></div>
          {status.port&&<div className="rounded p-3 bg-slate-800/20 dark:bg-slate-800/40"><span className="text-sm text-muted-foreground">端口: </span><span className="font-mono">{status.port}</span></div>}
          {status.connected&&<div className="rounded p-3 bg-slate-800/20 dark:bg-slate-800/40"><span className="text-sm text-muted-foreground">发起方: </span><span className={status.is_first_sender?'text-blue-400':'text-purple-400'}>{status.is_first_sender?'是':'否'}</span></div>}
          <div className="md:col-span-3 rounded p-3 bg-slate-800/20 dark:bg-slate-800/40"><span className="text-sm text-muted-foreground">消息: </span><span>{status.message}</span></div>
        </div>
      </div>
      <div className="rounded-lg p-6 border" style={{background:'var(--panel)'}}>
        <h3 className="text-lg font-medium mb-4">连接控制</h3>
        {!status.connected? <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={()=>{void refreshPorts();}} disabled={loading}>{loading?'刷新中...':'刷新端口'}</Button>
            <Button variant="secondary" onClick={()=>{void handleAutoConnect();}} disabled={loading||ports.length===0}>{loading?'自动连接中...':'自动连接'}</Button>
          </div>
          <div>
            <label className="block text-sm mb-2">选择串口 ({ports.length} 个可用):</label>
            <select value={selectedPort} onChange={e=>setSelectedPort(e.target.value)} className="w-full p-2 rounded border border-input bg-transparent">
              <option value="">请选择串口</option>
              {ports.map(p=> <option key={p.port_name} value={p.port_name}>{p.port_name} - {p.port_type}</option>)}
            </select>
          </div>
          <div><Button onClick={()=>{void handleConnect();}} disabled={!selectedPort||loading}>{loading?'连接中...':'手动连接'}</Button></div>
        </div>
        : <Button variant="destructive" onClick={()=>{void handleDisconnect();}} disabled={loading}>{loading?'断开中...':'断开连接'}</Button>}
      </div>
      {status.connected&&<div className="rounded-lg p-6 border space-y-4" style={{background:'var(--panel)'}}>
        <h3 className="text-lg font-medium mb-2">发送数据</h3>
        <div className="flex gap-2">
          <input type="text" value={sendMessage} onChange={e=>setSendMessage(e.target.value)} placeholder="输入要发送的消息" className="flex-1 p-2 rounded border border-input bg-transparent" onKeyDown={e=>{if(e.key==='Enter'){void handleSendData();}}} />
          <Button onClick={()=>{void handleSendData();}}>发送</Button>
        </div>
        <div className="flex items-center gap-2 pt-2">
          <input type="text" value={filter} onChange={e=>setFilter(e.target.value)} placeholder="过滤 (类型或内容)" className="flex-1 p-2 rounded border border-input bg-transparent" />
          {filter && <Button size="sm" variant="ghost" onClick={()=>setFilter('')}>清除过滤</Button>}
        </div>
      </div>}
      {status.connected&&<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-lg p-6 border" style={{background:'var(--panel)'}}>
          <h3 className="text-lg font-medium mb-4 text-emerald-400">接收数据 ({filteredReceived.length}/{receivedMessages.length})</h3>
          <div className="rounded p-4 max-h-80 overflow-y-auto bg-slate-900/20 dark:bg-slate-900/40">
            {filteredReceived.length===0? <p className="text-center text-sm text-muted-foreground py-8">暂无数据</p>
            : <div className="space-y-2">{filteredReceived.slice(-50).map((m,i)=>(
              <div key={i} className="rounded p-3 border border-emerald-600/40 bg-emerald-600/5 hover:bg-emerald-600/10 transition-colors">
                <div className="flex justify之间 items-start mb-1"><span className="text-xs text-muted-foreground">{fmt(m.timestamp)}</span><span className="text-xs px-2 py-0.5 rounded bg-emerald-900/40 text-emerald-200">{m.message_type}</span></div>
                <div className="font-mono text-xs break-all leading-relaxed">{m.data}</div>
              </div>))}<div ref={recvEndRef} /></div>}
          </div>
        </div>
        <div className="rounded-lg p-6 border" style={{background:'var(--panel)'}}>
          <h3 className="text-lg font-medium mb-4 text-sky-400">发送数据 ({filteredSent.length}/{sentMessages.length})</h3>
          <div className="rounded p-4 max-h-80 overflow-y-auto bg-slate-900/20 dark:bg-slate-900/40">
            {filteredSent.length===0? <p className="text-center text-sm text-muted-foreground py-8">暂无数据</p>
            : <div className="space-y-2">{filteredSent.slice(-50).map((m,i)=>(
              <div key={i} className="rounded p-3 border border-sky-500/40 bg-sky-500/5 hover:bg-sky-500/10 transition-colors">
                <div className="flex justify之间 items-start mb-1"><span className="text-xs text-muted-foreground">{fmt(m.timestamp)}</span><span className="text-xs px-2 py-0.5 rounded bg-sky-900/40 text-sky-200">{m.message_type}</span></div>
                <div className="font-mono text-xs break-all leading-relaxed">{m.data}</div>
              </div>))}<div ref={sentEndRef} /></div>}
          </div>
        </div>
      </div>}
    </div>
  );
};

export default SerialManager;
