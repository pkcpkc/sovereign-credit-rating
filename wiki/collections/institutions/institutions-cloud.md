---
type: "Overview"
title: "Institutions Relation Cloud"
description: "Interactive graph linking institutions cards sharing common tags."
timestamp: "2026-07-05T16:25:57Z"
hide:
  - navigation
  - toc
---
# Institutions Relation Cloud

<div class="graph-search-container"><div class="search-input-wrapper"><input type="text" id="graph-search" placeholder="Search institutions by name or tag..." autocomplete="off"><button id="search-clear" class="search-clear-btn" type="button">&times;</button></div><div class="filter-dropdown-wrapper"><label for="shared-tag-threshold">Min. shared tags:</label><select id="shared-tag-threshold" class="filter-dropdown-select"><option value="1">At least 1</option><option value="2" selected>At least 2</option><option value="3">At least 3</option><option value="4">At least 4</option></select></div></div>

<div id="cy-fullscreen" data-collection="institutions"></div>

<p class="graph-hint">💡 Note: Adjust the dropdown above to filter connections by the number of shared tags.</p>
