return {
	{
		"zbirenbaum/copilot.lua",
		name = "copilot",
		cmd = "Copilot",
		event = "InsertEnter",
		config = function()
			require("copilot").setup({
				suggestion = { enabled = false },
				panel = { enabled = false },
			})
		end,
	},
	{
		"CopilotC-Nvim/CopilotChat.nvim",
		dependencies = {
			"copilot", -- or github/copilot.vim
			"plenary", -- for curl, log wrapper
		},
	       build = "make tiktoken",
		config = function()
			local chat = require("CopilotChat")
	           chat.setup({
	               model = "o1",
	               debug = false
	           })
			vim.keymap.set({ "n", "v" }, "<leader>cc", chat.toggle, {})
		end,
		-- See Commands section for default commands if you want to lazy load on them
	},
	{
		"yetone/avante.nvim",
		event = "VeryLazy",
		version = false, -- Never set this value to "*"! Never!
		opts = {
			provider = "copilot",
			copilot = {
				model = "claude-3.7-sonnet-thought",
				-- model = "claude-3.7-sonnet",
				-- model = "gpt-4o-2024-11-20",
				-- model = "o1",
			},
			mappings = {
				-- ask = "<leader>cc",
			},
            behavior = {
                -- auto_suggestions= true,
            },
		},
		-- if you want to build from source then do `make BUILD_FROM_SOURCE=true`
		build = "make",
		-- build = "powershell -ExecutionPolicy Bypass -File Build.ps1 -BuildFromSource false" -- for windows
		dependencies = {
			"nvim-treesitter/nvim-treesitter",
			"folke/snacks.nvim",
			"plenary",
			"MunifTanjim/nui.nvim",
			--- The below dependencies are optional,
			"telescope", -- for file_selector provider telescope
			"copilot", -- for providers='copilot'
			{
				-- support for image pasting
				"HakonHarnes/img-clip.nvim",
				event = "VeryLazy",
				opts = {
					-- recommended settings
					default = {
						embed_image_as_base64 = false,
						prompt_for_file_name = false,
						drag_and_drop = {
							insert_mode = true,
						},
						-- required for Windows users
						use_absolute_path = true,
					},
				},
			},
			{
				-- Make sure to set this up properly if you have lazy=true
				"MeanderingProgrammer/render-markdown.nvim",
				opts = {
					file_types = { "markdown", "Avante" },
				},
				ft = { "markdown", "Avante" },
			},
		},
	},
}
