"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { StatisticalChart } from "./statistical-chart"
import { mockExperiments, mockResults } from "@/lib/mock-data"

interface ExperimentResultsProps {
  experimentId: string | null
}

export function ExperimentResults({ experimentId }: ExperimentResultsProps) {
  if (!experimentId) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Select an experiment to view results</p>
        </CardContent>
      </Card>
    )
  }

  const experiment = mockExperiments.find((e) => e.id === experimentId)
  const results = mockResults[experimentId]

  if (!experiment || !results) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">No results available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Experiment Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{experiment.name}</CardTitle>
              <CardDescription className="mt-2">{experiment.description}</CardDescription>
            </div>
            <Badge variant={results.significant ? "default" : "secondary"} className="text-sm">
              {results.significant ? "Statistically Significant" : "Not Significant"}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Control Group</CardDescription>
            <CardTitle className="text-3xl">{results.control.value.toFixed(2)}%</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{results.control.users.toLocaleString()} users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Treatment Group</CardDescription>
            <CardTitle className="text-3xl">{results.treatment.value.toFixed(2)}%</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{results.treatment.users.toLocaleString()} users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Uplift</CardDescription>
            <CardTitle className={`text-3xl ${results.uplift > 0 ? "text-chart-2" : "text-destructive"}`}>
              {results.uplift > 0 ? "+" : ""}
              {results.uplift.toFixed(2)}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">p-value: {results.pValue.toFixed(4)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Statistical Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Statistical Analysis</CardTitle>
          <CardDescription>Confidence intervals and distribution</CardDescription>
        </CardHeader>
        <CardContent>
          <StatisticalChart data={results} />
        </CardContent>
      </Card>

      {/* Guardrail Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Guardrail Metrics</CardTitle>
          <CardDescription>Monitoring for negative impacts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {results.guardrails.map((guardrail, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div>
                  <p className="font-medium">{guardrail.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">{guardrail.description}</p>
                </div>
                <div className="text-right">
                  <Badge variant={guardrail.status === "healthy" ? "default" : "destructive"}>{guardrail.status}</Badge>
                  <p className="text-sm text-muted-foreground mt-1">
                    {guardrail.change > 0 ? "+" : ""}
                    {guardrail.change.toFixed(2)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
