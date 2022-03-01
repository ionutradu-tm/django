import os
import fileinput

ACTIVE_BRANCHES = os.environ["ACTIVE_BRANCHES"]
Branches = ACTIVE_BRANCHES.split()
number_of_branches = len(Branches)
TextToReplace = '<select name="FromBranch">'
TextReplacement = '<select name="FromBranch">\n'
for repo in Branches:
    if number_of_branches > 1:
        TextReplacement = TextReplacement + "\t\t<option value=\"" + repo + "\">" + repo + "</option>\n"
        number_of_branches = number_of_branches - 1
    else:
        TextReplacement = TextReplacement + "\t\t<option value=\"" + repo + "\">" + repo + "</option>"
with fileinput.FileInput('mng/templates/deploy.html', inplace=True) as FileWrite:
    for line in FileWrite:
        print(line.replace(TextToReplace, TextReplacement), end='')