return {
	{
		"mfussenegger/nvim-lint",
		config = function()
			local lint = require("lint")

			lint.linters_by_ft = {
				python = { "flake8" },
				-- javascript = { "eslint" },
				java = { "checkstyle" },
			}

			local LintGroup = vim.api.nvim_create_augroup("lint", { clear = true })

			vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
				group = LintGroup,
				callback = function()
					lint.try_lint()
				end,
			})
		end,
	},
}
