import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  console.log('GET /api/test-simple called')
  
  return NextResponse.json({
    success: true,
    message: 'Simple API route working',
    timestamp: new Date().toISOString()
  })
}

export async function POST(request: NextRequest) {
  console.log('POST /api/test-simple called')
  
  const body = await request.json()
  
  return NextResponse.json({
    success: true,
    message: 'Simple POST route working',
    received: body,
    timestamp: new Date().toISOString()
  })
}
