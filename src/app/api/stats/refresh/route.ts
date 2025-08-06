import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://threads-bot-dashboard-3.onrender.com'
    const response = await fetch(`${backendUrl}/api/stats/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Error refreshing engagement data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to refresh engagement data'
      },
      { status: 500 }
    )
  }
} 