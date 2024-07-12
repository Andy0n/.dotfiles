return {
	{
		"zbirenbaum/copilot.lua",
		name = "copilot",
		cmd = "Copilot",
		event = "InsertEnter",
		config = function()
			require("copilot").setup({
				-- suggestion = {
				-- 	enabled = true,
				-- 	auto_trigger = true,
				-- 	debounce = 75,
				-- 	keymap = {
				-- 		accept = "<M-CR>",
				-- 		accept_word = false,
				-- 		accept_line = false,
				-- 		next = "<M-Tab>",
				-- 		prev = "<M-S-Tab>",
				-- 		dismiss = "<C-]>",
				-- 	},
				-- },
				suggestion = { enabled = false },
				panel = { enabled = false },
			})
		end,
	},
	{
		"zbirenbaum/copilot-cmp",

		after = "copilot",

		config = function()
			require("copilot_cmp").setup()
		end,
	},
	{
		"CopilotC-Nvim/CopilotChat.nvim",
		branch = "canary",
		dependencies = {
			"copilot", -- or github/copilot.vim
			"plenary", -- for curl, log wrapper
		},
		config = function()
			local chat = require("CopilotChat")
            chat.setup({
                debug = true
            })
			vim.keymap.set({ "n", "v" }, "<leader>cc", chat.toggle, {})
		end,
		-- See Commands section for default commands if you want to lazy load on them
	},
}
