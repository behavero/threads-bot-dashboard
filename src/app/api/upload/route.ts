import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'
import { requireAuth } from '@/lib/auth-server'

export async function POST(request: NextRequest) {
  try {
    // Require authentication
    const user = await requireAuth(request)
    
    const formData = await request.formData()
    const captions = formData.get('captions') as string
    const images = formData.getAll('images') as File[]

    const results: {
      captions: any[];
      images: any[];
      errors: string[];
    } = {
      captions: [],
      images: [],
      errors: []
    }

    // Handle captions
    if (captions && captions.trim()) {
      const captionList = captions.split('\n').filter(caption => caption.trim())
      
      for (const caption of captionList) {
        try {
          const [data] = await sql`
            INSERT INTO captions (user_id, text, created_at)
            VALUES (${user.id}, ${caption.trim()}, ${new Date().toISOString()})
            RETURNING *
          `

          if (data) {
            results.captions.push(data)
          }
        } catch (error) {
          results.errors.push(`Caption error: ${error}`)
        }
      }
    }

    // Handle images
    for (const image of images) {
      try {
        console.log('Processing image:', image.name, 'Size:', image.size)
        
        // Upload to Supabase Storage
        const fileName = `${Date.now()}-${image.name}`
        console.log('Uploading to Supabase Storage with filename:', fileName)
        
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('images')
          .upload(fileName, image)

        if (uploadError) {
          console.error('Supabase Storage upload error:', uploadError)
          results.errors.push(`Image upload error: ${uploadError.message}`)
          continue
        }

        console.log('Upload successful, getting public URL...')
        
        // Get public URL
        const { data: urlData } = supabase.storage
          .from('images')
          .getPublicUrl(fileName)

        console.log('Public URL:', urlData.publicUrl)

        // Insert into images table
        try {
          const [imageData] = await sql`
            INSERT INTO images (user_id, filename, url, size, type, created_at)
            VALUES (${user.id}, ${fileName}, ${urlData.publicUrl}, ${image.size}, ${image.type}, ${new Date().toISOString()})
            RETURNING *
          `

          if (imageData) {
            console.log('Image data inserted successfully:', imageData.id)
            results.images.push(imageData)
          }
        } catch (insertError) {
          console.error('Database insert error:', insertError)
          results.errors.push(`Image insert error: ${insertError}`)
        }
      } catch (error) {
        console.error('General image processing error:', error)
        results.errors.push(`Image error: ${error}`)
      }
    }

    return NextResponse.json({
      success: true,
      data: results
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { success: false, error: 'Upload failed' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    // Require authentication
    const user = await requireAuth(request)
    
    // Fetch existing captions and images (RLS will automatically filter by user_id)
    const [captions, images] = await Promise.all([
      sql`SELECT * FROM captions ORDER BY created_at DESC`,
      sql`SELECT * FROM images ORDER BY created_at DESC`
    ])

    return NextResponse.json({
      success: true,
      data: {
        captions: captions || [],
        images: images || []
      }
    })
  } catch (error) {
    console.error('Fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Fetch failed' },
      { status: 500 }
    )
  }
} 