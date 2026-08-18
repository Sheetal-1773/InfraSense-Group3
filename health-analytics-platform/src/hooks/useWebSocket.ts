import { useEffect, useState, useCallback, useRef } from 'react'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

interface UseWebSocketOptions {
  url?: string
  channel?: string
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  reconnectInterval?: number
  enabled?: boolean
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    channel = 'health',
    onMessage,
    onConnect,
    onDisconnect,
    reconnectInterval = 5000,
    enabled = true
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [isStale, setIsStale] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const staleCheckIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const connect = useCallback(() => {
    if (!enabled) return

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const wsHost = apiUrl.replace(/^http/, '').replace(/^\/\//, '').replace(/:8000$/, ':8000')
    const wsUrl = `${wsProtocol}//${wsHost}/ws/${channel}`
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        setIsConnected(true)
        onConnect?.()
      }
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          setLastMessage(message)
          setLastUpdate(new Date())
          setIsStale(false)
          onMessage?.(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
      
      ws.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()
        
        if (enabled) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }, [channel, enabled, reconnectInterval, onConnect, onDisconnect, onMessage])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (staleCheckIntervalRef.current) {
      clearInterval(staleCheckIntervalRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  useEffect(() => {
    connect()
    
    staleCheckIntervalRef.current = setInterval(() => {
      if (lastUpdate) {
        const now = new Date()
        const diffSeconds = (now.getTime() - lastUpdate.getTime()) / 1000
        if (diffSeconds > 30) {
          setIsStale(true)
        }
      }
    }, 5000)
    
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    lastUpdate,
    isStale,
    sendMessage,
    connect,
    disconnect
  }
}

export function useLiveMetrics(componentId?: string, enabled = true) {
  const [metrics, setMetrics] = useState<Record<string, any>>({})
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [isStale, setIsStale] = useState(false)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'metrics_update') {
      const data = message.data
      
      if (!componentId || data.component_id === componentId) {
        setMetrics(prev => ({ ...prev, ...data.metrics }))
        setLastUpdate(new Date(data.timestamp))
        setIsStale(false)
      }
    }
    
    if (message.type === 'health_update') {
      const data = message.data
      if (!componentId || data.component_id === componentId) {
        setMetrics(prev => ({ 
          ...prev, 
          health_score: data.health_score,
          status: data.status 
        }))
        setLastUpdate(new Date(data.timestamp))
        setIsStale(false)
      }
    }
  }, [componentId])

  const { isConnected, lastMessage } = useWebSocket({
    channel: 'health',
    onMessage: handleMessage,
    enabled
  })

  useEffect(() => {
    const interval = setInterval(() => {
      if (lastUpdate) {
        const now = new Date()
        const diffSeconds = (now.getTime() - lastUpdate.getTime()) / 1000
        if (diffSeconds > 30) {
          setIsStale(true)
        }
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [lastUpdate])

  return {
    metrics,
    lastUpdate,
    isStale,
    isConnected,
    lastMessage
  }
}

export function useLiveAlerts() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'alert') {
      const alert = message.data
      setAlerts(prev => [alert, ...prev].slice(0, 50))
      setLastUpdate(new Date(message.timestamp))
    }
  }, [])

  const { isConnected } = useWebSocket({
    channel: 'alerts',
    onMessage: handleMessage,
    enabled: true
  })

  return {
    alerts,
    lastUpdate,
    isConnected
  }
}

export function useLivePredictions() {
  const [predictions, setPredictions] = useState<any[]>([])
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'prediction') {
      const prediction = message.data
      setPredictions(prev => {
        const existing = prev.findIndex(p => p.id === prediction.id)
        if (existing >= 0) {
          const updated = [...prev]
          updated[existing] = prediction
          return updated
        }
        return [prediction, ...prev].slice(0, 20)
      })
      setLastUpdate(new Date(message.timestamp))
    }
  }, [])

  const { isConnected } = useWebSocket({
    channel: 'predictions',
    onMessage: handleMessage,
    enabled: true
  })

  return {
    predictions,
    lastUpdate,
    isConnected
  }
}