" A Vim Plugin for posting to my personal blog.
" Hopefully I'll end up extending this and it could be useful to others?
"
"

if filereadable($VIMRUNTIME."/plugin/davblog.py")
  pyfile $VIMRUNTIME/plugin/davblog.py
elseif filereadable($HOME."/.vim/plugin/davblog.py")
  pyfile $HOME/.vim/plugin/davblog.py
if filereadable($VIMRUNTIME."/.vim/bundle/davblog/plugin/davblog.py")
  pyfile $VIMRUNTIME/bundle/davblog/plugin/davblog.py
elseif filereadable($HOME."/.vim/bundle/davblog/plugin/davblog.py")
  pyfile $HOME/.vim/bundle/davblog/plugin/davblog.py
else
  call confirm('Unable to find davblog.vim', 'OK')
  finish
endif
if has('python')
    command! DavblogBrowse python davblog.davblog_browse()
endif

python davblog_init()
