"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ExperimentsList } from "./experiments-list"
import { MetricsCatalog } from "./metrics-catalog"
import { AirflowStatus } from "./airflow-status"
import { ExperimentResults } from "./experiment-results"

export function ExperimentDashboard() {
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null)

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-sidebar">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-sidebar-foreground">ExpPlatform</h1>
          <p className="text-sm text-sidebar-foreground/60 mt-1">A/B Testing & Analytics</p>
        </div>

        <nav className="px-3 space-y-1">
          <a
            href="#experiments"
            className="flex items-center gap-3 px-3 py-2 rounded-lg bg-sidebar-accent text-sidebar-accent-foreground"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <span className="font-medium">Experiments</span>
          </a>
          <a
            href="#metrics"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span className="font-medium">Metrics Catalog</span>
          </a>
          <a
            href="#automation"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span className="font-medium">Automation</span>
          </a>
          <a
            href="#configuration"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="font-medium">Configuration</span>
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1">
        <header className="border-b border-border bg-card">
          <div className="flex items-center justify-between px-8 py-4">
            <div>
              <h2 className="text-2xl font-semibold text-card-foreground">Experimentation Dashboard</h2>
              <p className="text-sm text-muted-foreground mt-1">Monitor and analyze A/B tests in real-time</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 text-sm font-medium text-foreground hover:bg-accent rounded-lg">
                Documentation
              </button>
              <button className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg">
                New Experiment
              </button>
            </div>
          </div>
        </header>

        <div className="p-8">
          <Tabs defaultValue="experiments" className="w-full">
            <TabsList className="mb-6">
              <TabsTrigger value="experiments">Active Experiments</TabsTrigger>
              <TabsTrigger value="results">Results & Analysis</TabsTrigger>
              <TabsTrigger value="metrics">Metrics Catalog</TabsTrigger>
              <TabsTrigger value="automation">Automation Status</TabsTrigger>
            </TabsList>

            <TabsContent value="experiments">
              <ExperimentsList onSelectExperiment={setSelectedExperiment} />
            </TabsContent>

            <TabsContent value="results">
              <ExperimentResults experimentId={selectedExperiment} />
            </TabsContent>

            <TabsContent value="metrics">
              <MetricsCatalog />
            </TabsContent>

            <TabsContent value="automation">
              <AirflowStatus />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
