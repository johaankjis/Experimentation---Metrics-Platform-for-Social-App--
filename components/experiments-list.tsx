"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { mockExperiments } from "@/lib/mock-data"

interface ExperimentsListProps {
  onSelectExperiment: (id: string) => void
}

export function ExperimentsList({ onSelectExperiment }: ExperimentsListProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockExperiments.map((experiment) => (
          <Card
            key={experiment.id}
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => onSelectExperiment(experiment.id)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{experiment.name}</CardTitle>
                  <CardDescription className="mt-1">{experiment.description}</CardDescription>
                </div>
                <Badge variant={experiment.status === "running" ? "default" : "secondary"}>{experiment.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Surface</span>
                  <span className="font-medium">{experiment.surface}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Users</span>
                  <span className="font-medium">{experiment.users.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="font-medium">{experiment.duration} days</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Primary Metric</span>
                  <span className="font-medium">{experiment.primaryMetric}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
