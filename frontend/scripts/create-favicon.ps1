# Create a simple favicon.ico using PowerShell
# This creates a basic 16x16 favicon

Add-Type -AssemblyName System.Drawing

# Create a 16x16 bitmap
$bitmap = New-Object System.Drawing.Bitmap(16, 16)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Fill with blue background (Smart Shield brand color)
$graphics.Clear([System.Drawing.Color]::FromArgb(14, 165, 233)) # #0ea5e9

# Draw a simple shield shape
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 1)
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)

# Simple shield outline
$points = @(
    [System.Drawing.Point]::new(8, 1),
    [System.Drawing.Point]::new(3, 3),
    [System.Drawing.Point]::new(3, 8),
    [System.Drawing.Point]::new(8, 14),
    [System.Drawing.Point]::new(13, 8),
    [System.Drawing.Point]::new(13, 3)
)
$graphics.FillPolygon($brush, $points)
$graphics.DrawPolygon($pen, $points)

# Save as ICO (using PNG format as fallback)
$bitmap.Save("$PSScriptRoot\..\public\favicon.png", [System.Drawing.Imaging.ImageFormat]::Png)

# Clean up
$graphics.Dispose()
$bitmap.Dispose()
$pen.Dispose()
$brush.Dispose()

Write-Host "✅ Created favicon.png" -ForegroundColor Green
Write-Host "Note: For .ico file, use an online converter or image editor" -ForegroundColor Yellow

