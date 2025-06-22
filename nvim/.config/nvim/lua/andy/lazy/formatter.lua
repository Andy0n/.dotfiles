return {
	{
		"stevearc/conform.nvim",
		config = function()
			local conform = require("conform")
			conform.setup({
				formatters_by_ft = {
					lua = { "stylua" },
					-- python = { "isort", "black" },
                    python = { "ruff_fix", "ruff_format", "ruff_organize_imports" },
					javascript = { "prettier" },
					typescript = { "prettier" },
                    html = { "prettier" },
					java = { "google-java-format" },
					-- java = { "clang-format" },
					rust = { "rustfmt" },
                    cpp = { "clang-format" },
                    css = { "prettier" },
                    scss = { "prettier" },
				},
			})

			vim.keymap.set("n", "<leader>f", conform.format)
		end,
	},
}
