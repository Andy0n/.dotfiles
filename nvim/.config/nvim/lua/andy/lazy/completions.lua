return {
	{
		"saghen/blink.cmp",
		dependencies = {
			"rafamadriz/friendly-snippets",
			"giuxtaposition/blink-cmp-copilot",
			"moyiz/blink-emoji.nvim",
			"Kaiser-Yang/blink-cmp-avante",
			-- TODO: luasnip
		},
		version = "1.*",
		---@module 'blink.cmp'
		---@type blink.cmp.Config
		opts = {
			keymap = { preset = "default" },

			appearance = {
				nerd_font_variant = "mono",
			},

			completion = {
				-- ghost_text = { enabled = true },
				documentation = { auto_show = true },
			},

			signature = {
				enabled = true,
			},

			-- Default list of enabled providers defined so that you can extend it
			-- elsewhere in your config, without redefining it, due to `opts_extend`
			sources = {
				default = { "avante", "copilot", "lsp", "path", "snippets", "buffer", "emoji" }, -- cmdline and term are nightly :/
				providers = {
					copilot = {
						module = "blink-cmp-copilot",
						name = "copilot",
						score_offset = 100,
						async = true,
					},
					emoji = {
						module = "blink-emoji",
						name = "emoji",
						score_offset = 15, -- Tune by preference
						opts = { insert = true }, -- Insert emoji (default) or complete its name
					},
					avante = {
						module = "blink-cmp-avante",
						name = "avante",
						opts = {},
					},
					dadbod = { name = "Dadbod", module = "vim_dadbod_completion.blink" },
				},
				per_filetype = {
					sql = { "snippets", "dadbod", "buffer" },
				},
			},
		},
		opts_extend = { "sources.default" },
	},
}
