import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'
import { requireAuth } from '@/lib/auth-server'

export async function GET(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const images = await sql`
      SELECT * FROM images 
      ORDER BY created_at DESC
    `

    return NextResponse.json({
      success: true,
      images: images || []
    })
  } catch (error) {
    console.error('Error fetching images:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch images' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const formData = await request.formData()
    const images = formData.getAll('images') as File[]

    const results: {
      images: any[];
      errors: string[];
    } = {
      images: [],
      errors: []
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
            INSERT INTO images (filename, url, size, type)
            VALUES (${fileName}, ${urlData.publicUrl}, ${image.size}, ${image.type})
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