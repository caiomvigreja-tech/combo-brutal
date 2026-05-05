import re

with open("index.html", "r") as f:
    content = f.read()

# Replace CSS variables
content = content.replace("--red:", "--brand:")
content = content.replace("--red-dark:", "--brand-dark:")
content = content.replace("--red-glow:", "--brand-glow:")
content = content.replace("--border-red:", "--border-brand:")

content = content.replace("var(--red)", "var(--brand)")
content = content.replace("var(--red-dark)", "var(--brand-dark)")
content = content.replace("var(--red-glow)", "var(--brand-glow)")
content = content.replace("var(--border-red)", "var(--border-brand)")
content = content.replace("line-red", "line-brand")

# Update :root with light theme variables and brand color
old_root = """    :root {
      --brand: #E02020;
      --brand-dark: #B01818;
      --brand-glow: rgba(224,32,32,0.18);
      --bg: #0a0a0a;
      --bg2: #111111;
      --bg3: #181818;
      --border: rgba(255,255,255,0.07);
      --border-brand: rgba(224,32,32,0.3);
      --text: #f0f0f0;
      --muted: #888;
      --muted2: #555;
      --font-display: 'Bebas Neue', sans-serif;
      --font-body: 'DM Sans', sans-serif;
    }"""

new_root = """    :root {
      --brand: #ff6b00;
      --brand-dark: #e66000;
      --brand-glow: rgba(255, 107, 0, 0.18);
      --green: #00b85c;
      --green-dark: #00a352;
      --bg: #0a0a0a;
      --bg2: #111111;
      --bg3: #181818;
      --border: rgba(255, 255, 255, 0.07);
      --border-brand: rgba(255, 107, 0, 0.3);
      --text: #f0f0f0;
      --muted: #888;
      --muted2: #555;
      --font-display: 'Bebas Neue', sans-serif;
      --font-body: 'DM Sans', sans-serif;
    }

    .theme-light {
      --bg: #ffffff;
      --bg2: #f8f9fa;
      --bg3: #f1f3f5;
      --border: rgba(0, 0, 0, 0.08);
      --border-brand: rgba(255, 107, 0, 0.25);
      --text: #1a1a1a;
      --muted: #555555;
      --muted2: #888888;
    }"""

content = content.replace(old_root, new_root)

# Update hardcoded colors
content = content.replace("color: #ccc;", "color: var(--muted);")
content = content.replace("color: #d5d5d5;", "color: var(--muted);")
content = content.replace("background: rgba(0,0,0,0.22);", "background: var(--bg);")
content = content.replace("background: #080808;", "background: var(--bg3);")

# Wait, for text that should be strictly white in dark mode but dynamic in light mode,
# like .valor-price .por which had color: #fff;
content = content.replace("color: #fff;", "color: var(--text);")
# But in .oferta it should be #fff if .oferta is always dark.
# Let's see... .oferta does NOT get theme-light, so it stays dark.
# So --text in .oferta will be #f0f0f0, which is fine.

# Let's change the CTA button to use green
content = content.replace("background: var(--brand);", "background: var(--brand);") # wait
content = re.sub(r'\.cta-btn\s*\{\s*display:\s*inline-block;\s*background:\s*var\(--brand\);', 
                 '.cta-btn {\n      display: inline-block;\n      background: var(--green);', content)
content = re.sub(r'\.cta-btn:hover\s*\{\s*background:\s*var\(--brand-dark\);', 
                 '.cta-btn:hover { background: var(--green-dark);', content)

# Sections to get theme-light
content = content.replace('<section class="cursos">', '<section class="cursos theme-light">')
content = content.replace('<section class="bonus">', '<section class="bonus theme-light">')
content = content.replace('<section class="valor">', '<section class="valor theme-light">')

# Add theme-light class to dor (we already removed inline style)
content = content.replace('<section class="dor theme-light">', '<section class="dor theme-light" style="padding-top: 72px;">')
content = content.replace('<section class="dor">', '<section class="dor theme-light">')

with open("index.html", "w") as f:
    f.write(content)

