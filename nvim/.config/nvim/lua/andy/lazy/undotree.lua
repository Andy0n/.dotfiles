return {
	"mbbill/undotree",
	keys = {
		{ "<leader>u", vim.cmd.UndotreeToggle, mode="n" },
	},
	config = function()
		-- vim.keymap.set("n", "<leader>u", vim.cmd.UndotreeToggle)
	end,
}
