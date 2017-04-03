set nocompatible              " be iMproved, required
filetype off                  " required
syntax on
set background=dark
set nofoldenable

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
Plugin 'tomasr/molokai.git'
Plugin 'MicahElliott/Rocannon'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'scrooloose/nerdtree'

" Airline Theme
" https://github.com/bling/vim-airline/wiki/Screenshots
let g:airline_theme = 'light'  " or sol, light, dark, molokai

if !exists('g:airline_symbols')
  let g:airline_symbols = {}
endif

let g:ctermhi_discard_rare = 1

"let b:commentary_format = '"%s'

" unicode symbols
let g:airline_left_sep = '»'
let g:airline_left_sep = '▶'
let g:airline_right_sep = '«'
let g:airline_right_sep = '◀'
let g:airline_symbols.linenr = '␊'
let g:airline_symbols.linenr = '␤'
let g:airline_symbols.linenr = '¶'
let g:airline_symbols.branch = '⎇'
let g:airline_symbols.paste = 'ρ'
let g:airline_symbols.paste = 'Þ'
let g:airline_symbols.paste = '∥'
let g:airline_symbols.whitespace = 'Ξ'

au BufNewFile,BufRead *.yml set ft=ansible
set laststatus=2

call vundle#end()            " required
filetype plugin indent on    " required

colorscheme molokai

noremap <C-s> :w<CR>
set clipboard=unnamedplus
set incsearch
