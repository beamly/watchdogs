# This Powershell script connects to Microsoft Office 365 and generates two files:
#
# users.csv  -  A comma seperated file containing A users display name, Mailbox
#               type, and all accociated email addresses
#
# admins.txt -  A tablulated view of all the non standard accounts (Admins,
#               Global admins)
#
# These files are used as the input to the test_o365_users.py test script, which
# verifies that all the admin users and email accounts are expected.
#
# Cards on the table: it took a LONG time to get this script running with a LOT
# of back and forth between the (admittedly excellent) Office365 support team. You'll
# first need to install the snappily titled "Office Online sign in assistant for
# IT Professionals RTW" and "Azure Active Directory Module for Windows PowerShell"
#
# https://support.office.com/en-gb/article/Windows-PowerShell-cmdlets-for-Office-365-06a743bb-ceb6-49a9-a61d-db4ffdf54fa6
#
# I then ran in to a load of issues with the running this script automatically
# even though the commands ran ran fine when run directly in a Powershell Terminal.
# Turned out that the Powershell terminal on the desktop ran in 32 bit mode while
# the OS was running a 64 Bit powershell, each of which has a different search
# path for modules. This took about 2 days to get working.
#
# The solution is to copy the installed files from
#
# C:\Windows\System32\WindowsPowerShell\v1.0\modules\MSOnline
#
# to
#
# C:\Windows\SysWOW64\WindowsPowerShell\v1.0\modules\MSOnline
#
# This script needs two environment variables to be set:
#
# OFFICE_365_USERNAME       The email address of the *READ ONLY* admin user
# OFFICE_365_PASSWORD       The password for the *READ ONLY* admin user
#
# Creating a read only admin user:
#
# 1. Create an account as you would usually, but don't assign them a licence
# 2. Double click the user in the web interface, go to settings, and assign them
#    the "Service administrator" role
# 3. Go to "Exchange Admin Center" and under "Permissions" click "admin roles"
# 4. Create a new role called "Audit Automation", add the "View-Only Recipients"
#    role, and add your your read only audit user created in step 1 as a member
# 5. *IMPORTANT* Sign out and sign back in as your automation user and verify
#    that you can't create or delete accounts
#

# For debugging purposes list the available modules: You should see something like:
#
# ModuleType Name                                ExportedCommands
# ---------- ----                                ----------------
# <snip>
# Manifest   MSOnline                            {New-MsolServicePrincipalAddr...
# <snip>

Get-Module -ListAvailable

$SecPass1 = convertto-securestring -asplaintext -string $env:OFFICE_365_PASSWORD -force
$MSOLM = new-object System.Management.Automation.PSCredential -argumentlist "$env:OFFICE_365_USERNAME",$SecPass1
$Session = New-PSSession -ConfigurationName Microsoft.Exchange -ConnectionUri https://ps.outlook.com/powershell/ -Credential $MSOLM -Authentication Basic -AllowRedirection
Import-Module -Name C:\Windows\System32\WindowsPowershell\v1.0\Modules\MSOnline
Connect-MSOLService -Credential $MSOLM
Import-PSSession $Session -AllowClobber
Get-MsolUser -All | select DisplayName,RecipientType,EmailAddresses | Export-Csv Users.csv
#Get-Recipient -ResultSize Unlimited | select DisplayName,RecipientType,EmailAddresses | Export-Csv users.csv

$O365ROLE = Get-MsolRole
foreach ( $O365ROLE in $O365ROLE )
{
   Write-Host "ROLE:" $O365ROLE.Name
   Get-MsolRoleMember -RoleObjectId $O365ROLE.ObjectId | Out-File -Append admins.txt -encoding utf8 -width 300
}
