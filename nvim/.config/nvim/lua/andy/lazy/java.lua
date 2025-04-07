return {
	{
		"mfussenegger/nvim-jdtls",

		dependencies = {
			"neovim/nvim-lspconfig",
            "saghen/blink.cmp",
		},

		ft = { "java" },
		enabled = true,

		config = function()
			print("jdtls loaded")
            local capabilities = require("blink.cmp").get_lsp_capabilities()

			local jdtls = require("jdtls")
			local jdtls_bin = vim.fn.stdpath("data") .. "/mason/bin/jdtls"

			local root_markers = { ".gradle", "gradlew", ".git", "mvnw", "pom.xml" }
			local root_dir = jdtls.setup.find_root(root_markers)
			local home = os.getenv("HOME")
			local project_name = vim.fn.fnamemodify(root_dir, ":p:h:t")
			local workspace_dir = home .. "/.cache/jdtls/workspace/" .. project_name

			vim.api.nvim_create_autocmd("FileType", {
				group = vim.api.nvim_create_augroup("lsp-java-group", {}),
				pattern = "java",
				callback = function(e)
					vim.opt.tabstop = 2
					vim.opt.softtabstop = 2
					vim.opt.shiftwidth = 2
					vim.opt.expandtab = true

					jdtls.start_or_attach({
						capabilities = capabilities,

						cmd = {
							jdtls_bin,
							"-data",
							workspace_dir,
						},

						root_dir = vim.fs.dirname(vim.fs.find(root_markers, { upward = true })[1]),
						-- root_dir = vim.fs.root(0, { ".git", "mvnw", "gradlew" }),

						on_attach = function(client, bufnr)
							jdtls.setup.add_commands() -- important to ensure you can update configs when build is updated
							-- if you setup DAP according to https://github.com/mfussenegger/nvim-jdtls#nvim-dap-configuration you can uncomment below
							-- jdtls.setup_dap({ hotcodereplace = "auto" })
							-- jdtls.dap.setup_dap_main_class_configs()

							-- you may want to also run your generic on_attach() function used by your LSP config
						end,

						settings = {
							java = {
								sources = {
									organizeImports = {
										starThreshold = 9999,
										staticStarThreshold = 9999,
									},
								},
							},
						},

						init_options = {
							bundles = {},
						},
					})
				end,
			})
		end,
	},
}
