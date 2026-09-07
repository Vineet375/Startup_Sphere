import os

file_path = 'templates/dashboard/_sidebar.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_sidebar = """<div class="sidebar d-none d-lg-block px-3" style="width: 250px; flex-shrink: 0;">
    <div class="nav flex-column mb-auto">"""

new_sidebar = """<div class="offcanvas-lg offcanvas-start sidebar border-end" tabindex="-1" id="sidebarMenu" aria-labelledby="sidebarMenuLabel" style="width: 250px; flex-shrink: 0; background-color: var(--bg-surface);">
    <div class="offcanvas-header d-lg-none border-bottom">
        <h5 class="offcanvas-title" id="sidebarMenuLabel">Menu</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" data-bs-target="#sidebarMenu" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body d-flex flex-column p-3 pt-lg-3 overflow-y-auto">
        <div class="nav flex-column mb-auto w-100">"""

if old_sidebar in content:
    content = content.replace(old_sidebar, new_sidebar)

# Fix the closing div for offcanvas-body
content = content + "\n    </div>"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
