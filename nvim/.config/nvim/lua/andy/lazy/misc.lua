return {
	{ "numToStr/Comment.nvim", opts = {} },
	{
		"folke/todo-comments.nvim",
		event = "VimEnter",
		dependencies = { "plenary" },
		opts = { signs = false },
	},
	{
		"lukas-reineke/indent-blankline.nvim",
		main = "ibl",
		dependencies = {
			"nvim-treesitter/nvim-treesitter",
			"catppuccin",
		},
		opts = {
			indent = {
				char = "┊",
			},
			scope = {
				show_start = false,
				show_end = false,
			},
		},
	},
	{
		"ThePrimeagen/vim-be-good",
		dependencies = {
			"plenary",
		},

		config = function() end,
	},
	{
		"tpope/vim-obsession",
	},
	{
		"tjdevries/present.nvim",
		config = function()
            present = require("present")
            -- present.setup({})
		end,
	},
	-- {
	-- 	"folke/noice.nvim",
	-- 	event = "VeryLazy",
	-- 	dependencies = {
	-- 		"MunifTanjim/nui.nvim",
	-- 		"rcarriga/nvim-notify",
	-- 	},
	-- 	config = function()
	-- 		require("noice").setup({
	-- 			lsp = {
	-- 				-- override markdown rendering so that **cmp** and other plugins use **Treesitter**
	-- 				override = {
	-- 					["vim.lsp.util.convert_input_to_markdown_lines"] = true,
	-- 					["vim.lsp.util.stylize_markdown"] = true,
	-- 					["cmp.entry.get_documentation"] = true, -- requires hrsh7th/nvim-cmp
	-- 				},
	-- 			},
	-- 			-- you can enable a preset for easier configuration
	-- 			presets = {
	-- 				bottom_search = true, -- use a classic bottom cmdline for search
	-- 				command_palette = true, -- position the cmdline and popupmenu together
	-- 				long_message_to_split = true, -- long messages will be sent to a split
	-- 				inc_rename = false, -- enables an input dialog for inc-rename.nvim
	-- 				lsp_doc_border = false, -- add a border to hover docs and signature help
	-- 			},
	-- 		})
	-- 	end,
	-- },
}
