<#
.SYNOPSIS
工程文件清理工具 v1.1

.DESCRIPTION
安全清理非核心工程文件，交互式确认每个删除操作
#>

param(
    [switch]$force = $false,
    [switch]$dryRun = $false
)

# 危险文件模式匹配
$patterns = @(
    '^\.craft-',    # Craft工具文件
    '\.bak$',       # 备份文件
    '~$',           # 临时文件
    '^\._'          # 系统临时文件
)

# 核心文件白名单
$protectedFiles = @(
    '\.py$',
    '\.md$',
    '\.ps1$',
    '\.bat$',
    '\.json$',
    '\.sh$'
)

# 交互式确认函数
function Confirm-Delete {
    param($file)
    if ($force) { return $true }
    $choice = Read-Host "确认删除 '$file'? (y/n)"
    return $choice -eq 'y'
}

# 主清理流程
Write-Host "=== 工程文件扫描 ==="
Get-ChildItem -Recurse -File | Where-Object {
    $file = $_.FullName
    $isProtected = $protectedFiles | Where-Object { $file -match $_ }
    $isDangerous = $patterns | Where-Object { $file -match $_ }
    
    $isDangerous -and (-not $isProtected)
} | ForEach-Object {
    $file = $_.FullName
    if ($dryRun) {
        Write-Host "[模拟] 将删除: $file" -ForegroundColor Yellow
    }
    elseif (Confirm-Delete $file) {
        try {
            Remove-Item $file -Force
            Write-Host "[成功] 已删除: $file" -ForegroundColor Green
        }
        catch {
            Write-Host "[失败] 删除错误: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "[跳过] 保留文件: $file" -ForegroundColor Blue
    }
}

# 清理空目录
Write-Host "`n=== 空目录清理 ==="
Get-ChildItem -Recurse -Directory | Where-Object { 
    @(Get-ChildItem -Path $_.FullName -Recurse -File).Count -eq 0 
} | ForEach-Object {
    $dir = $_.FullName
    if ($dryRun) {
        Write-Host "[模拟] 将删除空目录: $dir" -ForegroundColor Yellow
    }
    elseif (Confirm-Delete $dir) {
        try {
            Remove-Item $dir -Force
            Write-Host "[成功] 已删除空目录: $dir" -ForegroundColor Green
        }
        catch {
            Write-Host "[失败] 目录删除错误: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "[跳过] 保留空目录: $dir" -ForegroundColor Blue
    }
}

Write-Host "`n=== 清理完成 ==="
if ($dryRun) {
    Write-Host "本次为模拟运行，未实际修改文件系统" -ForegroundColor Cyan
}
else {
    Write-Host "实际清理操作已完成" -ForegroundColor Cyan
}