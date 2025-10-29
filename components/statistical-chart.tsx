"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

interface StatisticalChartProps {
  data: {
    control: { value: number; users: number }
    treatment: { value: number; users: number }
    uplift: number
    confidenceInterval: { lower: number; upper: number }
  }
}

export function StatisticalChart({ data }: StatisticalChartProps) {
  const chartData = [
    {
      group: "Control",
      value: data.control.value,
      fill: "hsl(var(--chart-3))",
    },
    {
      group: "Treatment",
      value: data.treatment.value,
      fill: "hsl(var(--chart-1))",
    },
  ]

  return (
    <ChartContainer
      config={{
        value: {
          label: "Conversion Rate",
          color: "hsl(var(--chart-1))",
        },
      }}
      className="h-[300px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="group" />
          <YAxis />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
