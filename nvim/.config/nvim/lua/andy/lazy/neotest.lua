return {
	{
		"nvim-neotest/neotest",
		dependencies = {
			"nvim-neotest/nvim-nio",
			"plenary",
			"antoinemadec/FixCursorHold.nvim",
			"nvim-treesitter/nvim-treesitter",
			-- "neotest-pytest",
            "nvim-neotest/neotest-python",
			"rcasia/neotest-java",
		},
        event = { "BufReadPost", "BufNewFile" },
		config = function()
			local neotest = require("neotest")

---@diagnostic disable-next-line: missing-fields
			neotest.setup({
				adapters = {
					-- require("neotest-pytest"),
					require("neotest-python"),
					require("neotest-java")({
                        ignore_wrapper = false
                    }),
				},
			})

			vim.keymap.set("n", "<leader>tc", neotest.run.run)
			vim.keymap.set("n", "<leader>ts", neotest.summary.toggle)
			vim.keymap.set("n", "<leader>to", neotest.output_panel.toggle)
		end,
	},
	-- {
	-- 	"neotest-pytest",
	-- 	-- dir = "~/repos/neotest-python/"
	-- 	dir = "~/projects/neotest-pytest/",
	-- },
}
