import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import { requireAuth } from '@/lib/auth-server'

export async function GET(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    console.log('Attempting to fetch images from Supabase...')
    
    const { data: images, error } = await supabase
      .from('images')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch images' },
        { status: 500 }
      )
    }
    
    console.log('Successfully fetched images:', images?.length || 0)
    
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
    console.log('POST /api/images called')
    
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const formData = await request.formData()
    const images = formData.getAll('images') as File[]

    console.log(`Processing ${images.length} images`)

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

        // Insert into images table using Supabase
        try {
          const { data: imageData, error: insertError } = await supabase
            .from('images')
            .insert({
              filename: fileName,
              url: urlData.publicUrl,
              size: image.size,
              type: image.type
            })
            .select()
            .single()

          if (insertError) {
            console.error('Database insert error:', insertError)
            results.errors.push(`Image insert error: ${insertError.message}`)
          } else if (imageData) {
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

    console.log('Returning results:', results)

    return NextResponse.json({
      success: true,
      data: results
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { success: false, error: `Upload failed: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    )
  }
} 