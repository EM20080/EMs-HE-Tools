Havok -autodraw "source" "output"
for %%f in (output\*.hkx.xml) do (AssetCcUnleashed.exe --rules4001 "%%f" "%%~dpnf" 2>nul & del "%%f")
