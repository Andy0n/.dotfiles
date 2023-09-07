---@diagnostic disable-next-line: missing-fields
require 'nvim-treesitter.configs'.setup {
    ensure_installed = {
        "c", "cpp", "lua", "vim", "vimdoc", "query", "python", "rust", "java",
        "javascript", "typescript"
    },

    sync_install = false,

    auto_install = true,

    highlight = {
        enable = true,
        additional_vim_regex_highlighting = false,
    },

    indent = {
        enable = true,
    },

    textobjects = {
        select = {
            enable = true,
            lookahead = true,
            keymaps = {
                ['aa'] = '@parameter.outer',
                ['ia'] = '@parameter.inner',
                ['af'] = '@function.outer',
                ['if'] = '@function.inner',
                ['ac'] = '@class.outer',
                ['ic'] = '@class.inner',
            },
        },
        swap = {
            enable = true,
            swap_next = {
                ['<leader>w'] = '@parameter.inner',
            },
            swap_previous = {
                ['<leader>W'] = '@parameter.inner',
            },
        },
    },
}
