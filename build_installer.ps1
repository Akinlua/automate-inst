# Instagram Auto Poster - PowerShell Installer Builder
# Alternative to NSIS for creating Windows installers

param(
    [string]$OutputPath = ".",
    [switch]$Sign,
    [string]$CertificatePath,
    [string]$CertificatePassword
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Instagram Auto Poster - Installer Builder" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if NSIS is available
$nsisPath = Get-Command "makensis" -ErrorAction SilentlyContinue

if (-not $nsisPath) {
    Write-Host "❌ NSIS not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install NSIS from: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installation:" -ForegroundColor White
    Write-Host "1. Add NSIS to your PATH environment variable" -ForegroundColor White
    Write-Host "2. Or run this script from the NSIS installation directory" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ NSIS found at: $($nsisPath.Source)" -ForegroundColor Green
Write-Host ""

# Build the installer
Write-Host "🔨 Building installer..." -ForegroundColor Blue
try {
    & makensis "installer.nsi"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Installer built successfully!" -ForegroundColor Green
        
        # Find the created installer
        $installerFile = Get-ChildItem -Name "Instagram_Auto_Poster_Installer_*.exe" | Select-Object -First 1
        
        if ($installerFile) {
            Write-Host "📦 Installer created: $installerFile" -ForegroundColor Cyan
            
            # Sign the installer if requested
            if ($Sign -and $CertificatePath) {
                Write-Host ""
                Write-Host "🔐 Digitally signing installer..." -ForegroundColor Blue
                
                # Check if signtool is available
                $signtool = Get-Command "signtool" -ErrorAction SilentlyContinue
                
                if ($signtool) {
                    try {
                        if ($CertificatePassword) {
                            & signtool sign /f $CertificatePath /p $CertificatePassword /t "http://timestamp.digicert.com" /fd sha256 /v $installerFile
                        } else {
                            & signtool sign /f $CertificatePath /t "http://timestamp.digicert.com" /fd sha256 /v $installerFile
                        }
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "✅ Installer signed successfully!" -ForegroundColor Green
                            
                            # Verify signature
                            Write-Host "🔍 Verifying signature..." -ForegroundColor Blue
                            & signtool verify /pa /v $installerFile
                        } else {
                            Write-Host "❌ Signing failed!" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host "❌ Signing error: $($_.Exception.Message)" -ForegroundColor Red
                    }
                } else {
                    Write-Host "❌ signtool.exe not found! Please install Windows SDK." -ForegroundColor Red
                }
            }
            
            Write-Host ""
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host "   🎉 Build Complete!" -ForegroundColor Green
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "✨ Your professional installer is ready!" -ForegroundColor White
            Write-Host "📁 Location: $(Get-Location)\$installerFile" -ForegroundColor White
            Write-Host ""
            
            if (-not $Sign) {
                Write-Host "💡 To digitally sign your installer:" -ForegroundColor Yellow
                Write-Host "   .\build_installer.ps1 -Sign -CertificatePath 'path\to\cert.pfx' -CertificatePassword 'password'" -ForegroundColor Gray
                Write-Host ""
                Write-Host "📖 See SIGNING_GUIDE.md for detailed instructions" -ForegroundColor Yellow
                Write-Host ""
            }
            
            Write-Host "🚀 Ready for distribution!" -ForegroundColor Green
            
        } else {
            Write-Host "❌ Could not find created installer file!" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Installer build failed!" -ForegroundColor Red
        Write-Host "Please check the errors above." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Build error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
