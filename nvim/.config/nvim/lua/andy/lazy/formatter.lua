return {
	{
		"stevearc/conform.nvim",
		config = function()
			local conform = require("conform")
			conform.setup({
				formatters_by_ft = {
					lua = { "stylua" },
					python = { "isort", "black" },
					javascript = { "prettier" },
					typescript = { "prettier" },
					java = { "google-java-format" },
					-- java = { "clang-format" },
					rust = { "rustfmt" },
				},
			})

			vim.keymap.set("n", "<leader>f", conform.format)
		end,
	},
}
