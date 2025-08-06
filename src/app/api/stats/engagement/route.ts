import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const days = searchParams.get('days') || '7'

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://threads-bot-dashboard-3.onrender.com'
    const response = await fetch(`${backendUrl}/api/stats/engagement?days=${days}`)

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Error fetching engagement stats:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch engagement data',
        data: []
      },
      { status: 500 }
    )
  }
} 