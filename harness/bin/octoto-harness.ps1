param(
    [ValidateSet("preflight", "verify", "commit", "close", "hook", "commit-msg", "install-hook", "uninstall-hook")]
    [string] $Mode = "preflight",

    [string] $Repo = "D:\reference2\octoto",

    [switch] $Run,

    [string] $Message,

    [string] $CommitMessageFile
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string] $Title)
    Write-Host ""
    Write-Host "== $Title =="
}

function Invoke-Git {
    param([string[]] $GitArgs)
    & git -C $Repo @GitArgs
}

function Invoke-CheckedCommand {
    param(
        [string] $FilePath,
        [string[]] $Arguments,
        [string] $WorkingDirectory = $null
    )

    if ($WorkingDirectory) {
        Push-Location $WorkingDirectory
    }

    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
        }
    }
    finally {
        if ($WorkingDirectory) {
            Pop-Location
        }
    }
}

function Get-DirtyEntry {
    param([string] $Line)

    if ($Line.Length -lt 4) {
        return $null
    }

    $status = $Line.Substring(0, 2)
    $path = $Line.Substring(3)

    if ($path -like "* -> *") {
        $path = ($path -split " -> ", 2)[1]
    }

    [pscustomobject]@{
        Status = $status.Trim()
        IndexStatus = $status.Substring(0, 1)
        WorkTreeStatus = $status.Substring(1, 1)
        Path = $path
        Area = Get-Area $path
    }
}

function Get-NameStatusEntry {
    param([string] $Line)

    if ([string]::IsNullOrWhiteSpace($Line)) {
        return $null
    }

    $parts = $Line -split "`t"
    if ($parts.Count -lt 2) {
        return $null
    }

    $status = $parts[0]
    $path = $parts[$parts.Count - 1]

    [pscustomobject]@{
        Status = $status
        IndexStatus = $status.Substring(0, 1)
        WorkTreeStatus = " "
        Path = $path
        Area = Get-Area $path
    }
}

function Get-Area {
    param([string] $Path)

    $normalized = $Path -replace "\\", "/"

    if ($normalized -match "^frontend/") { return "frontend" }
    if ($normalized -match "^(src|tests|drizzle|scripts)/") { return "backend" }
    if ($normalized -match "^(docs|todos)/" -or $normalized -match "^(AGENTS|CLAUDE|ARCHITECTURE)\.md$") { return "docs" }
    if ($normalized -match "^(\.claude|\.codex|\.gemini|docs/agents)/") { return "agent" }
    if ($normalized -match "^(package\.json|bun\.lock|Dockerfile|docker-compose|\.env\.example)") { return "infra" }

    "other"
}

function Format-Command {
    param([string] $Command)
    Write-Host "  $Command"
}

function Get-DirtyEntries {
    $lines = @(Invoke-Git @("status", "--porcelain=v1"))
    foreach ($line in $lines) {
        $entry = Get-DirtyEntry $line
        if ($null -ne $entry) {
            $entry
        }
    }
}

function Get-StagedEntries {
    $lines = @(Invoke-Git @("diff", "--cached", "--name-status"))
    foreach ($line in $lines) {
        $entry = Get-NameStatusEntry $line
        if ($null -ne $entry) {
            $entry
        }
    }
}

function Get-ValidationPlan {
    param(
        [object[]] $Entries,
        [switch] $CachedOnly
    )

    $commands = New-Object System.Collections.Generic.List[string]
    if (-not $CachedOnly) {
        $commands.Add("git -C `"$Repo`" diff --check")
    }
    $commands.Add("git -C `"$Repo`" diff --cached --check")

    $backendFiles = @($Entries |
        Where-Object { $_.Area -eq "backend" -and $_.Status -ne "D" } |
        ForEach-Object { $_.Path })

    $backendTests = @($backendFiles | Where-Object { $_ -match "^tests/" })
    $backendCheckFiles = @($backendFiles | Where-Object { $_ -match "^(src|tests)/" })

    if ($backendTests.Count -gt 0) {
        $commands.Add("cd `"$Repo`"; bun test $($backendTests -join ' ')")
    }

    if ($backendCheckFiles.Count -gt 0) {
        $commands.Add("cd `"$Repo`"; bunx biome check $($backendCheckFiles -join ' ')")
    }

    $frontendFiles = @($Entries |
        Where-Object { $_.Area -eq "frontend" -and $_.Status -ne "D" } |
        ForEach-Object { $_.Path })

    $frontendTests = @($frontendFiles |
        Where-Object { $_ -match "^frontend/src/test/" } |
        ForEach-Object { $_ -replace "^frontend/", "" })

    if ($frontendFiles.Count -gt 0) {
        $commands.Add("cd `"$Repo\frontend`"; bunx vue-tsc -b")
    }

    if ($frontendTests.Count -gt 0) {
        $commands.Add("cd `"$Repo\frontend`"; bun run test --run $($frontendTests -join ' ')")
    }

    $commands
}

function Invoke-LightValidation {
    param(
        [object[]] $Entries,
        [switch] $CachedOnly
    )

    Write-Section "Running validation"
    if (-not $CachedOnly) {
        Write-Host "Running git diff --check"
        Invoke-CheckedCommand "git" @("-C", $Repo, "diff", "--check")
    }
    Write-Host "Running git diff --cached --check"
    Invoke-CheckedCommand "git" @("-C", $Repo, "diff", "--cached", "--check")

    $backendTests = @($Entries |
        Where-Object { $_.Area -eq "backend" -and $_.Status -ne "D" -and $_.Path -match "^tests/" } |
        ForEach-Object { $_.Path })

    if ($backendTests.Count -gt 0) {
        Write-Host "Running backend touched tests"
        Invoke-CheckedCommand "bun" (@("test") + $backendTests) $Repo
    }

    $backendCheckFiles = @($Entries |
        Where-Object { $_.Area -eq "backend" -and $_.Status -ne "D" -and $_.Path -match "^(src|tests)/" } |
        ForEach-Object { $_.Path })

    if ($backendCheckFiles.Count -gt 0) {
        Write-Host "Running biome on touched backend files"
        Invoke-CheckedCommand "bunx" (@("biome", "check") + $backendCheckFiles) $Repo
    }

    $frontendFiles = @($Entries |
        Where-Object { $_.Area -eq "frontend" -and $_.Status -ne "D" } |
        ForEach-Object { $_.Path })

    if ($frontendFiles.Count -gt 0) {
        Write-Host "Running frontend typecheck"
        Invoke-CheckedCommand "bunx" @("vue-tsc", "-b") (Join-Path $Repo "frontend")
    }
}

function Assert-CommitReady {
    param([object[]] $Entries)

    if ($Entries.Count -eq 0) {
        throw "No staged changes. Stage the intended files first."
    }

    $areas = @($Entries | Select-Object -ExpandProperty Area -Unique)
    if ($areas -contains "agent" -and $areas.Count -gt 1) {
        throw "Staged changes mix agent/tooling files with product files. Split the commit."
    }

    if ($areas -contains "infra" -and $areas.Count -gt 1) {
        throw "Staged changes mix infra files with other areas. Split the commit."
    }
}

function Get-CommitSubjectSuggestion {
    param([object[]] $Entries)

    $areas = @($Entries | Select-Object -ExpandProperty Area -Unique)
    $scope = if ($areas.Count -eq 1) {
        switch ($areas[0]) {
            "frontend" { "frontend" }
            "backend" { "backend" }
            "docs" { "docs" }
            "agent" { "agents" }
            "infra" { "infra" }
            default { "chore" }
        }
    }
    else {
        "chore"
    }

    "chore($scope): write a concrete subject"
}

function Assert-CommitMessage {
    param([string] $Subject)

    $trimmed = $Subject.Trim()
    $pattern = "^(feat|fix|docs|refactor|test|chore)(\([a-z0-9-]+\))?: .{6,}$"
    if ($trimmed -notmatch $pattern) {
        throw "Commit subject must follow type(scope): concrete description."
    }

    if ($trimmed -match ":\s*(update|fix)\s*$") {
        throw "Commit subject is too vague. Describe the user-visible intent or concrete behavior."
    }
}

function Get-CommitMessageSubject {
    param([string] $Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Commit message file does not exist: $Path"
    }

    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    foreach ($line in $lines) {
        if (-not [string]::IsNullOrWhiteSpace($line) -and -not $line.TrimStart().StartsWith("#")) {
            return $line
        }
    }

    throw "Commit message is empty."
}

function Install-GitHook {
    $hookPath = "D:/reference2/ai-control-tower/harness/git-hooks/octoto"
    Invoke-CheckedCommand "git" @("-C", $Repo, "config", "core.hooksPath", $hookPath)
    Write-Section "Installed hook"
    Write-Host "core.hooksPath=$hookPath"
    Write-Host "git commit now runs octoh hook validation first."
}

function Uninstall-GitHook {
    Invoke-CheckedCommand "git" @("-C", $Repo, "config", "--unset", "core.hooksPath")
    Write-Section "Uninstalled hook"
    Write-Host "Removed local core.hooksPath override."
}

if (-not (Test-Path -LiteralPath $Repo)) {
    throw "Repo path does not exist: $Repo"
}

Write-Section "Runtime harness"
Write-Host "Mode: $Mode"
Write-Host "Repo: $Repo"
Write-Host "Policy: AGENTS.md first, private harness overlay second"

$entries = @(Get-DirtyEntries)
$stagedEntries = @(Get-StagedEntries)

if ($Mode -eq "install-hook") {
    Install-GitHook
    exit 0
}

if ($Mode -eq "uninstall-hook") {
    Uninstall-GitHook
    exit 0
}

if ($Mode -eq "hook") {
    Write-Section "Hook policy"
    Write-Host "Policy: staged diff must pass Octoto harness validation"

    Write-Section "Staged area summary"
    if ($stagedEntries.Count -eq 0) {
        Write-Host "No staged changes"
    }
    else {
        $stagedEntries |
            Group-Object Area |
            Sort-Object Name |
            ForEach-Object {
                Write-Host ("{0}: {1}" -f $_.Name, $_.Count)
            }
    }

    Assert-CommitReady $stagedEntries
    Invoke-LightValidation $stagedEntries -CachedOnly
    exit 0
}

if ($Mode -eq "commit-msg") {
    Write-Section "Commit message policy"
    $subject = Get-CommitMessageSubject $CommitMessageFile
    Write-Host "Subject: $subject"
    Assert-CommitMessage $subject
    exit 0
}

Write-Section "Git state"
Invoke-Git @("status", "--short", "--branch")

Write-Section "Dirty area summary"
if ($entries.Count -eq 0) {
    Write-Host "Clean working tree"
}
else {
    $entries |
        Group-Object Area |
        Sort-Object Name |
        ForEach-Object {
            Write-Host ("{0}: {1}" -f $_.Name, $_.Count)
        }
}

Write-Section "Guardrails"
Write-Host "- Do not stage unrelated dirty files."
Write-Host "- Do not push unless the user explicitly asks."
Write-Host "- Treat docs/agent-memory.md as Octoto project memory."
Write-Host "- Keep private cross-project rules in ai-control-tower."

$plan = @(Get-ValidationPlan $entries)

Write-Section "Selected validation plan"
if ($plan.Count -eq 0) {
    Write-Host "No validation commands selected."
}
else {
    foreach ($command in $plan) {
        Format-Command $command
    }
}

if ($Mode -eq "verify") {
    if ($Run) {
        Invoke-LightValidation $entries
    }
    else {
        Write-Section "Dry run"
        Write-Host "Add -Run to execute the selected light validation."
    }
}

if ($Mode -eq "commit") {
    Write-Section "Commit harness"
    Assert-CommitReady $stagedEntries

    Write-Host "Staged files:"
    $stagedEntries | ForEach-Object {
        Write-Host ("  {0}`t{1}" -f $_.Status, $_.Path)
    }

    Write-Section "Staged validation plan"
    $stagedPlan = @(Get-ValidationPlan $stagedEntries -CachedOnly)
    foreach ($command in $stagedPlan) {
        Format-Command $command
    }

    if (-not $Run) {
        Write-Section "Dry run"
        Write-Host "Add -Run and -Message to validate and commit."
        Write-Host ("Suggested subject: {0}" -f (Get-CommitSubjectSuggestion $stagedEntries))
    }
    else {
        if ([string]::IsNullOrWhiteSpace($Message)) {
            throw "Missing -Message. Use a Korean type(scope): subject commit message."
        }

        Assert-CommitMessage $Message
        Invoke-LightValidation $stagedEntries -CachedOnly
        Write-Section "Creating commit"
        Invoke-CheckedCommand "git" @("-C", $Repo, "commit", "-m", $Message)
    }
}

if ($Mode -eq "close") {
    Write-Section "Close checklist"
    Format-Command "git -C `"$Repo`" log --oneline -8"
    Format-Command "git -C `"$Repo`" stash list"
    Format-Command "git -C `"$Repo`" diff --name-status"
    Write-Host "Then summarize validation, commit, push state, learnings, and harness candidates."
}
