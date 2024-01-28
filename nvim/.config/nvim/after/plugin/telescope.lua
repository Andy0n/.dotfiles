pcall(require('telescope').load_extension, 'fzf')

require('telescope').setup({
    defaults = {
        -- prompt_prefix="🔍 ",
    },
    pickers = {
        find_files = {
            hidden = true,
            ignore = true,
            background = false,
            -- theme = 'cursor',
            -- previewer = false,
        },
    }
})

local builtin = require('telescope.builtin')
vim.keymap.set('n', '<leader>ff', builtin.find_files, { desc = 'Find [F]iles' })
vim.keymap.set('n', '<leader>gf', builtin.git_files, { desc = 'Find [G]it [F]iles' })
vim.keymap.set('n', '<leader>fb', builtin.buffers, { desc = 'Find [B]uffers' })
vim.keymap.set('n', '<leader>fr', builtin.oldfiles, { desc = 'Find [R]ecent [F]iles' })
vim.keymap.set('n', '<leader>fc', builtin.colorscheme, { desc = 'Find [C]olorschemes' })

