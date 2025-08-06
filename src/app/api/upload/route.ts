import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'
import { requireAuth } from '@/lib/auth-server'

export async function POST(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
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
            INSERT INTO captions (text, created_at)
            VALUES (${caption.trim()}, ${new Date().toISOString()})
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
        console.log(`Processing image: ${image.name} (${image.size} bytes, ${image.type})`)
        
        // Upload to Supabase Storage
        const fileName = `${Date.now()}-${image.name}`
        console.log(`Uploading to storage with filename: ${fileName}`)
        
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('images')
          .upload(fileName, image)

        if (uploadError) {
          console.error('Storage upload error:', uploadError)
          results.errors.push(`Image upload error: ${uploadError.message}`)
          continue
        }

        console.log('Upload successful:', uploadData)

        // Get public URL
        const { data: urlData } = supabase.storage
          .from('images')
          .getPublicUrl(fileName)

        console.log('Public URL:', urlData.publicUrl)

        // Insert into images table
        try {
          const [imageData] = await sql`
            INSERT INTO images (filename, url, size, type, created_at)
            VALUES (${fileName}, ${urlData.publicUrl}, ${image.size}, ${image.type}, ${new Date().toISOString()})
            RETURNING *
          `

          if (imageData) {
            console.log('Image inserted into database:', imageData)
            results.images.push(imageData)
          }
        } catch (insertError) {
          console.error('Database insert error:', insertError)
          results.errors.push(`Image insert error: ${insertError}`)
        }
      } catch (error) {
        console.error('General image error:', error)
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
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
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