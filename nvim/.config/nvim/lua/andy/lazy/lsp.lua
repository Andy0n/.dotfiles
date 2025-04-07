return {
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPost", "BufNewFile" },
		dependencies = {
			"williamboman/mason.nvim",
			"williamboman/mason-lspconfig.nvim",
			"saghen/blink.cmp",
			"j-hui/fidget.nvim",
		},

		config = function()
			local capabilities = require("blink.cmp").get_lsp_capabilities()

			require("fidget").setup({})
			require("mason").setup()
			require("mason-lspconfig").setup({
				ensure_installed = {
					"lua_ls",
					"rust_analyzer",
					"gopls",
					"pyright",
					"jdtls",
					"clangd",
					"html",
					"ruff",
				},
				automatic_installation = true,
				handlers = {
					function(server_name) -- default handler (optional)
						require("lspconfig")[server_name].setup({
							capabilities = capabilities,
						})
					end,

					["lua_ls"] = function()
						local lspconfig = require("lspconfig")
						lspconfig.lua_ls.setup({
							capabilities = capabilities,
							settings = {
								Lua = {
									callSnippet = "Replace",
								},
							},
						})
					end,

					["pyright"] = function()
						local lspconfig = require("lspconfig")
						lspconfig.pyright.setup({
							capabilities = capabilities,
							settings = {
								python = {
									analysis = {
										autoSearchPaths = true,
										useLibraryCodeForTypes = true,
										diagnosticMode = "workspace",
									},
								},
							},
						})
					end,

					["jdtls"] = function() end,
				},
			})

			require("lspconfig").ltex_plus.setup({})

			vim.diagnostic.config({
				update_in_insert = false,
				float = {
					focusable = false,
					style = "minimal",
					border = "rounded",
					source = "always",
					header = "",
					prefix = "",
				},
			})
		end,
	},
	{
		"folke/lazydev.nvim",
		ft = "lua",
		opts = {},
	},
}
