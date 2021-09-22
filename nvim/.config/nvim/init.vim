" VIMRC by Andreas Himmler
"
"  ________  ________   ________      ___    ___ ________  ________
" |\   __  \|\   ___  \|\   ___ \    |\  \  /  /|\   __  \|\   ___  \
" \ \  \|\  \ \  \\ \  \ \  \_|\ \   \ \  \/  / | \  \|\  \ \  \\ \  \
"  \ \   __  \ \  \\ \  \ \  \ \\ \   \ \    / / \ \  \\\  \ \  \\ \  \
"   \ \  \ \  \ \  \\ \  \ \  \_\\ \   \/  /  /   \ \  \\\  \ \  \\ \  \
"    \ \__\ \__\ \__\\ \__\ \_______\__/  / /      \ \_______\ \__\\ \__\
"     \|__|\|__|\|__| \|__|\|_______|\___/ /        \|_______|\|__| \|__|
"                                   \|___|/


"""""""""""""""""""""""""""""
" Plugins:
"""""""""""""""""""""""""""""
call plug#begin('~/.vim/plugged')
    " Fuzzy Finder
    Plug 'nvim-lua/plenary.nvim'
    Plug 'nvim-telescope/telescope.nvim'

    " Colors and more
    Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
    Plug 'gruvbox-community/gruvbox'

    " Undo
    Plug 'mbbill/undotree'

    " Useful tools
    "Plug 'tpope/vim-surround'
    Plug 'tpope/vim-speeddating' " In-/Decrease dates with C-A and C-X
    Plug 'scrooloose/nerdcommenter' " Un-/Comment lines with <leader>cc / <leader>cu

    " Git
    Plug 'tpope/vim-fugitive'
    Plug 'airblade/vim-gitgutter'

    " IntelliSense, Autoformat, Autocomplete, ...
    Plug 'neovim/nvim-lspconfig'
    Plug 'kabouzeid/nvim-lspinstall'
    Plug 'hrsh7th/nvim-compe/'
    "Plug 'glepnir/lspsaga.nvim'
    Plug 'simrat39/symbols-outline.nvim'
    Plug 'L3MON4D3/LuaSnip'
    Plug 'rafamadriz/friendly-snippets'

    Plug 'sbdchd/neoformat'

    " Debugging
    Plug 'puremourning/vimspector'
    Plug 'szw/vim-maximizer'

    " Lightning fast navigation - <leader>j
    Plug 'phaazon/hop.nvim'

    " Beautify
    Plug 'hoob3rt/lualine.nvim'
    Plug 'mhinz/vim-startify'
    Plug 'ap/vim-css-color'
    Plug 'akinsho/bufferline.nvim'

    " ThePrimeagen
    Plug 'ThePrimeagen/vim-be-good'
call plug#end()

lua require("andy")


"""""""""""""""""""""""""""""
" Mappings:
"""""""""""""""""""""""""""""
let mapleader = " "

nnoremap <F6> :UndotreeToggle<CR>

