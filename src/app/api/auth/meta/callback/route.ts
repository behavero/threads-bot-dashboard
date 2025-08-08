import { NextRequest, NextResponse } from 'next/server'
import { API_ENDPOINTS } from '@/lib/config'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const error = searchParams.get('error')
    
    if (error) {
      console.error('OAuth error:', error)
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?error=oauth_denied`
      )
    }
    
    if (!code || !state) {
      console.error('Missing code or state in OAuth callback')
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?error=oauth_invalid`
      )
    }
    
    // Parse state to get account_id
    const accountId = state
    
    console.log(`OAuth callback received for account ${accountId}`)
    
    // Call backend to exchange code for tokens
    const response = await fetch(API_ENDPOINTS.AUTH_CALLBACK, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        account_id: accountId,
      }),
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      console.error('Backend OAuth callback error:', errorData)
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?error=backend_oauth_failed`
      )
    }
    
    const data = await response.json()
    
    if (data.ok) {
      console.log(`OAuth successful for account ${accountId}`)
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?success=oauth_completed&account_id=${accountId}`
      )
    } else {
      console.error('OAuth failed:', data.error)
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?error=oauth_failed&message=${encodeURIComponent(data.error)}`
      )
    }
    
  } catch (error) {
    console.error('OAuth callback error:', error)
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_BASE_URL}/accounts?error=oauth_exception`
    )
  }
}
