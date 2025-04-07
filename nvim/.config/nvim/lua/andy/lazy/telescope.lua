return {
	"nvim-telescope/telescope.nvim",
	name = "telescope",
	dependencies = {
		"plenary",
		{
			"nvim-telescope/telescope-fzf-native.nvim",
			build = "make",
			cond = function()
				return vim.fn.executable("make") == 1
			end,
		},
		"nvim-telescope/telescope-ui-select.nvim",
		"nvim-tree/nvim-web-devicons",
	},
	config = function()
		require("telescope").setup({
			defaults = require("telescope.themes").get_ivy(),
			pickers = {
				git_files = {
					show_untracked = true,
				},
			},
			extensions = {
				["ui-select"] = {
					require("telescope.themes").get_dropdown(),
				},
				fzf = {},
			},
		})

		require("telescope").load_extension("fzf")
		require("telescope").load_extension("ui-select")

		local builtin = require("telescope.builtin")
		vim.keymap.set("n", "<leader>jf", builtin.find_files, {})
		vim.keymap.set("n", "<leader>jg", builtin.git_files, {})
		vim.keymap.set("n", "<leader>jh", builtin.help_tags, {})
		vim.keymap.set("n", "<leader>js", builtin.live_grep, {})

		vim.keymap.set("n", "<leader>jws", function()
			local word = vim.fn.expand("<cword>")
			builtin.grep_string({ search = word })
		end)

		vim.keymap.set("n", "<leader>jWs", function()
			local word = vim.fn.expand("<cWORD>")
			builtin.grep_string({ search = word })
		end)

		vim.keymap.set("n", "<leader>/", function()
			builtin.current_buffer_fuzzy_find(require("telescope.themes").get_ivy({
				-- winblend = 10,
				previewer = false,
			}))
		end)
	end,
}
