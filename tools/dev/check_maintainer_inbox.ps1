param(
    [string]$Repo = "",
    [int]$CommentLimit = 100
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoFromRemote {
    $remote = (git remote get-url origin).Trim()
    if (-not $remote) {
        throw "Could not determine origin remote."
    }

    if ($remote -match 'github\.com[:/](?<repo>[^/]+/[^/.]+)(?:\.git)?$') {
        return $Matches.repo
    }

    throw "Could not parse GitHub repo from remote: $remote"
}

function Get-AuthenticatedLogin {
    return (gh api user --jq .login).Trim()
}

if (-not $Repo) {
    $Repo = Get-RepoFromRemote
}

$maintainerLogin = Get-AuthenticatedLogin

$openPrs = gh pr list --repo $Repo --state open --json number,title,author,isDraft,reviewDecision,updatedAt,url |
    ConvertFrom-Json

$openIssues = gh issue list --repo $Repo --state open --json number,title,assignees,updatedAt,url |
    ConvertFrom-Json

$recentComments = gh api "repos/$Repo/issues/comments?per_page=$CommentLimit" | ConvertFrom-Json

$commentsByThread = @{}
foreach ($comment in $recentComments) {
    $threadKey = $comment.issue_url
    if (-not $commentsByThread.ContainsKey($threadKey)) {
        $commentsByThread[$threadKey] = @()
    }
    $commentsByThread[$threadKey] += $comment
}

$pendingThreads = @()
foreach ($threadKey in $commentsByThread.Keys) {
    $threadComments = $commentsByThread[$threadKey] | Sort-Object created_at
    $latestExternal = $null
    $maintainerRepliedAfter = $false

    foreach ($comment in $threadComments) {
        $isMaintainer = $comment.user.login -eq $maintainerLogin
        if (-not $isMaintainer) {
            $latestExternal = $comment
            $maintainerRepliedAfter = $false
            continue
        }

        if ($latestExternal) {
            $maintainerRepliedAfter = $true
        }
    }

    if ($latestExternal -and -not $maintainerRepliedAfter) {
        $pendingThreads += [pscustomobject]@{
            ThreadUrl = $latestExternal.html_url
            Author = $latestExternal.user.login
            CreatedAt = $latestExternal.created_at
            Body = ($latestExternal.body -replace '\s+', ' ').Trim()
        }
    }
}

Write-Host ""
Write-Host "Repo: $Repo" -ForegroundColor Cyan
Write-Host "Maintainer login used for reply detection: $maintainerLogin" -ForegroundColor Cyan

Write-Host ""
Write-Host "Open PRs" -ForegroundColor Yellow
if (-not $openPrs) {
    Write-Host "  none"
} else {
    foreach ($pr in $openPrs | Sort-Object updatedAt -Descending) {
        $draft = if ($pr.isDraft) { "draft" } else { "ready" }
        $review = if ($pr.reviewDecision) { $pr.reviewDecision } else { "no-decision" }
        Write-Host ("  #{0} [{1}] [{2}] {3}" -f $pr.number, $draft, $review, $pr.title)
        Write-Host ("     {0}" -f $pr.url)
    }
}

Write-Host ""
Write-Host "Open Issues" -ForegroundColor Yellow
if (-not $openIssues) {
    Write-Host "  none"
} else {
    foreach ($issue in $openIssues | Sort-Object updatedAt -Descending) {
        $assigneeCount = @($issue.assignees).Count
        $assigneeState = if ($assigneeCount -gt 0) { "$assigneeCount assignee(s)" } else { "unassigned" }
        Write-Host ("  #{0} [{1}] {2}" -f $issue.number, $assigneeState, $issue.title)
        Write-Host ("     {0}" -f $issue.url)
    }
}

Write-Host ""
Write-Host "Recent External Comments Without Maintainer Follow-Up" -ForegroundColor Yellow
if (-not $pendingThreads) {
    Write-Host "  none"
} else {
    foreach ($item in $pendingThreads | Sort-Object CreatedAt -Descending) {
        Write-Host ("  {0} by {1} at {2}" -f $item.ThreadUrl, $item.Author, $item.CreatedAt)
        Write-Host ("     {0}" -f $item.Body)
    }
}
