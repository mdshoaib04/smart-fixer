# Install Scoop if not installed
if (!(Get-Command scoop -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Scoop Package Manager..."
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    iwr -useb get.scoop.sh | iex
}

# Add Scoop to current session path explicitly
$env:PATH += ";$env:USERPROFILE\scoop\shims"

Write-Host "Installing Git (Required)..."
scoop install git

Write-Host "Adding Java Bucket..."
scoop bucket add java

Write-Host "Installing Compilers and Interpreters..."
scoop install gcc nodejs go rust ruby php openjdk

Write-Host "=========================================="
Write-Host "Installation Complete!"
Write-Host "IMPORTANT: You MUST restart your terminal (close and reopen) for changes to take effect."
Write-Host "=========================================="
