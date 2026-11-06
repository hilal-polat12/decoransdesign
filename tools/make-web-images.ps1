<#
Builds the site photos in images/ from the clean originals kept on this computer.

  powershell -ExecutionPolicy Bypass -File tools\make-web-images.ps1               # all products
  powershell -ExecutionPolicy Bypass -File tools\make-web-images.ps1 -Codes 91     # one product
  powershell -ExecutionPolicy Bypass -File tools\make-web-images.ps1 -Codes 85-90  # a range

Reads H<code>.<1|2|3>-2D.jpg (or .png) from the originals folder (default: the Decorans-2D folder
next to this repo), and for each one:
  - square or portrait photos: center-cropped to a 1024 x 1024 square
  - landscape photos (wide room scenes): kept at their own ratio, longest side at most 1024
  - a sparse, small diagonal "decoransdesign" watermark is drawn on top
and writes images/H<code>.<n>-2D.jpg. The originals never go into the repo, which is public.
#>
param(
  [string]$Codes = '',
  [string]$Source = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'Decorans-2D'),
  [string]$Output = (Join-Path (Split-Path $PSScriptRoot -Parent) 'images')
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

# which product codes to build
$wanted = $null
if ($Codes) {
  $wanted = @{}
  foreach ($part in $Codes -split ',') {
    $p = $part.Trim().TrimStart('Hh')
    if ($p -match '^(\d+)-[Hh]?(\d+)$') { [int]$Matches[1]..[int]$Matches[2] | ForEach-Object { $wanted[$_] = $true } }
    elseif ($p -match '^\d+$') { $wanted[[int]$p] = $true }
    elseif ($p) { throw "Unknown code: $part" }
  }
}

$MAX = 1024
$codec = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object Drawing.Imaging.EncoderParameter([Drawing.Imaging.Encoder]::Quality, [long]84)

# watermark: small, thin text, well spaced, rotated -20 degrees, each row shifted by half a step
$font = New-Object Drawing.Font('Segoe UI Semibold', 17, [Drawing.FontStyle]::Regular, [Drawing.GraphicsUnit]::Pixel)
$white = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(150, 255, 255, 255))
$shadow = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(45, 0, 0, 0))
$TEXT = 'decoransdesign'; $STEP_X = 520; $STEP_Y = 210; $ANGLE = -20

$files = Get-ChildItem $Source -File | Where-Object { $_.Name -match '^H(\d+)\.[123]-2D\.(jpg|jpeg|png)$' } |
  Where-Object { $null -eq $wanted -or $wanted.ContainsKey([int]($_.Name -replace '^H(\d+)\..*$', '$1')) } |
  Sort-Object { [int]($_.Name -replace '^H(\d+)\..*$', '$1') }, Name
if (-not $files) { throw "No matching originals in $Source" }

$done = 0
foreach ($f in $files) {
  $img = [Drawing.Image]::FromFile($f.FullName)
  try {
    if ($img.Width -gt $img.Height) {
      # landscape: keep the ratio
      $scale = [Math]::Min(1.0, $MAX / $img.Width)
      $w = [int][Math]::Round($img.Width * $scale); $h = [int][Math]::Round($img.Height * $scale)
      $sx = 0; $sy = 0; $sw = $img.Width; $sh = $img.Height
    } else {
      # square or portrait: center crop to a square
      $side = [Math]::Min($img.Width, $img.Height)
      $w = $MAX; $h = $MAX
      $sx = ($img.Width - $side) / 2; $sy = ($img.Height - $side) / 2; $sw = $side; $sh = $side
    }
    $bmp = New-Object Drawing.Bitmap $w, $h
    $g = [Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'
    $g.PixelOffsetMode = 'HighQuality'; $g.TextRenderingHint = 'AntiAliasGridFit'
    $g.DrawImage($img, (New-Object Drawing.Rectangle 0, 0, $w, $h), $sx, $sy, $sw, $sh, [Drawing.GraphicsUnit]::Pixel)

    $g.TranslateTransform($w / 2, $h / 2)
    $g.RotateTransform($ANGLE)
    $reach = [Math]::Sqrt($w * $w + $h * $h) / 2 + $STEP_X
    $row = 0
    for ($y = -$reach; $y -le $reach; $y += $STEP_Y) {
      $off = if ($row % 2) { $STEP_X / 2 } else { 0 }
      for ($x = -$reach + $off; $x -le $reach; $x += $STEP_X) {
        $g.DrawString($TEXT, $font, $shadow, $x + 1, $y + 1)
        $g.DrawString($TEXT, $font, $white, $x, $y)
      }
      $row++
    }
    $g.Dispose()
  } finally { $img.Dispose() }

  $name = ($f.BaseName) + '.jpg'
  $bmp.Save((Join-Path $Output $name), $codec, $ep); $bmp.Dispose()
  $done++
  Write-Host ('{0}  {1}x{2}' -f $name, $w, $h)
}
Write-Host "$done images written to $Output"
