return {
	{
		"nvim-neotest/neotest",
		dependencies = {
			"nvim-neotest/nvim-nio",
			"plenary",
			"antoinemadec/FixCursorHold.nvim",
			"nvim-treesitter/nvim-treesitter",
			"nvim-neotest/neotest-python",
		},
		config = function()
			local neotest = require("neotest")

			neotest.setup({
				adapters = {
					require("neotest-python"),
				},
			})

			vim.keymap.set("n", "<leader>tc", neotest.run.run)
			vim.keymap.set("n", "<leader>ts", neotest.summary.toggle)
			vim.keymap.set("n", "<leader>to", neotest.output_panel.toggle)
		end,
	},
}
