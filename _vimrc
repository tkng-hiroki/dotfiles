" Input
set expandtab
set tabstop=4
set shiftwidth=4
set softtabstop=4
set cinoptions+=g1
set cinoptions+=h1
set indentexpr=GetCppIndent()

function! GetCppIndent()
    let curr_line = getpos('.')[1]
    let prev_indx = 1
    while match(getline(curr_line - prev_indx), '^[ \t]*$') == 0
        let prev_indx = prev_indx + 1
    endwhile
    let prev_line = getline(curr_line - prev_indx)
    let ns_indent = match(prev_line, 'namespace')
    if 0 <= ns_indent
        return ns_indent
    endif
    return cindent('.')
endfunction 

" Mapping
map J <C-d>
map K <C-u>
map <C-j> <C-w>j
map <C-k> <C-w>k
map <C-h> <C-w>h
map <C-l> <C-w>l

" Backup
set backup
set backupdir=$HOME/vimfiles/backup
set swapfile
set directory=$HOME/vimfiles/backup,c:\temp
set history=1000
set undodir=$HOME/vimfiles/undo

" Dein
if &compatible
  set nocompatible
endif

set shellslash
let s:dein_dir=expand('$HOME/dein/plugin')
let s:dein_rep_dir=expand('$HOME/dein/dein.vim')
let s:dein_config=expand('$HOME/dein/config.toml')
let s:dein_config_lazy=expand('$HOME/dein/config_lazy.toml')

if &runtimepath !~# 'dein.vim'
  if !isdirectory(s:dein_rep_dir)
    execute '!git clone https://github.com/Shougo/dein.vim' s:dein_rep_dir
  endif
  execute 'set runtimepath^=' . s:dein_rep_dir
endif

if dein#load_state(s:dein_dir)
  call dein#begin(s:dein_dir, [$MYVIMRC, s:dein_config])
  call dein#load_toml(s:dein_config)
  call dein#load_toml(s:dein_config_lazy, {'lazy': 1})
  call dein#end()
  call dein#save_state()
endif

filetype plugin indent on
syntax enable

if dein#check_install()
  call dein#install()
endif
