function ColorMyPencils(color)
	color = color or "catppuccin"
	vim.cmd.colorscheme(color)

	-- vim.api.nvim_set_hl(0, "Normal", { bg = "none" })
	-- vim.api.nvim_set_hl(0, "NormalFloat", { bg = "none" })
end

return {
	{
		"dasupradyumna/midnight.nvim",
		lazy = true,
	},
	{
		"catppuccin/nvim",
		name = "catppuccin",
		lazy = false,
		priority = 1000,
		config = function()
			require("catppuccin").setup({
				flavour = "mocha",
				-- transparent_background = true,
				integrations = {
					indent_blankline = {
						enabled = true,
						scope_color = "flamingo", -- catppuccin color (eg. `lavender`) Default: text
						colored_indent_levels = false,
					},
				},
			})

			vim.cmd("colorscheme catppuccin")

			ColorMyPencils()
		end,
	},
}
