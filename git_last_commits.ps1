###
# this script extracts the history of all branches of all git repos under a fixed folder (c:\dev\)
# a command line switch (--all) allows for extracting last commits only or all commits
###
function explore($parent){
    # write-host $parent
    if(test-path "$parent\.git\HEAD".replace('[', '`[').replace(']', '`]')  -PathType Leaf){
        $parent
    }
    foreach($sub in (dir -dir $parent -force) | ?{$_.name -notlike 'env*' -and $_.name -notlike '.*'  -and $_.name -notlike 'tfsroot'})
    {
        explore $sub.FullName
    }
}


function last_commits ($folder, $after){
    $hist = (git hist --after=$after | %{"$dir - $_"})
    if($hist){
        write-host $_
        Write-Host $hist
    }
}

function all_commits ($folder){
    Write-Progress -Activity "processing folder $folder"
    $branches = (git branch --all)
    $current_branch = ($branches | ?{$_.substring(0,1) -eq '*'} | %{$_.substring(2)})
    $results = @{
        'folder'   = $folder;
        'branch'   = $current_branch;
        'remote'   = (git remote -v | ?{$_ -like '*push*'})
        'status'   = (git status)
        'branches' = @{}
    }
    write-debug $folder
    $fetch = (git fetch)
    $b=0
    $branches `
    | ?{$_ -notlike '*->*'} `
    | %{$_.substring(2)} `
    | %{
        Write-Progress -Activity "processing folder $folder" -Status $_ -PercentComplete (100*$b / $branches.count)
        $b+=1
        write-debug $_
        try{
            $hist = (git hist $_ -n 999999| ?{$_ -like '*Raemy*'})
            if($hist){
                $results['branches'][$_] = $hist
            }
        }
        catch {
            $results['branches'][$_] = $error
        }

    }
    Write-Progress -Activity "processing folder $folder" -Status 'Done' -PercentComplete 100
    $results | ConvertTo-Json
}

$all = if($args | ?{$_ -eq '--all'}) {$True} else {$False}


$DebugPreference = 'SilentlyContinue' # 'Break' #


$after = (get-date).adddays(-7).tostring('yyyy-MM-dd')
explore 'c:\dev' | %{
    $dir = $_
    pushd $dir;
    $Host.UI.RawUI.WindowTitle = $_;
    try {
        if($all){all_commits $_}
        else {last_commits $_ $after}
    }
    catch {
        $error
    }
    popd
}

$DebugPreference = 'SilentlyContinue'
