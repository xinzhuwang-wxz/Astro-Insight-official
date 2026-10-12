// src/lib/calendar-data.ts

export type EventItem = { title: string; time: string; category: string }
export type ApiEventItem = { month: number; day: number; title: string; time: string; category: string }
export type LegendItem = { icon: string; label: string; selected?: boolean }

export type CalendarMonthData = {
  calendarData: (number | null)[][]
  dayHeaders: string[]
  events: ApiEventItem[]
  legendItems: LegendItem[]
}

const calendarDataStore: { [month: string]: CalendarMonthData } = {
  '9': {
    calendarData: [
      [null, 1, 2, 3, 4, 5, 6],
      [7, 8, 9, 10, 11, 12, 13],
      [14, 15, 16, 17, 18, 19, 20],
      [21, 22, 23, 24, 25, 26, 27],
      [28, 29, 30, null, null, null, null]
    ],
    dayHeaders: ['日', '一', '二', '三', '四', '五', '六'],
    events: [
      { month: 9, day: 1, title: 'Aurigids 流星雨观测', time: '22:30 - 02:00', category: '流星雨' },
      { month: 9, day: 7, title: '丰收月圆观测', time: '20:00 - 23:00', category: '观测' },
      { month: 9, day: 7, title: '月偏食讨论会', time: '21:00 - 22:00', category: '会议' },
      { month: 9, day: 19, title: '土星掩星实验', time: '01:15 - 01:45', category: '实验' },
      { month: 9, day: 21, title: '新月观测准备', time: '全天', category: '新月' },
      { month: 9, day: 21, title: '日食观测中心协调', time: '09:00 - 11:00', category: '会议' },
      { month: 9, day: 21, title: '土星冲观测会', time: '22:00 - 23:30', category: '行星事件' },
      { month: 9, day: 22, title: '秋分时间测定实验', time: '00:00 - 02:00', category: '实验' },
      { month: 9, day: 24, title: 'ε-Perseids 峰值观测', time: '23:00 - 03:00', category: '观测' },
      { month: 9, day: 25, title: '星系分类实验：训练数据标注', time: '13:00 - 16:00', category: '实验' }
    ],
    legendItems: [
      { icon: '🔬', label: '实验', selected: true },
      { icon: '🧑‍🤝‍🧑', label: '会议', selected: true },
      { icon: '🌕', label: '满月', selected: false },
      { icon: '🌑', label: '新月', selected: false },
      { icon: '🌠', label: '流星雨', selected: false },
      { icon: '🌞', label: '日食/月食', selected: false },
      { icon: '🪐', label: '行星事件', selected: false },
      { icon: '🍂', label: '节气', selected: false }
    ]
  },
  '10': {
    calendarData: [
      [null, null, 1, 2, 3, 4, 5],
      [6, 7, 8, 9, 10, 11, 12],
      [13, 14, 15, 16, 17, 18, 19],
      [20, 21, 22, 23, 24, 25, 26],
      [27, 28, 29, 30, 31, null, null]
    ],
    dayHeaders: ['日', '一', '二', '三', '四', '五', '六'],
    events: [
      { month: 10, day: 3, title: '金星掩星观测', time: '19:30 - 20:10', category: '观测' },
      { month: 10, day: 10, title: '天文实验室：相位测定', time: '14:00 - 16:00', category: '实验' },
      { month: 10, day: 12, title: '星系分类实验：样本标注', time: '10:00 - 12:00', category: '实验' },
      { month: 10, day: 14, title: '观测者会议：夜间计划', time: '20:00 - 21:30', category: '会议' },
      { month: 10, day: 18, title: '彗星跟踪观测', time: '21:00 - 23:00', category: '观测' },
      { month: 10, day: 20, title: '系外行星凌日分析', time: '02:00 - 04:00', category: '实验' },
      { month: 10, day: 22, title: '银河中心深空拍摄排期', time: '23:00 - 03:00', category: '观测' },
      { month: 10, day: 25, title: '星系分类：模型评估会议', time: '15:00 - 16:30', category: '会议' },
      { month: 10, day: 29, title: '射电望远镜校准实验', time: '02:00 - 04:00', category: '实验' }
    ],
    legendItems: [
      { icon: '🔬', label: '实验', selected: true },
      { icon: '🧑‍🤝‍🧑', label: '会议', selected: true },
      { icon: '🌕', label: '满月', selected: false },
      { icon: '🌑', label: '新月', selected: false },
      { icon: '🌠', label: '流星雨', selected: false },
      { icon: '🌞', label: '日食/月食', selected: false },
      { icon: '🪐', label: '行星事件', selected: false },
      { icon: '🍂', label: '节气', selected: false }
    ]
  }
}

export function getCalendarData(month: number | string): CalendarMonthData | null {
  const monthKey = String(month)
  return calendarDataStore[monthKey] || null
}
