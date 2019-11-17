# dafault user & jobs settings
init = {
    "user":"init",
    "key":"42",
    "job":1,
    "state":"0",
}
# status for job
# n2s - name to status
# s2n - status to name
state = {
    "n2s":{
        "run":"R",
        "ok":"0",
        "fail":"1",
        "lock":"2",
    },
    "s2n":{
        "R":"run",
        "0":"ok",
        "1":"fail",
        "2":"lock",
    },
}
# digit to arch
arch = {
    32:"x86",
    64:"x86_64",
}
# file extension to file type
ftype = {
    "deb":"pkg",
    "gz":"arh",
    "xz":"arh",
    "bz":"arh",
    "zip":"arh",
    "7z":"arh",
    "dsc":"log",
    "build":"log",
    "changes":"log",
    "log":"log",
}
# csv delimiter
csvd = ";"
# queue timeout
qetime = 3
