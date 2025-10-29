export const mockExperiments = [
  {
    id: "exp-001",
    name: "Feed Algorithm V2",
    description: "Testing new recommendation algorithm for user feed",
    status: "running",
    surface: "Feed",
    users: 50000,
    duration: 14,
    primaryMetric: "Session Length",
    startDate: "2025-01-15",
  },
  {
    id: "exp-002",
    name: "Notification Timing",
    description: "Optimizing push notification delivery times",
    status: "running",
    surface: "Notifications",
    users: 75000,
    duration: 7,
    primaryMetric: "Engagement Rate",
    startDate: "2025-01-20",
  },
  {
    id: "exp-003",
    name: "Messaging UI Redesign",
    description: "New chat interface with improved UX",
    status: "completed",
    surface: "Messaging",
    users: 30000,
    duration: 21,
    primaryMetric: "Message Send Rate",
    startDate: "2025-01-01",
  },
  {
    id: "exp-004",
    name: "Onboarding Flow V3",
    description: "Simplified onboarding with fewer steps",
    status: "running",
    surface: "Onboarding",
    users: 25000,
    duration: 10,
    primaryMetric: "Completion Rate",
    startDate: "2025-01-18",
  },
  {
    id: "exp-005",
    name: "Search Autocomplete",
    description: "AI-powered search suggestions",
    status: "draft",
    surface: "Search",
    users: 0,
    duration: 14,
    primaryMetric: "Search Success Rate",
    startDate: "2025-02-01",
  },
  {
    id: "exp-006",
    name: "Profile Customization",
    description: "Enhanced profile editing capabilities",
    status: "running",
    surface: "Profile",
    users: 40000,
    duration: 14,
    primaryMetric: "Profile Completion",
    startDate: "2025-01-16",
  },
]

export const mockResults: Record<
  string,
  {
    control: { value: number; users: number }
    treatment: { value: number; users: number }
    uplift: number
    pValue: number
    significant: boolean
    confidenceInterval: { lower: number; upper: number }
    guardrails: Array<{
      name: string
      description: string
      status: "healthy" | "warning" | "critical"
      change: number
    }>
  }
> = {
  "exp-001": {
    control: { value: 12.4, users: 25000 },
    treatment: { value: 14.8, users: 25000 },
    uplift: 19.35,
    pValue: 0.0023,
    significant: true,
    confidenceInterval: { lower: 14.2, upper: 15.4 },
    guardrails: [
      {
        name: "Crash Rate",
        description: "App crash frequency",
        status: "healthy",
        change: -0.2,
      },
      {
        name: "API Latency",
        description: "Average response time",
        status: "healthy",
        change: 1.5,
      },
      {
        name: "DAU",
        description: "Daily active users",
        status: "healthy",
        change: 2.1,
      },
    ],
  },
  "exp-002": {
    control: { value: 8.2, users: 37500 },
    treatment: { value: 11.6, users: 37500 },
    uplift: 41.46,
    pValue: 0.0001,
    significant: true,
    confidenceInterval: { lower: 11.1, upper: 12.1 },
    guardrails: [
      {
        name: "Unsubscribe Rate",
        description: "Notification opt-out rate",
        status: "healthy",
        change: -1.2,
      },
      {
        name: "Session Length",
        description: "Average session duration",
        status: "healthy",
        change: 5.3,
      },
      {
        name: "Retention D7",
        description: "7-day retention rate",
        status: "healthy",
        change: 3.8,
      },
    ],
  },
  "exp-003": {
    control: { value: 45.3, users: 15000 },
    treatment: { value: 52.1, users: 15000 },
    uplift: 15.01,
    pValue: 0.0156,
    significant: true,
    confidenceInterval: { lower: 50.8, upper: 53.4 },
    guardrails: [
      {
        name: "Message Delivery",
        description: "Successful message delivery rate",
        status: "healthy",
        change: 0.3,
      },
      {
        name: "Load Time",
        description: "Chat interface load time",
        status: "healthy",
        change: -8.5,
      },
      {
        name: "Error Rate",
        description: "Message send errors",
        status: "healthy",
        change: -2.1,
      },
    ],
  },
}

export const mockMetrics = {
  northStar: [
    {
      name: "Daily Active Users (DAU)",
      category: "Engagement",
      description: "Number of unique users who open the app daily",
      calculation: "COUNT(DISTINCT user_id) WHERE last_active_date = CURRENT_DATE",
      currentValue: "2.4M",
    },
    {
      name: "Session Length",
      category: "Engagement",
      description: "Average time users spend in the app per session",
      calculation: "AVG(session_end_time - session_start_time)",
      currentValue: "12.3 min",
    },
    {
      name: "D7 Retention",
      category: "Retention",
      description: "Percentage of users who return after 7 days",
      calculation: "(Users active on D7 / Users active on D0) * 100",
      currentValue: "42.5%",
    },
    {
      name: "Content Creation Rate",
      category: "Engagement",
      description: "Average posts/messages created per user per day",
      calculation: "COUNT(content_created) / COUNT(DISTINCT user_id)",
      currentValue: "3.8",
    },
  ],
  guardrails: [
    {
      name: "Crash Rate",
      category: "Performance",
      description: "Percentage of sessions that end in a crash",
      calculation: "(Crashed sessions / Total sessions) * 100",
      currentValue: "0.12%",
    },
    {
      name: "API Latency P95",
      category: "Performance",
      description: "95th percentile API response time",
      calculation: "PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time)",
      currentValue: "245ms",
    },
    {
      name: "Error Rate",
      category: "Reliability",
      description: "Percentage of failed API requests",
      calculation: "(Failed requests / Total requests) * 100",
      currentValue: "0.08%",
    },
    {
      name: "Engagement Drop",
      category: "Engagement",
      description: "Week-over-week decrease in key engagement metrics",
      calculation: "((Current week - Previous week) / Previous week) * 100",
      currentValue: "-1.2%",
    },
  ],
}

export const mockAirflowDags = [
  {
    name: "experiment_ingest_dag",
    description: "Daily ingestion of experiment assignment data",
    status: "success",
    lastRun: "2 hours ago",
    duration: "3.2m",
    schedule: "0 2 * * *",
  },
  {
    name: "transform_metrics_dag",
    description: "Transform raw events into analysis-ready metrics",
    status: "success",
    lastRun: "1 hour ago",
    duration: "5.8m",
    schedule: "0 3 * * *",
  },
  {
    name: "reporting_dag",
    description: "Generate daily experiment reports and dashboards",
    status: "running",
    lastRun: "15 min ago",
    duration: "2.1m",
    schedule: "0 4 * * *",
  },
  {
    name: "metrics_aggregation_dag",
    description: "Aggregate user-level metrics for analysis",
    status: "success",
    lastRun: "3 hours ago",
    duration: "4.5m",
    schedule: "0 1 * * *",
  },
  {
    name: "guardrail_monitoring_dag",
    description: "Monitor guardrail metrics and send alerts",
    status: "success",
    lastRun: "30 min ago",
    duration: "1.8m",
    schedule: "*/30 * * * *",
  },
]
