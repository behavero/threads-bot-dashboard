import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

// Status store could be DB; for demo we'll compute a URL based on a token (user_id or job id)
function buildStatusUrl(host: string, token: string) {
  return `https://${host}/api/data-deletion/status?token=${encodeURIComponent(token)}`
}

function parseSignedRequest(signedRequest: string, appSecret: string) {
  const [encodedSig, payload] = signedRequest.split('.', 2)
  if (!encodedSig || !payload) throw new Error('Invalid signed_request')

  const sig = Buffer.from(encodedSig.replace(/-/g, '+').replace(/_/g, '/'), 'base64')
  const dataJson = Buffer.from(payload.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8')
  const data = JSON.parse(dataJson)

  const expectedSig = crypto
    .createHmac('sha256', appSecret)
    .update(payload)
    .digest()

  if (!crypto.timingSafeEqual(sig, expectedSig)) throw new Error('Bad signature')
  return data // includes user_id for Facebook/Instagram
}

export async function POST(request: NextRequest) {
  try {
    const appSecret = process.env.META_APP_SECRET || process.env.FB_APP_SECRET
    if (!appSecret) {
      console.error('Missing META_APP_SECRET environment variable')
      return NextResponse.json({ error: 'Server configuration error' }, { status: 500 })
    }

    const body = await request.json()
    const signed_request = body?.signed_request || request.nextUrl.searchParams.get('signed_request')
    
    if (!signed_request) {
      return NextResponse.json({ error: 'Missing signed_request' }, { status: 400 })
    }

    const data = parseSignedRequest(signed_request, appSecret)

    // The `user_id` is typically in the payload:
    const userId = data?.user_id || data?.user?.id
    if (!userId) {
      return NextResponse.json({ error: 'Missing user_id in signed_request payload' }, { status: 400 })
    }

    // Generate a unique token for this deletion request
    const token = crypto.createHash('sha256').update(String(userId) + Date.now()).digest('hex')
    const host = request.headers.get('x-forwarded-host') || request.headers.get('host') || 'localhost:3000'

    // Call backend deletion (Render) webhook to actually delete
    try {
      const backendUrl = process.env.BACKEND_URL
      const internalToken = process.env.INTERNAL_API_TOKEN
      
      if (backendUrl && internalToken) {
        const backendResponse = await fetch(`${backendUrl}/internal/data-deletion`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json', 
            'X-Internal-Token': internalToken 
          },
          body: JSON.stringify({ userId, token }),
        })

        if (!backendResponse.ok) {
          console.error('Backend deletion failed:', await backendResponse.text())
          // Continue anyway - we'll return the status URL and let the backend handle it
        }
      } else {
        console.warn('Backend URL or internal token not configured - deletion will be queued')
      }
    } catch (backendError) {
      console.error('Error calling backend deletion:', backendError)
      // Continue anyway - we'll return the status URL
    }

    return NextResponse.json({
      url: buildStatusUrl(host, token), // Meta requires this field
      confirmation_code: token,        // Optional but handy
    })
  } catch (err: any) {
    console.error('Data deletion request error:', err)
    return NextResponse.json({ 
      error: err.message || 'Invalid request' 
    }, { status: 400 })
  }
}

export async function GET(request: NextRequest) {
  return NextResponse.json({ 
    error: 'Method Not Allowed. Use POST with signed_request.' 
  }, { status: 405 })
}
