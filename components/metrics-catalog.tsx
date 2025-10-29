"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { mockMetrics } from "@/lib/mock-data"

export function MetricsCatalog() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>North Star Metrics</CardTitle>
          <CardDescription>Primary metrics that drive product decisions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockMetrics.northStar.map((metric, index) => (
              <div key={index} className="flex items-start justify-between p-4 border border-border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{metric.name}</h4>
                    <Badge variant="outline">{metric.category}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{metric.description}</p>
                  <p className="text-xs text-muted-foreground mt-2 font-mono bg-muted px-2 py-1 rounded inline-block">
                    {metric.calculation}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <p className="text-2xl font-bold">{metric.currentValue}</p>
                  <p className="text-sm text-muted-foreground">Current</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Guardrail Metrics</CardTitle>
          <CardDescription>Metrics to monitor for negative impacts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockMetrics.guardrails.map((metric, index) => (
              <div key={index} className="flex items-start justify-between p-4 border border-border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{metric.name}</h4>
                    <Badge variant="outline">{metric.category}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{metric.description}</p>
                  <p className="text-xs text-muted-foreground mt-2 font-mono bg-muted px-2 py-1 rounded inline-block">
                    {metric.calculation}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <p className="text-2xl font-bold">{metric.currentValue}</p>
                  <p className="text-sm text-muted-foreground">Current</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
