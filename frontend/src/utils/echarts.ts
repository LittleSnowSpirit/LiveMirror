/**
 * ECharts 模块化注册文件
 * 只引入使用的图表类型和组件，实现 tree-shaking
 */
import * as echarts from 'echarts/core'

// 图表类型
import { BarChart } from 'echarts/charts'
import { LineChart } from 'echarts/charts'
import { PieChart } from 'echarts/charts'
import { RadarChart } from 'echarts/charts'
import { ScatterChart } from 'echarts/charts'
import { GraphChart } from 'echarts/charts'

// 组件
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent
} from 'echarts/components'

// 渲染器
import { CanvasRenderer } from 'echarts/renderers'

// 注册
echarts.use([
  // 图表
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  ScatterChart,
  GraphChart,
  // 组件
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent,
  // 渲染器
  CanvasRenderer
])

export default echarts
