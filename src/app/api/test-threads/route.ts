import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    console.log('Testing Threads API connection...')
    
    const body = await request.json()
    const { username, password } = body
    
    if (!username || !password) {
      return NextResponse.json({
        success: false,
        error: 'Username and password are required'
      })
    }
    
    console.log('Testing login for username:', username)
    
    // For now, we'll simulate the API test since the Python backend isn't connected
    // In a real implementation, this would call the Python Threads API
    
    // Simulate API response
    const mockResponse = {
      success: true,
      message: 'Threads API test successful (simulated)',
      account: {
        username: username,
        status: 'connected',
        followers_count: 0,
        last_posted: null
      },
      api_status: {
        base_url: 'https://www.threads.net/api/v1',
        rate_limit_remaining: 100,
        rate_limit_reset: new Date(Date.now() + 3600000).toISOString()
      }
    }
    
    console.log('Threads API test response:', mockResponse)
    
    return NextResponse.json(mockResponse)
    
  } catch (error) {
    console.error('Threads API test error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'Threads API test failed'
    })
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log('Getting Threads API status...')
    
    // Return API configuration and status
    const apiStatus = {
      success: true,
      message: 'Threads API status check',
      api_config: {
        base_url: 'https://www.threads.net/api/v1',
        max_retries: 3,
        retry_delay_base: 2.0,
        rate_limit_delay: 1.0,
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      },
      features: {
        login: true,
        post_text: true,
        post_with_image: true,
        rate_limiting: true,
        human_like_behavior: true,
        retry_logic: true
      },
      status: 'ready'
    }
    
    return NextResponse.json(apiStatus)
    
  } catch (error) {
    console.error('Threads API status error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 