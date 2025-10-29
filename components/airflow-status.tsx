"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { mockAirflowDags } from "@/lib/mock-data"

export function AirflowStatus() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total DAGs</CardDescription>
            <CardTitle className="text-3xl">12</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Active pipelines</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>SLA Adherence</CardDescription>
            <CardTitle className="text-3xl text-chart-2">100%</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Avg Execution Time</CardDescription>
            <CardTitle className="text-3xl">4.2m</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Daily refresh</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>DAG Status</CardTitle>
          <CardDescription>Real-time pipeline monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockAirflowDags.map((dag, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        dag.status === "success"
                          ? "bg-chart-2"
                          : dag.status === "running"
                            ? "bg-chart-4"
                            : "bg-muted-foreground"
                      }`}
                    />
                    <div>
                      <h4 className="font-semibold">{dag.name}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{dag.description}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">{dag.lastRun}</p>
                    <p className="text-xs text-muted-foreground">Last run</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{dag.duration}</p>
                    <p className="text-xs text-muted-foreground">Duration</p>
                  </div>
                  <Badge variant={dag.status === "success" ? "default" : "secondary"}>{dag.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
