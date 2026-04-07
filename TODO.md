# End-to-end validation

- [ ] Export a production line from Helmod in-game (copy to clipboard or download to file)
- [ ] Run `helmod-generator --clipboard --raw` to verify the Helmod export decodes correctly (if `slpp` chokes on the Lua format, we need to write a custom parser)
- [ ] Run `helmod-generator --clipboard --verbose` to check the parsed model (correct buildings, recipes, modules, counts) and get a blueprint string
- [ ] Import the blueprint string in Factorio and verify buildings appear with correct recipes and modules assigned
