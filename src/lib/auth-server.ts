import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest } from 'next/server'

export async function createServerSupabaseClient() {
  try {
    const cookieStore = await cookies()

    return createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll(cookiesToSet) {
            try {
              cookiesToSet.forEach(({ name, value, options }) =>
                cookieStore.set(name, value, options)
              )
            } catch {
              // The `setAll` method was called from a Server Component.
              // This can be ignored if you have middleware refreshing
              // user sessions.
            }
          },
        },
      }
    )
  } catch (error) {
    // Handle the case where cookies are not available (static generation)
    console.warn('Cookies not available, using fallback authentication')
    return null
  }
}

export async function getServerUser(request?: NextRequest) {
  const supabase = await createServerSupabaseClient()
  if (!supabase) {
    throw new Error('Authentication not available')
  }
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

export async function requireAuth(request?: NextRequest) {
  try {
    const user = await getServerUser(request)
    if (!user) {
      throw new Error('Unauthorized')
    }
    return user
  } catch (error) {
    throw new Error('Unauthorized')
  }
} 