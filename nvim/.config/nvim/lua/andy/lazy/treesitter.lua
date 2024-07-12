return {
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate",
		config = function()
			require("nvim-treesitter.configs").setup({
				ensure_installed = {
					"vimdoc",
					"javascript",
					"typescript",
					"c",
					"lua",
					"rust",
					"jsdoc",
					"bash",
					"cpp",
					"python",
					"java",
					"markdown",
				},

				sync_install = false,

				auto_install = true,

				indent = {
					enable = true,
				},

				highlight = {
					enable = true,
					additional_vim_regex_highlighting = { "markdown" },
				},
			})
		end,
	},
	{
		"nvim-treesitter/playground",
	},
}
