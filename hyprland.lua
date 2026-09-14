-- Arasaka: dark red border, blurred translucent surfaces.
local active_border_color = { colors = { "rgba(b80a0acc)", "rgba(3a0508cc)" }, angle = 45 }
local inactive_border_color = "rgba(1e1e2299)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    blur = {
      enabled = true,
      size = 6,
      passes = 3,
      noise = 0.015,
      contrast = 1.0,
      brightness = 0.9,
      vibrancy = 0.1,
      popups = true,
    },
  },
})

-- Blur behind the translucent shell surfaces (bar, menus, notifications).
hl.layer_rule({
  match = { namespace = "^(omarchy-bar|omarchy-menu|omarchy-image-selector|omarchy-emojis|omarchy-clipboard|omarchy-keyboard-panel|omarchy-notifications|omarchy-osd|omarchy-reminders|omarchy-network-qr)$" },
  blur = true,
  ignore_alpha = 0.3,
})

-- Let the wallpaper show through windows, more so when unfocused.
o.window({ tag = "default-opacity" }, { opacity = "0.94 0.86" })
o.window({ tag = "terminal" }, { opacity = "0.88 0.80" })
