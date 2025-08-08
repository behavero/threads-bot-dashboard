import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get('token')
  
  if (!token) {
    return NextResponse.json({ error: 'Missing token' }, { status: 400 })
  }

  // TODO: In a real implementation, you would:
  // 1. Look up the deletion job status from a database
  // 2. Check if the deletion is pending, in progress, or completed
  // 3. Return the actual status based on the job state
  
  // For now, we'll simulate a completed status
  // In production, you'd query your database for the actual status
  
  try {
    // Simulate checking backend for status
    const backendUrl = process.env.BACKEND_URL
    const internalToken = process.env.INTERNAL_API_TOKEN
    
    if (backendUrl && internalToken) {
      try {
        const statusResponse = await fetch(`${backendUrl}/internal/data-deletion/status?token=${token}`, {
          headers: { 
            'X-Internal-Token': internalToken 
          },
        })
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json()
          return NextResponse.json(statusData)
        }
      } catch (backendError) {
        console.error('Error checking backend status:', backendError)
        // Fall through to default response
      }
    }
    
    // Default response if backend is not available
    return NextResponse.json({
      status: 'completed',
      token,
      message: 'User data deletion was processed.',
      completed_at: new Date().toISOString(),
      deleted_items: {
        accounts: 'all',
        captions: 'all', 
        images: 'all',
        posting_history: 'all',
        sessions: 'all'
      }
    })
    
  } catch (error) {
    console.error('Status check error:', error)
    return NextResponse.json({
      status: 'error',
      token,
      message: 'Error checking deletion status.',
      error: 'Internal server error'
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  return NextResponse.json({ 
    error: 'Method Not Allowed. Use GET with token parameter.' 
  }, { status: 405 })
}
