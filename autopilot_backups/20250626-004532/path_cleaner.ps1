<#
.PARAMETER dryRun
是否仅模拟运行而不实际修改
#>
param([switch]$dryRun = $false)

# 获取当前PATH中的所有Python相关路径
$pathEntries = $env:PATH -split ';' | Where-Object {
    $_ -match 'Python' -and 
    -not (Test-Path $_) -and 
    -not [string]::IsNullOrWhiteSpace($_)
}

if ($pathEntries.Count -eq 0) {
    Write-Host "✅ 未检测到无效的Python路径"
    exit 0
}

Write-Host "=== 检测到以下无效路径 ==="
$pathEntries | ForEach-Object { Write-Host " - $_" }

if (-not $dryRun) {
    # 获取系统PATH
    $systemPath = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
    
    # 清理无效路径
    $cleanSystemPath = ($systemPath -split ';' | Where-Object {
        -not ($_ -match 'Python' -and -not (Test-Path $_))
    }) -join ';'
    
    $cleanUserPath = ($userPath -split ';' | Where-Object {
        -not ($_ -match 'Python' -and -not (Test-Path $_))
    }) -join ';'

    # 需要管理员权限修改系统PATH
    if ($cleanSystemPath -ne $systemPath) {
        try {
            if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
                Write-Host "⚠️ 需要管理员权限来清理系统PATH"
                Write-Host "请右键点击PowerShell选择'以管理员身份运行'"
                exit 1
            }
            
            [Environment]::SetEnvironmentVariable('PATH', $cleanSystemPath, 'Machine')
            Write-Host "✅ 已清理系统PATH中的无效Python路径"
        } catch {
            Write-Host "❌ 系统PATH清理失败: $_"
        }
    }

    # 清理用户PATH
    if ($cleanUserPath -ne $userPath) {
        [Environment]::SetEnvironmentVariable('PATH', $cleanUserPath, 'User')
        Write-Host "✅ 已清理用户PATH中的无效Python路径"
    }

    Write-Host "`n请关闭并重新打开所有终端窗口使更改生效"
} else {
    Write-Host "`n⚠️ 模拟运行完成（未实际修改PATH）"
}

# 验证当前Python环境
Write-Host "`n=== 当前Python环境 ==="
try {
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    Write-Host "主程序路径: $pythonPath"
    Write-Host "版本: $(python --version 2>&1)"
} catch {
    Write-Host "❌ 无法找到有效的Python环境"
}