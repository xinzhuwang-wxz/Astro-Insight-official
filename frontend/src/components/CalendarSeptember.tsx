"use client"
import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getCalendarData, ApiEventItem, EventItem, LegendItem } from '../lib/calendar-data'
import type { FC } from 'react'

// 扩展EventItem类型以支持美国天文事件的location字段
interface ExtendedEventItem extends EventItem {
  location?: string;
}

type EventsMap = { [day: number]: ExtendedEventItem[] }
// 无需 initialState，直接用 getCalendarData


const CalendarSeptember: FC = () => {
  const [month, setMonth] = useState<number>(9)
  // 直接同步获取数据
  const data = getCalendarData(month)
  // legendState 只在组件内本地管理
  const [legendState, setLegendState] = useState<LegendItem[] | null>(data ? data.legendItems.map(l => ({ ...l })) : null)
  // 美国天文事件数据状态
  const [usAstronomyEvents, setUsAstronomyEvents] = useState<any>(null)
  // 控制美国事件显示的状态
  const [showUSEvents, setShowUSEvents] = useState<boolean>(false)
  // 控制是否显示美国事件按钮（只有用户触发过查询才显示）
  const [showUSButton, setShowUSButton] = useState<boolean>(false)

  // 监听美国天文事件数据更新
  useEffect(() => {
    const handleUSAstronomyRefresh = (event: CustomEvent) => {
      const newData = event.detail;
      setUsAstronomyEvents(newData);
      setShowUSEvents(true); // 接收到数据时显示美国事件
      setShowUSButton(true); // 显示切换按钮
      console.log("CalendarSeptember: 接收到美国天文事件数据更新", newData);
    };

    // 注册事件监听器
    if (typeof window !== 'undefined') {
      window.addEventListener('refreshUSAstronomyData', handleUSAstronomyRefresh as EventListener);
      
      // 组件加载时检查是否已有缓存的美国天文事件数据
      const cachedData = localStorage.getItem('usAstronomyEvents');
      if (cachedData) {
        try {
          const parsedData = JSON.parse(cachedData);
          setUsAstronomyEvents(parsedData);
          // 注意：不设置 showUSEvents，保持默认隐藏状态
        } catch (error) {
          console.error("解析美国天文事件缓存数据失败:", error);
        }
      }
    }

    // 清理函数
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('refreshUSAstronomyData', handleUSAstronomyRefresh as EventListener);
      }
    };
  }, []);

  function currentMonthLabel() {
    return `${2025}年${month}月`
  }

  function changeMonth(delta: number) {
    setMonth((m) => {
      const next = m + delta
      if (next < 1) return 12
      if (next > 12) return 1
      return next
    })
  }

  const calendarData = data?.calendarData ?? []
  const dayHeaders = data?.dayHeaders ?? []
  // 构建 day->events map
  const events: EventsMap = {}
  if (data && Array.isArray(data.events)) {
    data.events.forEach((e) => {
      if (!events[e.day]) events[e.day] = []
      events[e.day].push({ title: e.title, time: e.time, category: e.category })
    })
  }

  // 合并美国天文事件数据（只有在显示状态为true时才合并）
  if (showUSEvents && usAstronomyEvents && Array.isArray(usAstronomyEvents.events)) {
    usAstronomyEvents.events.forEach((usEvent: any) => {
      // 将美国事件的日期错开显示，避免与现有事件冲突
      let targetDay = usEvent.day;
      
      // 如果目标日期已有事件，则向后偏移1-3天找空位
      let offset = 0;
      while (events[targetDay] && events[targetDay].length > 0 && offset < 10) {
        offset++;
        targetDay = usEvent.day + offset;
        if (targetDay > 31) {
          targetDay = usEvent.day - offset; // 如果超出月末，向前偏移
        }
        if (targetDay < 1) {
          targetDay = usEvent.day; // 如果小于1，回到原始日期
          break;
        }
      }
      
      if (!events[targetDay]) events[targetDay] = [];
      events[targetDay].push({
        title: `🇺🇸 ${usEvent.title}`,
        time: usEvent.time,
        category: usEvent.category,
        location: usEvent.location
      } as ExtendedEventItem);
      
      console.log(`美国事件已添加: ${usEvent.title} 原日期:${usEvent.day} 显示日期:${targetDay}`);
    });
  }
  const router = useRouter()

  function handleDateClick(day?: number | null) {
    if (!day) return
    const dayEvents = events[day] || []
    // 判定星系分类事件：category==='星系分类' OR title 包含关键词
    const titleHasGalaxy = dayEvents.some(ev => typeof ev.title === 'string' && ev.title.includes('星系分类'))
    const categoryHasGalaxy = dayEvents.some(ev => ev.category === '星系分类')
    const hasGalaxy = categoryHasGalaxy || titleHasGalaxy
    console.log('[Calendar] click day:', day, 'events:', dayEvents, 'categoryHasGalaxy:', categoryHasGalaxy, 'titleHasGalaxy:', titleHasGalaxy, 'hasGalaxy:', hasGalaxy)

    if (!hasGalaxy) return

    // choose the best event to carry its title into the album page
    const visibleEvents = dayEvents.filter(isEventVisible)
    // pick by priorityLabels order
    let chosen: ExtendedEventItem | null = null
    for (const label of priorityLabels) {
      const found = visibleEvents.find(ev => ev.category === label || (ev.title && ev.title.includes(label)))
      if (found) { chosen = found; break }
    }
    if (!chosen && visibleEvents.length > 0) chosen = visibleEvents[0]

    // map category to folder (extendable)
    const folderMap: { [k: string]: string } = { '星系分类': 'HB' }
    const folder = chosen ? (folderMap[chosen.category] || 'HB') : 'HB'
    const encodedTitle = chosen ? encodeURIComponent(chosen.title) : ''
    const target = `/album/${folder}?day=${day}${encodedTitle ? `&title=${encodedTitle}` : ''}`
    console.log('[Calendar] navigating to target:', target, 'chosen event:', chosen)

    // 优先使用 router.push；如果失败或不可用，尝试 window.location
    try {
      if (router && typeof router.push === 'function') {
        router.push(target)
        console.log('[Calendar] router.push called with', target)
        return
      }
    } catch (err) {
      console.error('[Calendar] router.push threw', err)
    }

    try {
      if (typeof window !== 'undefined') {
        window.location.href = target
        console.log('[Calendar] window.location.href set to', target)
      }
    } catch (e) {
      console.error('[Calendar] fallback navigation failed', e)
    }
  }
  const legendItems = legendState ?? (data?.legendItems ?? [])

  // helper: determine icon to show for a given date based on visible events and a priority list
  const priorityLabels = ['实验', '星系分类', '会议', '观测', '流星雨', '日食/月食', '行星事件', '满月', '新月', '节气']

  function getIconForDate(day?: number | null) {
    if (!day) return null
    const dayEvents = (events && events[day]) ? events[day].filter(isEventVisible) : []
    if (!dayEvents || dayEvents.length === 0) return null

  const categories = new Set(dayEvents.map((e: ExtendedEventItem) => e.category))
    for (const label of priorityLabels) {
      if (categories.has(label)) {
        const found = (legendItems || []).find((l) => l.label === label)
        if (found) return found.icon
      }
    }

    // fallback: try to map first event category to its legend icon
    const firstCat = dayEvents[0].category
    const found = (legendItems || []).find((l) => l.label === firstCat)
    return found ? found.icon : '•'
  }

  // derive set of selected categories
  const selectedCategories = new Set(legendItems.filter((l) => l.selected).map((l) => l.label))

  function isEventVisible(ev: ExtendedEventItem) {
    // if any legend selected, only show events whose category matches a selected legend label
    if (selectedCategories.size === 0) return true
    return selectedCategories.has(ev.category)
  }

  return (
    <div className="w-full flex items-center justify-center p-4">
      <div className="relative w-[95vw] max-w-7xl rounded-2xl overflow-hidden shadow-2xl" style={{ backgroundColor: 'rgba(2,6,23,0.9)' }}>
        <div className="relative z-10 p-6 sm:p-8 md:p-10 lg:p-12 flex flex-col">
          <div className="flex items-center justify-between mb-4 sm:mb-6">
            <div>
              <h2 className="text-white text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight">事件 — {currentMonthLabel()}</h2>
            </div>
            <div className="flex items-center space-x-2">
              <button className="px-3 py-1 bg-white/6 rounded" onClick={() => setMonth(m => m === 1 ? 12 : m - 1)}>上月</button>
              <button className="px-3 py-1 bg-white/6 rounded" onClick={() => setMonth(m => m === 12 ? 1 : m + 1)}>下月</button>
              {showUSButton && usAstronomyEvents && (
                <button 
                  className={`px-3 py-1 rounded text-xs ${showUSEvents ? 'bg-blue-600 text-white' : 'bg-white/6 text-slate-300'}`}
                  onClick={() => setShowUSEvents(!showUSEvents)}
                >
                  🇺🇸 美国事件
                </button>
              )}
            </div>
          </div>

          {/* Calendar grid responsive: use CSS grid with aspect ratio for cells */}
          <div className="w-full">
            {(Object.keys(events).length === 0) ? (
              <div className="w-full py-12 flex flex-col items-center justify-center text-slate-300">
                <div className="text-lg font-medium">本月无事件</div>
                <div className="mt-2 text-sm">试试切换到其他月份查看活动。</div>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-7 gap-2 mb-3">
                  {dayHeaders.map((d) => (
                    <div key={d} className="text-xs sm:text-sm text-slate-200 text-center font-semibold">
                      {d}
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-7 gap-4">
                  {calendarData.flat().map((date, idx) => {
                    const hasEvent = !!(date && events && events[date] && events[date].some(isEventVisible))
                    const icon = getIconForDate(date)
                    return (
                      <div
                        key={idx}
                        data-day={date ?? ''}
                        onClick={() => handleDateClick(date)}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleDateClick(date) }}
                        role={date ? 'button' : undefined}
                        tabIndex={date ? 0 : undefined}
                        className={`relative ${date ? 'cursor-pointer' : ''} bg-[linear-gradient(180deg,_rgba(255,255,255,0.02),_rgba(0,0,0,0.12))] border border-[rgba(255,255,255,0.03)] rounded-xl p-3 flex flex-col backdrop-blur-md transition-transform duration-150 hover:scale-[1.01] ${hasEvent ? 'ring-1 ring-sky-500/30' : ''}`}
                        style={{ minHeight: 130 }}
                      >
                        {date ? (
                          <>
                            <div className="flex justify-between items-start">
                              <div className="text-slate-200 text-sm font-semibold">{date}</div>
                            </div>

                            {/* per-cell icon (top-right) */}
                            {icon && (
                              <div className="absolute right-3 top-3 text-lg" title="事件类别">{icon}</div>
                            )}

                            <div className="mt-2 flex-1 overflow-auto text-slate-100 text-sm leading-snug" style={{ maxHeight: 84 }}>
                              {events[date] && (
                                <ul className="space-y-1">
                                  {events[date].filter((ev: ExtendedEventItem) => isEventVisible(ev)).map((ev: ExtendedEventItem, i: number) => (
                                    <li key={i} className="">
                                      <div className="font-medium">{ev.title}</div>
                                      <div className="text-xs text-slate-300">
                                        {ev.time} · {ev.category}
                                        {ev.location && <div className="text-xs text-blue-300 mt-1">📍 {ev.location}</div>}
                                      </div>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          </>
                        ) : (
                          <div className="text-transparent">-</div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </>
            )}
          </div>

          <div className="mt-4">
            <div className="grid grid-cols-4 gap-3">
              {legendItems.map((it, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      const copy = (legendItems || []).map((x) => x === it ? { ...x, selected: !x.selected } : x)
                      setLegendState(copy)
                    }}
                    className={`flex items-center space-x-2 text-sm p-2 rounded ${it.selected ? 'bg-white/6 text-white' : 'text-slate-300 hover:bg-white/3'}`}
                  >
                    <span className="text-lg">{it.icon}</span>
                    <span className={it.selected ? 'font-semibold' : ''}>{it.label}</span>
                    {it.selected && <span className="ml-2 text-xs text-sky-300">已选</span>}
                  </button>

                  {/* album link: map certain legend labels to folders (e.g., 星系分类 -> HB) */}
                  {it.label === '星系分类' && (
                    <Link href={`/album/HB`} className="text-slate-300 text-sm px-2 py-1 rounded hover:bg-white/3">相册</Link>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 text-center text-slate-200 text-sm">一起加入 Astro community，共创天文学 sci agent</div>
        </div>
      </div>
    </div>
  )
}

export default CalendarSeptember
