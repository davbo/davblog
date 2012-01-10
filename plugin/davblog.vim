" A Vim Plugin for posting to my personal blog.
" Hopefully I'll end up extending this and it could be useful to others?
"
"

pyfile davblog.py
if has('python')
    command! DavblogBrowse python davblog.davblog_browse()
endif

python davblog_init()
