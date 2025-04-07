vim.opt.guicursor = ""

vim.opt.number = true
vim.opt.relativenumber = true

vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true

vim.opt.smartindent = true

vim.opt.wrap = false

vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"
vim.opt.undofile = true

vim.opt.incsearch = true
vim.opt.hlsearch = false

vim.opt.termguicolors = true

vim.opt.scrolloff = 8
vim.opt.signcolumn = "yes"
-- vim.opt.colorcolumn = "81"
vim.opt.isfname:append("@-@")
vim.opt.cursorline = false
vim.opt.ruler = true

vim.opt.updatetime = 50

--vim.opt.clipboard = "unnamedplus"
vim.opt.mouse = "a"

vim.opt.smartcase = true
vim.opt.ignorecase = true

vim.opt.wildmenu = true
vim.opt.wildmode = "longest:full,full"
vim.opt.completeopt = "menuone,noselect"

vim.opt.autoread = true

vim.opt.splitright = true
vim.opt.splitbelow = true

vim.opt.showmode = false
