/**
 * Main Dashboard Page
 * CODE REVIEW EXERCISE: This file contains intentional issues including a race condition.
 */
'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, Activity } from 'lucide-react'

// ISSUE 3: Poor types - should have proper interfaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  // ISSUE 3: Poor types - using any
  const [status, setStatus] = useState<any>(null)
  const [logs, setLogs] = useState<any[]>([])
  const [results, setResults] = useState<any[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  // ISSUE 5: Race condition - multiple simultaneous fetches can cause state inconsistency
  const fetchData = async () => {
    // ISSUE 2: No error handling for fetch operations
    const statusRes = await fetch(`${API_URL}/status`)
    const statusData = await statusRes.json()
    setStatus(statusData)

    const logsRes = await fetch(`${API_URL}/logs`)
    const logsData = await logsRes.json()
    setLogs(logsData)
  }

  useEffect(() => {
    fetchData()
    // ISSUE 5: Race condition - interval can trigger multiple concurrent fetchData calls
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  // ISSUE 2: No error handling for file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsProcessing(true)

    const formData = new FormData()
    formData.append('file', file)

    // ISSUE 2: No error handling for fetch
    const response = await fetch(`${API_URL}/process`, {
      method: 'POST',
      body: formData,
    })

    const result = await response.json()
    
    // ISSUE 5: Race condition - updating results array without proper state management
    setResults([result, ...results])
    setIsProcessing(false)
    
    // Refresh data
    fetchData()
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Agent Document Processing</h1>
        <p className="text-muted-foreground">
          Multi-agent pipeline for document classification, extraction, and routing
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.active_tasks || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.completed_tasks || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upload Document</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={isProcessing}
              className="text-sm"
              accept=".txt"
            />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Agent Logs</CardTitle>
            <CardDescription>Real-time activity from all agents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {logs.map((log, idx) => (
                <div key={idx} className="text-sm border-l-2 border-primary pl-3 py-1">
                  <div className="flex justify-between">
                    <span className="font-medium">{log.agent}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-muted-foreground">{log.message}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Classification Results</CardTitle>
            <CardDescription>Recent document processing results</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.map((result, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium">
                        {result.classification?.category}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Confidence: {(result.classification?.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                    <span className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">
                      {result.status}
                    </span>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium mb-1">Routing:</div>
                    <div className="text-muted-foreground">
                      → {result.routing?.destination}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Agent Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {status?.agents && Object.entries(status.agents).map(([agent, agentStatus]) => (
              <div key={agent} className="flex items-center space-x-2">
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
                <span className="capitalize">{agent}: {agentStatus as string}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
